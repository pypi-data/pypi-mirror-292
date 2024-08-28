from __future__ import annotations

import asyncio
import base64
import copy
import hashlib
import json
import mimetypes
import os
import pkgutil
import secrets
import shutil
import tempfile
import warnings
from concurrent.futures import CancelledError
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Literal, Optional, TypedDict

import fsspec.asyn
import httpx
import huggingface_hub
from huggingface_hub import SpaceStage
from websockets.legacy.protocol import WebSocketCommonProtocol

class TooManyRequestsError(Exception):
    """Raised when the API returns a 429 status code."""

    pass


class QueueError(Exception):
    """Raised when the queue is full or there is an issue adding a job to the queue."""

    pass


class InvalidAPIEndpointError(Exception):
    """Raised when the API endpoint is invalid."""

    pass


class SpaceDuplicationError(Exception):
    """Raised when something goes wrong with a Space Duplication."""

    pass


class ServerMessage(str, Enum):
    send_hash = "send_hash"
    queue_full = "queue_full"
    estimation = "estimation"
    send_data = "send_data"
    process_starts = "process_starts"
    process_generating = "process_generating"
    process_completed = "process_completed"
    log = "log"
    progress = "progress"
    heartbeat = "heartbeat"
    server_stopped = "server_stopped"
    unexpected_error = "unexpected_error"


class Status(Enum):
    """Status codes presented to client users."""

    STARTING = "STARTING"
    JOINING_QUEUE = "JOINING_QUEUE"
    QUEUE_FULL = "QUEUE_FULL"
    IN_QUEUE = "IN_QUEUE"
    SENDING_DATA = "SENDING_DATA"
    PROCESSING = "PROCESSING"
    ITERATING = "ITERATING"
    PROGRESS = "PROGRESS"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"
    LOG = "LOG"

    @staticmethod
    def ordering(status: Status) -> int:
        """Order of messages. Helpful for testing."""
        order = [
            Status.STARTING,
            Status.JOINING_QUEUE,
            Status.QUEUE_FULL,
            Status.IN_QUEUE,
            Status.SENDING_DATA,
            Status.PROCESSING,
            Status.PROGRESS,
            Status.ITERATING,
            Status.FINISHED,
            Status.CANCELLED,
        ]
        return order.index(status)

    def __lt__(self, other: Status):
        return self.ordering(self) < self.ordering(other)

    @staticmethod
    def msg_to_status(msg: str) -> Status:
        """Map the raw message from the backend to the status code presented to users."""
        return {
            ServerMessage.send_hash: Status.JOINING_QUEUE,
            ServerMessage.queue_full: Status.QUEUE_FULL,
            ServerMessage.estimation: Status.IN_QUEUE,
            ServerMessage.send_data: Status.SENDING_DATA,
            ServerMessage.process_starts: Status.PROCESSING,
            ServerMessage.process_generating: Status.ITERATING,
            ServerMessage.process_completed: Status.FINISHED,
            ServerMessage.progress: Status.PROGRESS,
            ServerMessage.log: Status.LOG,
            ServerMessage.server_stopped: Status.FINISHED,
        }[msg]  # type: ignore


@dataclass
class ProgressUnit:
    index: Optional[int]
    length: Optional[int]
    unit: Optional[str]
    progress: Optional[float]
    desc: Optional[str]

    @classmethod
    def from_msg(cls, data: list[dict]) -> list[ProgressUnit]:
        return [
            cls(
                index=d.get("index"),
                length=d.get("length"),
                unit=d.get("unit"),
                progress=d.get("progress"),
                desc=d.get("desc"),
            )
            for d in data
        ]


@dataclass
class StatusUpdate:
    """Update message sent from the worker thread to the Job on the main thread."""

    code: Status
    rank: int | None
    queue_size: int | None
    eta: float | None
    success: bool | None
    time: datetime | None
    progress_data: list[ProgressUnit] | None
    log: tuple[str, str] | None = None


def create_initial_status_update():
    return StatusUpdate(
        code=Status.STARTING,
        rank=None,
        queue_size=None,
        eta=None,
        success=None,
        time=datetime.now(),
        progress_data=None,
    )


@dataclass
class JobStatus:
    """The job status.

    Keeps track of the latest status update and intermediate outputs (not yet implements).
    """

    latest_status: StatusUpdate = field(
        default_factory=create_initial_status_update)
    outputs: list[Any] = field(default_factory=list)


@dataclass
class Communicator:
    """Helper class to help communicate between the worker thread and main thread."""

    lock: Lock
    job: JobStatus
    prediction_processor: Callable[..., tuple]
    reset_url: str
    should_cancel: bool = False
    event_id: str | None = None
