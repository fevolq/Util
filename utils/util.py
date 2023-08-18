#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2022/10/19 18:32
# FileName:

import datetime
import functools
import hashlib
import logging
import os
import platform
import random
import time
import traceback
import typing
import uuid
from typing import List, Union, Callable

import pytz


def asia_local_time(fmt="%Y-%m-%d %H:%M:%S", tz="Asia/Shanghai"):
    """
    本地时间
    :param fmt:
    :param tz:
    :return:
    """
    return datetime.datetime.strftime(datetime.datetime.now(pytz.timezone(tz)), fmt)


def time2str(t=None, fmt="%Y-%m-%d %H:%M:%S") -> str:
    """
    时间timestamp转字符串
    :param t: 时间戳
    :param fmt:
    :return:
    """
    return time.strftime(fmt, time.localtime(time.time() if t is None else t))


def str2time(t=None, fmt="%Y-%m-%d %H:%M:%S") -> float:
    """
    字符串转时间戳
    :param t: 时间字符串
    :param fmt:
    :return:
    """
    return time.time() if t is None else time.mktime(time.strptime(t, fmt))


def get_delay_date(date_str: str = None, date_fmt="%Y-%m-%d", delay: int = 0) -> str:
    """
    获取指定日期的几日前或后的日期
    :param date_str: 日期，默认为当前日期。
    :param date_fmt: date_str的格式
    :param delay: 间隔天数。正数为往后，负数为往前。
    :return: %Y-%m-%d
    """
    if date_str is None:
        date_str = str(datetime.datetime.now().date())
    delay_date = datetime.datetime.strptime(date_str, date_fmt) + datetime.timedelta(days=delay)
    return datetime.datetime.strftime(delay_date, "%Y-%m-%d")


def hash_list(dict_list: List[dict], hash_field: str) -> list:
    """
    数据的hash值，用于判断唯一
    :param dict_list: [{'date': xxx}, ...]
    :param hash_field: 'date'
    :return:
    """
    arr = []
    for item in dict_list:
        v = item.get(hash_field, None)
        if not v:
            continue
        m = hashlib.md5()
        m.update(v.lower().encode(encoding='UTF-8'))
        arr.append(m.hexdigest())
    return arr


def md5(s: typing.Union[str, bytes]) -> str:
    """md5"""
    if isinstance(s, str):
        s = s.encode(encoding='UTF-8')
    return hashlib.md5(s).hexdigest()


def hash256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def random_string(length: int, choices: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') -> str:
    """随机字符串"""
    return ''.join(random.choice(choices) for _ in range(length))


def gen_unique_str(key: str = None) -> str:
    key = random_string(3) if key is None else key
    key = f'{time.time()}{uuid.uuid4()}{key}'
    return md5(key)


def timeit(func):
    """执行函数打印时间"""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        _hash = ""      # hash(str(args)+str(kwargs))
        print_str = f'===start {func.__name__} {_hash} , kwargs:{kwargs}.'
        print(print_str)
        logging.info(print_str)
        start = time.time()

        ret = func(*args, **kwargs)

        ms = 1000 * (time.time() - start)
        print_str = f'===end {func.__name__} {_hash} {ms}ms, kwargs:{kwargs}.'
        print(print_str)
        logging.info(print_str)

        return ret

    return new_func


def mkdir(path):
    """
    创建文件夹
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def remove_dir(path):
    """
    移除文件夹
    :param path:
    :return:
    """
    if os.path.exists(path):
        os.remove(path)


def catch_error(ignore_errors: List[type(Exception)] = None, raise_error: bool = True,
                callback: Callable = None, args: Union[list, tuple] = None, kwargs: dict = None):
    """
    异常捕获
    :param ignore_errors: 忽略的异常类型
    :param raise_error: 是否推出异常
    :param callback: 回调函数
    :param args: 回调函数参数
    :param kwargs: 回调函数参数
    :return:
    """
    ignore_errors = ignore_errors or []
    args = args or []
    kwargs = kwargs or {}

    def do(func):
        @functools.wraps(func)
        def decorated_func(*attr, **options):
            res = None
            try:
                res = func(*attr, **options)
            except (*ignore_errors,):
                pass
            except Exception as e:
                if callback is not None:
                    logging.error(traceback.format_exc())
                    callback(*args, **kwargs)
                if raise_error:
                    raise e
            return res

        return decorated_func

    return do


def is_linux():
    return platform.system().lower() == 'linux'
