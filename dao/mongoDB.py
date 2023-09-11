#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2022/11/28 18:52
# FileName:

from dao import poolDB, db, config, db_exception


class Mongo:
    default_conf = {
        'host': config.MONGO_HOST,
        'port': config.MONGO_PORT,
        'user': config.MONGO_USER,
        'password': config.MONGO_PWD,
    }

    def __init__(self, db_name, db_conf, *, use_pool) -> None:
        if use_pool:
            self.__conn = poolDB.get_coon(mode='mongo', db_name=db_name, db_conf=db_conf)
            pass
        else:
            self.__conn = db.Db('mongo', db_name, db_conf)

    @property
    def coon(self):
        return self.__conn

    def execute(self, collection_name: str, action: str, *args, **kwargs):
        """

        :param action: 执行的命令
        :param collection_name: 指定的集合
        :param args:
        :param kwargs:
        :return:
        """
        raise_error = kwargs.pop('raise_error') if 'raise_error' in kwargs else True  # 是否扔出异常

        res = {'result': None, 'success': True}
        with self.__conn as coon:
            try:
                cursor = coon[collection_name]
                result = getattr(cursor, action)(*args, **kwargs)
                if action.lower().startswith('find'):  # 查询操作，必须在关闭游标前拿出结果
                    result = list(result)
                res['result'] = result
            except Exception as e:
                res['result'] = e
                res['success'] = False
                if raise_error:
                    raise db_exception.DbException(e)

        return res


def mongo_obj(db_name: int = None, *, db_conf: dict = None, use_pool: bool = False):
    """

    :param db_name: 库名
    :param db_conf: 数据库配置。格式参考 Mongo.default_conf
    :param use_pool: 是否使用连接池
    :return:
    """
    if db_name is None:
        db_name = config.MONGO_DB

    db_config = Mongo.default_conf
    if db_conf is not None:
        db_config.update(db_conf)

    return Mongo(db_name, db_config, use_pool=use_pool)


def execute(
        collection_name: str, action: str, *args,
        db_name: str = None, db_conf: dict = None,
        use_pool=True, **kwargs,
):
    """

    :param collection_name: 集合名
    :param action: 执行动作（方法str）
    :param args:
    :param db_name: 库名
    :param db_conf: 数据库配置。格式参考 Mongo.default_conf
    :param use_pool:
    :param kwargs:
    :return:
    """
    use_pool = False  # 强制使用Db实现
    mongo = mongo_obj(db_name, db_conf=db_conf, use_pool=use_pool)
    return mongo.execute(collection_name, action, *args, **kwargs)


if __name__ == '__main__':
    # result = execute('user', 'find', '', db_name='log')
    # result = execute('user', 'insert_many', [{'name': 'test_01'}], db_name='log').acknowledged
    # print(result)
    ...
