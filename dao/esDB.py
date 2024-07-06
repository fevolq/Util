#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2022/12/13 11:18
# FileName:

from dao import poolDB, db, config, db_exception


class Elasticsearch:
    default_conf = {
        'host': config.ES_HOST,
        'port': config.ES_PORT,
        'user': config.ES_USER,
        'password': config.ES_PWD,
    }

    def __init__(self, db_conf, *, use_pool) -> None:
        if use_pool:
            self.__conn = poolDB.get_coon(mode='elasticsearch', db_conf=db_conf)
        else:
            self.__conn = db.Db('elasticsearch', db_conf=db_conf)

    @property
    def coon(self):
        return self.__conn

    def execute(self, index_name: str, action: str, *args, **kwargs):
        """

        :param index_name: 指定的索引
        :param action: 执行的命令
        :param args:
        :param kwargs:
        :return:
        """
        raise_error = kwargs.pop('raise_error') if 'raise_error' in kwargs else True  # 是否扔出异常

        res = {'result': None, 'success': True}
        with self.__conn as coon:
            try:
                result = getattr(coon, action)(index=index_name, *args, **kwargs)
                res['result'] = result
            except Exception as e:
                res['result'] = str(e)
                res['success'] = False
                if raise_error:
                    raise db_exception.DbException(e)

        return res


def es_obj(db_conf: dict = None, *, use_pool: bool = True):
    db_config = Elasticsearch.default_conf
    if db_conf is not None:
        db_config.update(db_conf)

    return Elasticsearch(db_config, use_pool=use_pool)


def execute(
        index_name: str, action: str, *args,
        db_conf: dict = None,
        use_pool=False, **kwargs,
):
    """

    :param index_name: 索引名
    :param action: 执行动作（方法str）
    :param args:
    :param db_conf: 数据库配置。格式参考 Elasticsearch.default_conf
    :param use_pool: 是否使用池
    :param kwargs:
    :return:
    """
    es = es_obj(db_conf, use_pool=use_pool)
    return es.execute(index_name, action, *args, **kwargs)


if __name__ == '__main__':
    # result = execute('demo', 'index', {'name': 'test_01'})
    # print(result)
    ...
