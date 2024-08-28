#!/usr/bin/env python
# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
import threading
import time
from .queue_client import QueueClient

class AsyncResult:
    def __init__(self):
        self._result = None
        self._callbacks = []
        self._is_finished = threading.Event()

    def set_result(self, result):
        self._result = result
        self._is_finished.set()
        for callback in self._callbacks:
            callback(result)

    def add_done_callback(self, callback):
        if self._is_finished.is_set():
            callback(self._result)
        else:
            self._callbacks.append(callback)

    def wait(self, timeout=None):
        self._is_finished.wait(timeout)
        return self._result

class Client:
    def __init__(self, endpoint, token, input_name):
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
        self.executor = ThreadPoolExecutor()

    def async_predict(self, data, callback=None):
        index, request_id = self.input_queue.put(data)
        async_result = AsyncResult()
        if callback:
            async_result.add_done_callback(callback)

        # The asynchronous task that will be submitted to the executor
        def task():
            result = None
            while result is None:
                dfs = self.sink_queue.get(request_id=request_id, timeout='0s', auto_delete=False)
                if len(dfs) > 0:
                    result = str(dfs[0].data)
                    self.sink_queue.delete(dfs[0].index)
                else:
                    time.sleep(1)  # Polling interval
            async_result.set_result(result)

        self.executor.submit(task)
        return async_result
