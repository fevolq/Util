#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/9/4 10:38
# FileName:

import bcrypt


def hash_password(password: str, salt=bcrypt.gensalt()):
    return bcrypt.hashpw(password.encode(), salt).decode()


def check_password(password: str, password_hash: str):
    return bcrypt.checkpw(password.encode(), password_hash.encode())


if __name__ == '__main__':
    # 注册
    pwd = '123456'      # 输入
    key = hash_password(pwd)    # 入库
    print(key)

    # 登录
    input_pwd = '123456'
    print(check_password(input_pwd, key))       # 查出库内的记录，再校验
