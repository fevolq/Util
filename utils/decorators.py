#!-*- coding:utf-8 -*-
# FileName:

import threading
import time
import traceback
from functools import wraps
from typing import List, Union, Callable
import inspect

from utils import log_sls


def func_log(__module__, __content__: str = '', *, ignore_args: List = None):
    """
    函数启动与终止的日志
    :param __module__:
    :param __content__:
    :param ignore_args:
    :return:
    """
    ignore_args = ignore_args or []

    def do(func):
        content = __content__ or func.__name__

        @wraps(func)
        def decorated_func(*args, **kwargs):
            # 获取func的传参（参数名称）
            sig = inspect.signature(func)  # 获取函数签名
            params = list(sig.parameters.keys())  # 获取函数参数名
            bound_args = sig.bind(*args, **kwargs).arguments  # 将参数名与 *args 和 **kwargs 中的值关联起来
            all_args = {k: v for k, v in bound_args.items() if k in params and k not in ignore_args}  # 转换为字典形式

            log_sls.info(__module__, f'开始：{content}', func_id=id(sig), **all_args)
            start = time.time()
            res = func(*args, **kwargs)
            end = time.time()
            log_sls.info(__module__, f'结束：{content}',
                         func_id=id(sig), func_spent=f'{round(end - start, 2)} s', **all_args)
            return res

        return decorated_func

    return do


def retry(__module__, __content__: str = '', *, ignore_except_list: List = None, max_times: int = 0, interval: int = 0):
    """
    重试
    :param __module__:
    :param __content__:
    :param ignore_except_list: 不重试的异常，直接推出异常
    :param max_times: 最大重试次数
    :param interval: 重试间隔（min）
    :return:
    """
    ignore_except_list = ignore_except_list or []
    max_times = max(max_times, 0)
    interval = max(interval, 0)

    def do(func):
        content = __content__ or func.__name__

        @wraps(func)
        def decorated_func(*args, **kwargs):
            res = None
            times = 0
            while times <= max_times:
                try:
                    res = func(*args, **kwargs)
                    break
                except (*ignore_except_list,):
                    raise
                except Exception:
                    if times >= max_times:
                        raise
                times += 1
                time.sleep(interval * 60)
                log_sls.info(__module__, f'开始重试：{content}', times=times)

            return res

        return decorated_func

    return do


def thread_lock(lock: Union[threading.Lock, threading.RLock]):
    """
    线程锁
    :param lock:
    :return:
    """

    def decorator(func):
        def locked_func(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)

        return locked_func

    return decorator


def catch_error(
        __module__, __content__: str = '', *,
        ignore_errors: List[type(Exception)] = None,
        raise_error: bool = True,
        callback: Callable = None, args: Union[list, tuple] = None, kwargs: dict = None,
):
    """
    异常捕获
    :param __module__:
    :param __content__:
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
        @wraps(func)
        def decorated_func(*attr, **options):
            res = None
            try:
                res = func(*attr, **options)
            except (*ignore_errors,):
                pass
            except Exception as e:
                log_sls.error(__module__, __content__, func=func.__name__,
                              e=str(e), exc=traceback.format_exc(), )
                if callback is not None:
                    callback(*args, **kwargs)
                if raise_error:
                    raise
            return res

        return decorated_func

    return do
