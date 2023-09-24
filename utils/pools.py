#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2022/11/4 18:15
# FileName:

import concurrent.futures
from typing import List

import threadpool
import gevent
from gevent.pool import Pool
from gevent import monkey

THREAD_POOL_SIZE = 4
GEVENT_POOL_SIZE = 4


def execute_thread(callback, args_list: List = None, times: int = 0, pools: int = 4, force_pool: bool = False):
    """
    多线程
    :param callback: 单线程的执行方法
    :param args_list: 单线程的参数组成的数组。[[(args1, args2,), {'key1': value1, 'key2': value2}], ]
    :param times: 执行的次数。当args_list为空时，生效，否则使用args_list的数量来判断
    :param pools: 线程池数量
    :param force_pool: 当pools大于设定的最大限制时，是否强制使用pools
    :return:
    """
    # 获取 max_workers
    if pools > THREAD_POOL_SIZE and not force_pool:
        pools = THREAD_POOL_SIZE

    # 获取执行次数
    args_length = len(args_list) if args_list else 0
    times = args_length or times
    assert times, '参数异常，导致执行次数为0'
    pools = min(times, pools)

    # 解析参数
    def get_params(params):
        item_args = params[0] if any([isinstance(params[0], tuple), isinstance(params[0], list)]) else []
        item_kwargs = params[-1] if isinstance(params[-1], dict) else {}
        return item_args, item_kwargs

    with concurrent.futures.ThreadPoolExecutor(max_workers=pools) as executor:
        futures = []
        for i in range(times):
            if args_list:
                args, kwargs = get_params(args_list[i])
                future = executor.submit(callback, *args, **kwargs)
            else:
                future = executor.submit(callback)
            futures.append(future)

        # 获取任务的结果
        result = [future.result() for future in futures]
    return result


def _execute_thread(func, args_list, pools: int = 4, force_pool: bool = False):
    """
    多线程
    :param func: 单线程的执行方法
    :param args_list: 单线程的参数组成的数组。[[(args1, args2,), {'key1': value1, 'key2': value2}], ]
    :param pools: 线程池数量
    :param force_pool: 当pools大于设定的最大限制时，是否强制使用pools
    :return:
    """
    if pools > THREAD_POOL_SIZE and not force_pool:
        pools = THREAD_POOL_SIZE
    if len(args_list) <= pools:
        pools = len(args_list)
    thread_pool = threadpool.ThreadPool(pools)
    result_list = [None] * len(args_list)

    # 构造不定参数
    def tmp_f(item):
        args = item[0] if any([isinstance(item[0], tuple), isinstance(item[0], list)]) else []
        kwargs = item[-1] if isinstance(item[-1], dict) else {}
        return func(*args, **kwargs)

    # 构造回调函数
    def callback(req, result):
        result_list[task_list.index(req)] = result

    task_list = threadpool.makeRequests(tmp_f, args_list, callback)
    [thread_pool.putRequest(task) for task in task_list]
    # task_pool.poll()
    thread_pool.wait()
    return result_list


def execute_event(callback, args_list: List = None, times: int = 0, pools=4, force_pool=False):
    """
    多协程
    :param callback: 单协程的执行方法
    :param args_list: 单协程的参数组成的数组。[[(args1, args2,), {'key1': value1, 'key2': value2}], ]
    :param times: 执行的次数。当args_list为空时，生效，否则使用args_list的数量来判断
    :param pools: 协程池数量
    :param force_pool: 当pools大于设定的最大限制时，是否强制使用pools
    :return:
    """
    monkey.patch_socket()  # 识别IO阻塞

    if pools > GEVENT_POOL_SIZE and not force_pool:
        pools = GEVENT_POOL_SIZE

    # 获取执行次数
    args_length = len(args_list) if args_list else 0
    times = args_length or times
    assert times, '参数异常，导致执行次数为0'
    pools = min(times, pools)

    # 解析参数
    def get_params(params):
        item_args = params[0] if any([isinstance(params[0], tuple), isinstance(params[0], list)]) else []
        item_kwargs = params[-1] if isinstance(params[-1], dict) else {}
        return item_args, item_kwargs

    def func(index):
        if args_list:
            args, kwargs = get_params(args_list[index])
            return callback(*args, **kwargs)
        else:
            return callback()

    gevent_pool = gevent.pool.Pool(pools)
    task_list = [gevent_pool.spawn(func, i) for i in range(times)]
    gevent.joinall(task_list)

    result = [task.value for task in task_list]
    return result
