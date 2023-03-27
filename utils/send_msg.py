#!-*coding:utf-8 -*-
# python3.7
# CreateTime: 2022/11/4 18:16
# FileName: 发送消息

import json
import typing

import requests


# def robot_msg(robot_url: str, content: typing.Union[dict, str]):
#     """飞书 机器人消息"""
#     try:
#         assert robot_url
#         keys = ("msgtype", "text", "content")
#         if ".feishu." in robot_url:
#             keys = ("msg_type", "content", "text")
#         if isinstance(content, dict):
#             content = json.dumps(content, ensure_ascii=False)
#         requests.post(
#             robot_url,
#             json={
#                 keys[0]: "text",
#                 keys[1]: {
#                     keys[2]: content
#                 }
#             }
#         )
#     except Exception:
#         pass


def feishu_robot_msg(robot_url: str, content: typing.Union[dict, str], title=None):
    """飞书 机器人消息"""
    try:
        assert robot_url
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)
        requests.post(
            robot_url,
            json={
                "msg_type": "post",
                "content": {
                    "post": {
                        "zh_cn": {
                            "title": title,
                            "content": [
                                [
                                    {
                                        "tag": "text",
                                        "text": content,
                                    }
                                ]
                            ]
                        }
                    }
                }
            }
        )
    except Exception:
        pass


if __name__ == '__main__':
    info = 'hello world\nhttps://www.baidu.com'
    url = ''
    feishu_robot_msg(url, info, title='test')
