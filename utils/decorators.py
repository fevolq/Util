#!-*- coding:utf-8 -*-
# CreateTime: 2024/7/13 14:27
# FileName: 装饰器
import functools
import inspect
import logging
import time
import traceback
from functools import wraps
from typing import List, Callable, Union

from utils import log_sls


def func_log(__module__, __content__: str = '', ignore_args: List = None):
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

            log_sls.info(__module__, f'开始：{content}', **all_args)
            start = time.time()
            res = func(*args, **kwargs)
            end = time.time()
            log_sls.info(__module__, f'结束：{content}', func_spent=f'{round(end - start, 2)} s', **all_args)
            return res

        return decorated_func

    return do


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
                # logging.error(f'{func.__name__}: {str(e)}')
                # logging.exception(traceback.format_exc())
                log_sls.error('decorators', '出现未捕获的异常', func=func.__name__, e=str(e), exc=traceback.format_exc())
                if callback is not None:
                    callback(*args, **kwargs)
                if raise_error:
                    raise
            return res

        return decorated_func

    return do
