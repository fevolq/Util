import json
from typing import List

import requests


def robot_text(url: str, text: str, *, title: str = None, href: List[dict] = None, at: [str] = None):
    """
    飞书机器人（文本）
    :param url:
    :param text: 内容
    :param title: 标题
    :param href: 超链接。{'href': '链接', 'text': '文本'}
    :param at: @用户的user_id
    :return:
    """
    assert url, '缺少 url'

    content = []

    assert isinstance(text, str), '文本内容 必须为字符串'
    content.append([{'tag': 'text', 'text': text}])

    if href:
        a_arr = []
        for item in href:
            assert isinstance(item.get('href'), str) and isinstance(item.get('text'), str), 'href 格式错误'
            a_arr.append({'tag': 'a', **item})
            a_arr.append({'tag': 'text', 'text': ' '})
        content.append(a_arr)
    if at:
        at_arr = []
        for item in at:
            at_arr.append({'tag': 'at', 'user_id': item})
        content.append(at_arr)

    resp = requests.post(
        url,
        json={
            'msg_type': 'post',
            'content': json.dumps(
                {
                    'post': {
                        'zh_cn': {
                            'title': title,
                            'content': content,
                        }
                    },
                },
                ensure_ascii=False,
            ),
        }
    )
    return resp


def robot_text_v2(url: str, content: [List[dict]], *, title: str = None):
    """
    飞书机器人（文本）
    robot_text_v2(url, title='v2', content=[
        [{'tag': 'text', 'text': '文本1'}, {'tag': 'text', 'text': ' '}, {'tag': 'a', 'text': '飞书', 'href': 'https://open.feishu'}],
        [{'tag': 'text', 'text': '\n'}],
        [{'tag': 'text', 'text': '文本2'}, {'tag': 'text', 'text': '文本22'}, {'tag': 'text', 'text': '\n'}, {'tag': 'a', 'text': '百度', 'href': 'https://www.baidu.com'}],
        [{'tag': 'text', 'text': '文本3'}, {'tag': 'a', 'text': 'google', 'href': 'https://www.google.com'}],
    ])
    :param url:
    :param content: 内容
    :param title: 标题
    :return:
    """
    assert url, '缺少 url'

    resp = requests.post(
        url,
        json={
            'msg_type': 'post',
            'content': json.dumps(
                {
                    'post': {
                        'zh_cn': {
                            'title': title,
                            'content': content,
                        }
                    },
                },
                ensure_ascii=False,
            ),
        }
    )
    return resp


def robot_template(url: str, template_id: str, version: str, variable: dict):
    """
    飞书机器人（模板）
    :param url:
    :param template_id: 模板ID
    :param version: 模板版本
    :param variable: 参数
    :return:
    """
    assert url, '缺少 url'

    data = {
        "msg_type": "interactive",
        "card": {
            "type": "template",
            "data": {
                "template_id": template_id,
                "template_version_name": version,
                "template_variable": variable
            }
        }
    }
    resp = requests.post(
        url,
        json=data
    )
    return resp
