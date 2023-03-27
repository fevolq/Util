#!-*-coding:utf-8 -*-
# python3.7
# @Author: F___Q
# Create time: 2022/10/5 16:36
# Filename:

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = ''
MYSQL_PWD = ''
MYSQL_DB = ''

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PWD = ''
REDIS_DB = {
    '': 0,
}

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_DB = ''
MONGO_USER = ''
MONGO_PWD = ''

ES_HOST = '127.0.0.1'
ES_PORT = 9200
ES_USER = ''
ES_PWD = ''

try:
    from .local_config import *
except:
    pass
