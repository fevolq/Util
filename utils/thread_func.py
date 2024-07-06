#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2022/12/21 18:03
# FileName: 异步线程

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue


class ThreadPool:
    """
    线程池。池中每增加一个任务，即增加一个线程，各自执行任务。
    """

    __lock = threading.RLock()
    __instance = None
    __pools = 100

    def __new__(cls, *args, **kwargs):
        # 构造单例
        if cls.__instance:
            return cls.__instance

        # 线程锁
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super().__new__(cls)
            return cls.__instance

    def __init__(self):
        self._executor = ThreadPoolExecutor(ThreadPool.__pools)

    def submit(self, func, *args, **kwargs):
        self._executor.submit(func, *args, **kwargs)
        # try:
        #     self._executor.submit(func, *args, **kwargs)
        # except:
        #     self._executor.shutdown(False)


class ThreadQueue(threading.Thread):
    """
    单线程。主线程外另起一个线程，任务放到该线程的Queue中，顺序执行。
    """

    __lock = threading.RLock()
    __instance = None
    _queue = Queue()
    is_start_thread = False

    def __new__(cls, *args, **kwargs):
        # 构造单例
        if cls.__instance:
            return cls.__instance

        # 线程锁
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super().__new__(cls)
            return cls.__instance

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            data = self._queue.get()
            func = data['func']
            args = data['args']
            kwargs = data['kwargs']
            func(*args, **kwargs)
            del data

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


def get_pool_instance():
    return ThreadPool()


def get_queue_instance():
    thread_queue = ThreadQueue()
    if not thread_queue.is_start_thread:
        with threading.RLock():
            if not thread_queue.is_start_thread:
                thread_queue.is_start_thread = True
                thread_queue.setDaemon(True)
                thread_queue.start()
    return thread_queue


def submit(func, *args, use_pool: bool = True, **kwargs):
    if use_pool:
        instance = get_pool_instance()
    else:
        instance = get_queue_instance()

    instance.submit(func, *args, **kwargs)
