#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import concurrent.futures
import json
import os
import re
import secrets
import tempfile
import threading
import time
import urllib.parse
import uuid
import warnings
from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Callable
from .queue_client import QueueClient
from .utils import (
    Communicator,
    JobStatus,
    Message,
    QueueError,
    ServerMessage,
    Status,
    StatusUpdate,
)


class Client:
    def __init__(self, endpoint, token, input_name, max_workers: int = 40):
        self.endpoint = endpoint
        self.token = token
        self.input_name = input_name
        self.sink_name = input_name + '/sink'
        self.input_queue = QueueClient(endpoint, input_name)
        self.sink_queue = QueueClient(endpoint, self.sink_name)
        self.input_queue.set_token(token)
        self.input_queue.init()
        self.sink_queue.set_token(token)
        self.sink_queue.init()
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers)
        
    def make_predict(self, helper: Communicator | None = None):
        def _predict(data, tags, req_path):
            index, request_id = self.input_queue.put(data, tags=tags)
            # print(f'input index: {index}, data: {data}')
            result = None
            while result is None:
                try:
                    dfs = self.sink_queue.get(request_id=request_id, timeout='5s', auto_delete=False)
                    if len(dfs) > 0:
                        result = str(dfs[0].data)
                        self.sink_queue.delete(dfs[0].index)
                        # print(f'sink index: {dfs[0].index}, data: {dfs[0].data}')
                        return result
                except Exception as e:
                    print("err:", e)
                    continue

        return _predict

    def submit(self, data, tags: dict = {}, req_path = '', result_callbacks=None):
        predict_fn = self.make_predict()
        future = self.executor.submit(predict_fn, data, tags, req_path)

        job = Job(future, communicator=None)
        if result_callbacks:
            if isinstance(result_callbacks, Callable):
                result_callbacks = [result_callbacks]

            def create_fn(callback) -> Callable:
                def fn(future):
                    if isinstance(future.result(), tuple):
                        callback(*future.result())
                    else:
                        callback(future.result())

                return fn

            for callback in result_callbacks:
                job.add_done_callback(create_fn(callback))

        return job


class Job(Future):

    def __init__(
        self,
        future: Future,
        communicator: Communicator | None = None
    ):
        self.future = future
        self.communicator = communicator

    def result(self, timeout: float | None = None) -> Any:
        return super().result(timeout=timeout)

    def status(self) -> StatusUpdate:
        time = datetime.now()
        cancelled = False
        if self.communicator:
            with self.communicator.lock:
                cancelled = self.communicator.should_cancel
        if cancelled:
            return StatusUpdate(
                code=Status.CANCELLED,
                rank=0,
                queue_size=None,
                success=False,
                time=time,
                eta=None,
                progress_data=None,
            )
        if self.done():
            if not self.future._exception:  # type: ignore
                return StatusUpdate(
                    code=Status.FINISHED,
                    rank=0,
                    queue_size=None,
                    success=True,
                    time=time,
                    eta=None,
                    progress_data=None,
                )
            else:
                return StatusUpdate(
                    code=Status.FINISHED,
                    rank=0,
                    queue_size=None,
                    success=False,
                    time=time,
                    eta=None,
                    progress_data=None,
                )
        elif not self.communicator:
            return StatusUpdate(
                code=Status.PROCESSING,
                rank=0,
                queue_size=None,
                success=None,
                time=time,
                eta=None,
                progress_data=None,
            )
        else:
            with self.communicator.lock:
                return self.communicator.job.latest_status

    def cancel(self) -> bool:
        if self.communicator:
            with self.communicator.lock:
                self.communicator.should_cancel = True
                return True
        return self.future.cancel()
