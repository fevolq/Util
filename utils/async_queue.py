#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/9/24 15:16
# FileName: 基于队列的异步生产消费任务

"""
场景：
有多张图片需要保存（或上传）
生产者：读取图片内容
消费者：存储图片

常规流程：读取图片、存储。循环执行，或多线程执行。时间 =（生产者 + 消费者）*n
分解执行多线程：多线程执行生产者，再执行消费者。时间 =（生产者 * n + 消费者 * n）
异步队列：消费者监听独队列，生产者的结果放入队列，两者的阻塞互不干扰。则理想状态 时间 = 生产者 * n +（最后一个）消费者

优化：若不在乎消费者的结果顺序，则生产者和消费者还可启用多线程来与队列交互。
"""

import logging
import queue
import threading
from typing import List

MAXSIZE = 10


class StopFlag:

    def __init__(self): ...


class AsyncQueue:

    def __init__(self, *, name='', maxsize=MAXSIZE):
        """

        :param name: 任务名称
        :param maxsize: 队列最大值
        """
        self.name = name
        self.q = queue.Queue(maxsize=maxsize)
        self.__producer_thread = None
        self.__consumer_thread = None

        self._result = []  # 结果

    def __repr__(self):
        return self.name

    def get_result(self):
        return self._result

    def add_producer(self, callback, args_list: List):

        # 解析参数
        def get_params(params):
            args = params[0] if any([isinstance(params[0], tuple), isinstance(params[0], list)]) else []
            kwargs = params[-1] if isinstance(params[-1], dict) else {}
            return args, kwargs

        def producer():
            for param in args_list:
                args, kwargs = get_params(param)
                data = callback(*args, **kwargs)
                self.q.put(data)

        self.__producer_thread = threading.Thread(target=producer)

    def add_consumer(self, callback):

        def consumer():
            while True:
                data = self.q.get()
                if isinstance(data, StopFlag):
                    logging.info(f'异步队列：{self.name}——消费者完成')
                    break

                self._result.append(callback(data))
                self.q.task_done()

        self.__consumer_thread = threading.Thread(target=consumer)

    def run(self):
        assert self.__producer_thread, '请注册生产者：add_producer'
        assert self.__consumer_thread, '请注册消费者：add_consumer'

        logging.info(f'异步队列：{self.name}——启动')

        self.__producer_thread.start()
        self.__consumer_thread.start()

        self.__producer_thread.join()  # 等待生产者线程结束
        logging.info(f'异步队列：{self.name}——生产者退出')
        self.q.put(StopFlag())  # 添加队列结束标志
        self.__consumer_thread.join()  # 等待消费者线程结束
        logging.info(f'异步队列：{self.name}——消费者退出')
