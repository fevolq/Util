#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/4/10 14:31
# FileName: 命令行执行

import subprocess
from typing import List


class Command:

    def __init__(self, inputs: List):
        self.inputs = inputs
        self.proc = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def __call__(self, *args, **kwargs):
        for args in self.inputs:
            info = args
            if isinstance(args, (list, tuple)):
                info = ' '.join(args)
            print(f'Execute command: {info}')
            self.proc.stdin.write(info.encode('utf-8') + b'\n')

        # self.proc.stdin.close()   # TODO：是否关闭（释放资源）
        stdout, stderr = self.proc.communicate()
        return stdout, stderr


def command(inputs: List):
    """

    @param inputs: [] or [[], ]
    @return:
    """
    return Command(inputs)()


if __name__ == '__main__':
    args_list = [
        ['cd', '/data/Demo'],
        ['source', './venv/bin/activate'],
        ['cd', './project/application'],
        ['python', './app.py >/dev/null 2>&1'],
    ]
    command(args_list)
