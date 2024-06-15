#!-*coding:utf-8 -*-
# python3.7
# CreateTime: 2022/11/28 18:55
# FileName:

"""
异步线程，可能造成数据丢失。
"""
import copy
import logging
import os
import time
from typing import Union
import threading

from utils import util, thread_func, colors
# from dao import mongoDB, esDB


LOG_LEVEL = {
    'debug': {'level': logging.DEBUG},
    'info': {'level': logging.INFO},
    'warning': {'level': logging.WARNING},
    'error': {'level': logging.ERROR},
}


class LogSLS:
    __project = 'template'  # 当前项目。每个项目应该唯一，数据会存储至对应的集合中。
    __lock = threading.RLock()
    __instance = None

    def __new__(cls, *args, **kwargs):
        # 构造单例
        if hasattr(cls, '__instance'):
            return cls.__instance

        # 线程锁
        with cls.__lock:
            if not hasattr(cls, 'instance'):
                cls.__instance = super(LogSLS, cls).__new__(cls)
            return cls.__instance

    def __init__(self):
        ...

    def __repr__(self):
        return LogSLS.__project

    @staticmethod
    def save_mongo(data):
        # mongoDB.execute(LogSLS.__project, 'insert_one', data, db_name='log_sls', raise_error=False)
        ...

    @staticmethod
    def save_es(data):
        # esDB.execute(LogSLS.__project.lower(), 'index', document=data, raise_error=False)
        ...

    def save(self, data):
        thread_func.submit(self.save_mongo, copy.deepcopy(data), use_pool=False)
        thread_func.submit(self.save_es, copy.deepcopy(data), use_pool=False)
        ...

    def __sls(self, mod: str, level: str, content: Union[str, int], **kwargs):
        """
        sls日志服务的所需数据
        :param mod: 所属模块
        :param level: 日志等级
        :param content: 主体内容
        :param kwargs:
        :return:
        """
        try:
            now = util.now_time()

            # 元数据
            metadata = {
                'time': now,
                'timestamp': time.time(),
                'pid': os.getpid(),  # 当前进程id
                'ppid': os.getppid(),  # 父进程id
            }

            # 日志主体内容，及其他自定义字段内容
            log_content = {
                'content': content,
            }
            log_content.update(kwargs)

            doc = {
                'project': LogSLS.__project,  # 当前项目
                'level': level,  # 日志等级
                'metadata': metadata,  # 元数据
                'module': mod,  # 来源模块
                'content': log_content,  # 日志内容
            }
            # self.save(doc)    # 日志远程存储

        except Exception as e:
            logging.exception(e)

    @staticmethod
    def __logging(level, content: str, **kwargs):
        """日志运行展示"""
        level = LOG_LEVEL[level]['level']
        kwargs_info = []
        for k, v in kwargs.items():
            kwargs_info.append(f'{colors.green(k)}{colors.grey(": ")}{colors.cyan(v)}')
        kwargs_info.insert(0, content)

        logging.log(level, f'{colors.white(";")} '.join(kwargs_info))

    def info(self, module: str, content, **kwargs):
        level = 'info'
        self.__logging(level, f'[{module}] {content}', **kwargs)
        return self.__sls(module, level, content, **kwargs)

    def warning(self, module: str, content, **kwargs):
        level = 'warning'
        self.__logging(level, f'[{module}] {content}', **kwargs)
        return self.__sls(module, level, content, **kwargs)

    def debug(self, module: str, content, **kwargs):
        level = 'debug'
        self.__logging(level, f'[{module}] {content}', **kwargs)
        return self.__sls(module, level, content, **kwargs)

    def error(self, module: str, content, **kwargs):
        level = 'error'
        self.__logging(level, f'[{module}] {content}', **kwargs)
        return self.__sls(module, level, content, **kwargs)

    def exception(self, module: str, content, **kwargs):
        """错误堆栈"""
        level = 'exception'
        logging.exception(content)
        for k, v in kwargs.items():
            logging.exception(logging.INFO, f'{k} = {v}')
        return self.__sls(module, level, content, **kwargs)


instance = LogSLS()


def info(mod: str, content: str, **kwargs):
    """

    :param mod: 所属模块
    :param content: 主体内容
    :param kwargs:
    :return
    """
    return instance.info(mod, content, **kwargs)


def debug(mod: str, content: str, **kwargs):
    return instance.debug(mod, content, **kwargs)


def warning(mod: str, content: str, **kwargs):
    return instance.warning(mod, content, **kwargs)


def error(mod: str, content: str, **kwargs):
    return instance.error(mod, content, **kwargs)


def exception(mod: str, content: str, **kwargs):
    return instance.exception(mod, content, **kwargs)


if __name__ == '__main__':
    import log_init

    log_init.init_logging('')


    def execute():
        print('start')

        info('test', 'content_info', key='key_info', value='value_info')
        debug('test', 'content_debug', key='key_debug', value='value_debug')
        warning('demo', 'content_warning', key='key_warning', value='value_warning')
        error('demo', 'content_error', key='key_error', value='value_error')

        print('end')


    execute()

    print('...')
