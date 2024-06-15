#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2024/6/15 11:57
# FileName: jwt鉴权 与 序列化

import datetime
import pickle
import base64

import jwt  # pip install jwt


class User(object):
    def __init__(self, uid, email: str = ''):
        self.uid = uid
        self.email = email
        self.role: Role = ...
        self.permission: Permission = ...
        self._prepare()

    def _prepare(self):
        if self.uid:
            self.email = 'xxx@demo.com'
        else:
            self.uid = '01'
        self.role = Role(self.uid)
        self.permission = Permission(self.role.role_id)


class Role:

    def __init__(self, uid):
        self._uid = uid
        self.role_id = ''
        self._prepare()

    def _prepare(self):
        self.role_id = '01'


class Permission:

    def __init__(self, role_id):
        self.role_id = role_id
        self.domains = ['read', 'write']


def create_token(user: User):
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    serialized_user = base64.b64encode(pickle.dumps(user)).decode('utf-8')

    # 构建payload
    payload = {
        'exp': expire_time,
        'uid': user.uid,
        'user': serialized_user,
        # 当前权限的版本（应对后台更改用户权限时的校验）
    }

    # 签名并生成令牌
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def validate_token(token):
    payload = None
    success = False
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        success = True
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
    except jwt.InvalidTokenError:
        print("Invalid token.")
    return success, payload


def main():
    admin = User('02')
    token = create_token(admin)
    print(token)
    is_valid, payload = validate_token(token)
    if not is_valid:
        print('over')
        return
    print(payload)

    serialized_user = payload.get('user', '')
    user_bytes = base64.b64decode(serialized_user.encode('utf-8'))

    # 使用pickle反序列化得到User对象
    user = pickle.loads(user_bytes)
    print(user.role.role_id)


secret_key = 'xxx'
main()
