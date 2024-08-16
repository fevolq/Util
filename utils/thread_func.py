#!-*- coding:utf-8 -*-
# FileName: 异步线程任务

import logging
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import atexit
from typing import Union


class ThreadPool:
    """
    线程池。任务交给池中的线程执行
    """

    _instances = []

    def __init__(self, name='default', *, maxsize: int = 0):
        ThreadPool._instances.append(self)
        self.name = name
        maxsize = max(maxsize, 0) or None
        self._executor = ThreadPoolExecutor(maxsize)

    def submit(self, callback, *args, **kwargs):
        try:
            self._executor.submit(callback, *args, **kwargs)
        except RuntimeError as e:
            logging.error(f'Error submit {self.name} task: {e}')
            raise

    def shutdown(self, wait=True):
        try:
            self._executor.shutdown(wait=wait)
        except Exception as e:
            logging.error(f'Error shutdown {self.name}: {e}')
            raise


class ThreadQueue(threading.Thread):
    """
    单线程。主线程外另起一个线程，任务放到该线程的Queue中，顺序执行。
    注意：当某一个示例的队列满了后，若仍继续提交任务，则会阻塞主线程
    """

    _instances = []

    class StopFlag:
        def __init__(self): ...

    def __init__(self, name='default', *, maxsize: int = 0):
        super().__init__(name=name)
        ThreadQueue._instances.append(self)
        maxsize = max(maxsize, 0)
        self.name = name
        self._queue = Queue(maxsize=maxsize)
        self._stop_flag = self.StopFlag()  # 结束标志
        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                data = self._queue.get(timeout=1)
                if data is self._stop_flag:
                    self._queue.task_done()
                    break
                callback = data['callback']
                args = data['args']
                kwargs = data['kwargs']
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logging.error(f'Error {callback.__name__}: {e}')
                finally:
                    self._queue.task_done()
            except queue.Empty:
                continue

    def submit(self, callback, *args, **kwargs):
        data = {
            'callback': callback,
            'args': args,
            'kwargs': kwargs,
        }
        try:
            self._queue.put(data)
        except Exception as e:
            logging.exception(e)
            raise

    def shutdown(self, wait=True):
        if self.ident is not None:
            self._queue.put(self._stop_flag)
            if wait:
                self._queue.join()
                self.join()


def submit(instance: Union[ThreadPool, ThreadQueue], callback, *args, **kwargs):
    """
    提交任务
    :param instance:
    :param callback:
    :param args:
    :param kwargs:
    :return:
    """
    instance.submit(callback, *args, **kwargs)


@atexit.register
def shutdown():
    instances = [*ThreadPool._instances, *ThreadQueue._instances]
    for instance in instances:
        instance.shutdown(wait=True)
