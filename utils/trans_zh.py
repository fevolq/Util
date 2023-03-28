#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/3/28 22:32
# FileName: 中文转换

"""
pip install opencc-python-reimplemented
"""

import threading

import opencc


class TransZH:

    __lock = threading.RLock()

    def __new__(cls, *args, **kwargs):
        # 构造单例
        if hasattr(cls, 'instance'):
            return cls.instance

        # 线程锁
        with cls.__lock:
            if not hasattr(cls, 'instance'):
                cls.instance = super(TransZH, cls).__new__(cls)
            return cls.instance

    def __init__(self):
        self._trad_simple = None        # 繁体 >> 简体
        self._simple_trad = None        # 简体 >> 繁体

    def get_convert(self, conversion):
        if conversion == 't2s':
            if self._trad_simple is None:
                self._trad_simple = opencc.OpenCC('t2s')
            return self._trad_simple
        elif conversion == 's2t':
            if self._simple_trad is None:
                self._simple_trad = opencc.OpenCC('s2t')
            return self._simple_trad

    def t2s(self, value):
        """
        繁体 >> 简体
        :param value:
        :return:
        """
        converter = self.get_convert('t2s')
        return converter.convert(value)

    def s2t(self, value):
        """
        简体 >> 繁体
        :param value:
        :return:
        """
        converter = self.get_convert('s2t')
        return converter.convert(value)


def t2s(value):
    """繁体 >> 简体"""
    return TransZH().t2s(value)


def s2t(value):
    """简体 >> 繁体"""
    return TransZH().s2t(value)


if __name__ == '__main__':
    # print(t2s('繁體'))
    # print(s2t('繁体'))
    ...
