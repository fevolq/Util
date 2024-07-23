#!-*- coding:utf-8 -*-
# FileName: 异步线程任务

import logging
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import atexit


class ThreadPool:
    """
    线程池。任务交给池中的线程执行
    """

    __lock = threading.RLock()
    __instance = None
    __has_init = False
    __pools = 100

    def __new__(cls, *args, **kwargs):
        # 构造单例
        if cls.__instance is None:
            with cls.__lock:
                if cls.__instance is None:
                    cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if ThreadPool.__has_init:
            return
        ThreadPool.__has_init = True
        self._executor = ThreadPoolExecutor(ThreadPool.__pools)

    def submit(self, func, *args, **kwargs):
        try:
            self._executor.submit(func, *args, **kwargs)
        except RuntimeError as e:
            logging.error(f'Error submit task: {e}')
            raise

    def shutdown(self, wait=True):
        try:
            self._executor.shutdown(wait=wait)
        except Exception as e:
            logging.error(f'Error during shutdown: {e}')
            raise


class ThreadQueue(threading.Thread):
    """
    单线程。主线程外另起一个线程，任务放到该线程的Queue中，顺序执行。
    """

    __lock = threading.RLock()
    __instance = None
    __has_init = False
    _queue = Queue(maxsize=100)

    class StopFlag:
        def __init__(self): ...

    def __new__(cls, *args, **kwargs):
        # 构造单例
        if cls.__instance is None:
            with cls.__lock:
                if cls.__instance is None:
                    cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if ThreadQueue.__has_init:
            return
        ThreadPool.__has_init = True
        super().__init__(name='ThreadQueue')
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
                func = data['func']
                args = data['args']
                kwargs = data['kwargs']
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logging.error(f'Error {func.__name__}: {e}')
                finally:
                    self._queue.task_done()
            except queue.Empty:
                continue

    def submit(self, func, *args, **kwargs):
        data = {
            'func': func,
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


def get_pool_instance():
    return ThreadPool()


def get_queue_instance():
    return ThreadQueue()


def submit(func, *args, use_pool: bool = True, **kwargs):
    """
    提交任务
    :param func:
    :param args:
    :param use_pool: 是否在线程池使用
    :param kwargs:
    :return:
    """
    if use_pool:
        instance = get_pool_instance()
    else:
        instance = get_queue_instance()

    instance.submit(func, *args, **kwargs)


@atexit.register
def shutdown():
    instances = [get_pool_instance(), get_queue_instance()]
    for instance in instances:
        instance.shutdown(wait=True)
