#!-*coding:utf-8 -*-
# FileName:

"""
log结构化。
使用时：
1. 针对不同项目，更改 LogSLS.__project
2. 若需要存储，改变 LOG_SERVER 为实际的log服务地址（配套服务：https://github.com/fevolq/LogServer）
3. 不包含logging初始化，若需要可参考__main__中的定义
"""
import datetime
import logging
import os
import time
from typing import Union

import pytz
import requests

from utils import colors, thread_func

log_level = {
    'debug': {'level': logging.DEBUG},
    'info': {'level': logging.INFO},
    'warning': {'level': logging.WARNING},
    'error': {'level': logging.ERROR},
}
LOG_SERVER = ''
TZ = 'Asia/Shanghai'


class LogSLS:
    __project = 'Util'  # 当前项目。每个项目应该唯一，数据会存储至对应的集合中。
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return self.__project

    def __sls(self, __module__: str, level: str, __content__: Union[str, int], **kwargs):
        """
        sls日志服务的所需数据
        :param __module__: 所属模块
        :param level: 日志等级
        :param __content__: 主体内容
        :param kwargs:
        :return:
        """
        # 元数据
        metadata = {
            'time': datetime.datetime.strftime(datetime.datetime.now(pytz.timezone(TZ)), '%Y-%m-%d %H:%M:%S'),
            'timestamp': time.time(),
            'pid': os.getpid(),  # 当前进程id
            'ppid': os.getppid(),  # 父进程id
        }

        # 日志主体内容，及其他自定义字段内容
        log_content = {
            '__content__': __content__,
        }
        log_content.update(kwargs)

        doc = {
            'project': LogSLS.__project,  # 当前项目
            'level': level,  # 日志等级
            'metadata': metadata,  # 元数据
            'module': __module__,  # 来源模块
            'doc': log_content,  # 日志内容
        }
        self.__save(doc)  # 日志存储

    @classmethod
    def __save(cls, doc: dict):
        def request():
            if LOG_SERVER:
                requests.post(f'{LOG_SERVER}/log/submit', json={'project': cls.__project, 'doc': doc})

        thread_func.submit(request, use_pool=False)

    @classmethod
    def __logging(cls, level, __content__: str, **kwargs):
        """日志运行展示"""
        level = log_level[level]['level']

        kwargs_info = [__content__]
        for k, v in kwargs.items():
            if not isinstance(v, (str, int)):
                v = str(v)
            kwargs_info.append(f'{colors.green(k)}{colors.grey(": ")}{colors.cyan(v)}')

        logging.log(level, f'{colors.white(";")} '.join(kwargs_info))

    def info(self, __module__: str, __content__, **kwargs):
        level = 'info'
        self.__logging(level, f'[{__module__}] {__content__}', **kwargs)
        return self.__sls(__module__, level, __content__, **kwargs)

    def warning(self, __module__: str, __content__, **kwargs):
        level = 'warning'
        self.__logging(level, __content__, **kwargs)
        return self.__sls(__module__, level, __content__, **kwargs)

    def debug(self, __module__: str, __content__, **kwargs):
        level = 'debug'
        self.__logging(level, __content__, **kwargs)
        return self.__sls(__module__, level, __content__, **kwargs)

    def error(self, __module__: str, __content__, **kwargs):
        level = 'error'
        self.__logging(level, __content__, **kwargs)
        return self.__sls(__module__, level, __content__, **kwargs)

    def exception(self, __module__: str, __content__, **kwargs):
        """错误堆栈"""
        level = 'exception'
        logging.exception(__content__)
        for k, v in kwargs.items():
            logging.exception(logging.INFO, f'{k} = {v}')
        return self.__sls(__module__, level, __content__, **kwargs)


instance = LogSLS()


def info(__module__: str, __content__: str, **kwargs):
    """

    :param __module__: 所属模块
    :param __content__: 主体内容
    :param kwargs:
    :return
    """
    return instance.info(__module__, __content__, **kwargs)


def debug(__module__: str, __content__: str, **kwargs):
    return instance.debug(__module__, __content__, **kwargs)


def warning(__module__: str, __content__: str, **kwargs):
    return instance.warning(__module__, __content__, **kwargs)


def error(__module__: str, __content__: str, **kwargs):
    return instance.error(__module__, __content__, **kwargs)


def exception(__module__: str, __content__: str, **kwargs):
    return instance.exception(__module__, __content__, **kwargs)


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
