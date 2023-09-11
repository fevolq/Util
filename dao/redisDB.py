#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2022/10/27 16:54
# FileName:
from typing import Union

from dao import poolDB, db, config, db_exception


class Redis:
    default_conf = {
        'host': config.REDIS_HOST,
        'port': config.REDIS_PORT,
        'password': config.REDIS_PWD,
    }
    default_db = 0

    def __init__(self, db_name, db_conf, *, use_pool) -> None:
        if use_pool:
            self.__conn = poolDB.get_coon(mode='redis', db_name=db_name, db_conf=db_conf)
        else:
            self.__conn = db.Db('redis', db_name, db_conf)

    @property
    def coon(self):
        return self.__conn

    def execute(self, action, *args, **kwargs) -> dict:
        raise_error = kwargs.pop('raise_error') if 'raise_error' in kwargs else True  # 是否扔出异常

        res = {'result': None, 'success': True}
        with self.__conn as coon:
            try:
                result = getattr(coon, action)(*args, **kwargs)
                res['result'] = result
            except Exception as e:
                res['result'] = e
                res['success'] = False
                if raise_error:
                    raise db_exception.DbException(e)

        return res


def redis_obj(db_name: Union[int, str] = Redis.default_db, *, db_conf: dict = None, use_pool: bool = True):
    """

    :param db_name: 库名。int 或 config中已有的命名定义
    :param db_conf: 数据库配置。格式参考 Redis.default_conf
    :param use_pool: 是否使用连接池
    :return:
    """
    db_name = config.REDIS_DB.get(db_name, db_name)

    db_config = Redis.default_conf
    if db_conf is not None:
        db_config.update(db_conf)

    return Redis(db_name, db_config, use_pool=use_pool)


def execute(
        action: str, *args,
        db_name: Union[int, str] = Redis.default_db, db_conf: dict = None,
        use_pool=True, **kwargs,
):
    """

    :param action: 执行动作（方法str）
    :param args:
    :param db_name: 库名。int 或 config中已有的命名定义
    :param db_conf: 数据库配置。格式参考 Redis.default_conf
    :param use_pool: 是否使用连接池
    :param kwargs:
    :return:
    """
    redis = redis_obj(db_name=db_name, db_conf=db_conf, use_pool=use_pool)
    return redis.execute(action, *args, **kwargs)


if __name__ == '__main__':
    ...

    # # string
    # result = execute('set', 'key_string', 11, db_name=14, use_pool=False)
    # result = execute('get', 'key_string', db_name=14, use_pool=False)         # 获取单个
    # result = execute('mget', ['key_string', ], db_name=14, use_pool=False)    # 获取指定的多个key

    # # hash
    # result = execute('hset', 'key_hash', 'a', 11, db_name=14, use_pool=False)      # 单个键值对
    # result = execute('hmset', 'key_hash', {'b': 22, 'c': 'cc'}, db_name=14, use_pool=False)    # 多个键值对
    # result = execute('hget', 'key_hash', 'a', db_name=14, use_pool=True)      # 获取指定键的值
    # result = execute('hgetall', 'key_hash', db_name=14, use_pool=True)        # 获取所有键值对

    # # set
    # result = execute('sadd', 'key_set', 'a', 11, 22, db_name=14, use_pool=True)
    # result = execute('smembers', 'key_set', db_name=14, use_pool=True)

    # print(type(result['result']))
    # print(result, type(result['result']))
