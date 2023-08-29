#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/8/29 16:35
# FileName:

"""
字段值校验。

单字段校验：check_one_col
    与：{col: {校验符1: 条件值, 校验符2: 条件值, ...}}
    或：{col: [{校验符1: 条件值, ...}, ...]}

    示例：
    {'a': {'=': 1}}  =>  a == 1
    {'a': {'>': 0, '<': 10}}  =>  0 < a < 9
    {'a': [{'<': 0}, {'IN': [3, 6, 9]}]}  =>  a < 0 or a in [3, 6, 9]

多字段校验：check_conditions
    与：{AND: [check_conditions, ...]}
    或：{OR: [check_conditions, ...]}
    可相互嵌套，但最内层一定为 check_one_col
"""

from typing import Union


def check(op, col_value, check_value):
    """
    {op: value}
    :param op: 比较符
    :param col_value:
    :param check_value:
    :return:
    """
    op = op.upper()
    if op == '=':
        return col_value == check_value
    elif op == '!=' or op == '<>':
        return col_value != check_value
    elif op == '>':
        return col_value > check_value
    elif op == '>=':
        return col_value >= check_value
    elif op == '<':
        return col_value < check_value
    elif op == '<=':
        return col_value <= check_value
    elif op == 'IN':
        return col_value in check_value
    elif op == 'NOT IN':
        return col_value not in check_value
    else:
        raise Exception(f'error op: {op}')


def check_one_col(row: dict, condition: dict) -> bool:
    """
    一个字段的条件校验
    与：{col: {op_1: value_1, op_2: 条件值}}
    或：{col: [op_condition_1, op_condition_1]}
    :param row:
    :param condition: and: {'col': {'op': 'value', }}、 or: {'col': [{'op': 'value'}, ]}
    :return: bool
    """

    def get_check_value(value):
        """
        获得用于比较的“值”
        :param value: 条件值。即 condition中的value
        :return:
        """
        if isinstance(value, str):
            # 引用其他字段的值。row = {'a': 1, 'b': 2}, condition = {'a': {'>': '[b]'}}
            if value.startswith('[') and value.endswith(']'):
                check_col = value.lstrip('[').rstrip(']')
                if check_col not in row:
                    value = None
                else:
                    value = row[check_col]
        elif isinstance(value, (list, tuple)):
            tmp_value = []
            for v in value:
                tmp_value.append(get_check_value(v))
            value = tmp_value
        return value

    def check_one(col_value, op, condition_value):
        """
        检验单个 {op: condition_value}
        :param col_value: 字段值，即校验值
        :param op: 校验符
        :param condition_value: 条件值
        :return:
        """
        op = op.upper()
        check_value = get_check_value(condition_value)
        if check_value is None:  # 字段不存在时，为False
            checked = False
        else:
            checked = check(op, col_value, check_value)
        return checked

    def and_op(col_value, col_term: dict):
        result = []
        for op, term_value in col_term.items():
            result.append(check_one(col_value, op, term_value))
        return all(result)

    def or_op(col_value, col_terms: Union[list, tuple]):
        result = []
        for col_term in col_terms:
            result.append(and_op(col_value, col_term))
        return any(result)

    correct = False
    for col, term in condition.items():
        assert col in row, f'Field —— [{col}] not found in row'

        if isinstance(term, dict):
            correct = and_op(row[col], term)
        elif isinstance(term, (list, tuple)):
            correct = or_op(row[col], term)
        break
    return correct


def check_conditions(row: dict, conditions: dict) -> bool:
    """
    conditions：
        {
            'OR': [
                {'OR': [condition1, condition2]},
                {'AND': [condition3, condition4]},
            ]
        }

    condition1：
    {'OR': [col_conditions_1, col_conditions_2]} 或 col_conditions_1
    最内层的条件格式为check_one_col的condition
    :param row:
    :param conditions:
    :return:
    """
    assert len(conditions) == 1, 'The length of conditions must be 1'

    link = list(conditions.keys())[0]
    if link.upper() in ('AND', 'OR'):
        conditions = conditions[link]
    else:
        return check_one_col(row, conditions)

    result = []
    for one in conditions:
        one_result = check_conditions(row, one)
        result.append(one_result)
        if link.upper() == 'AND' and not one_result:
            break
        elif link.upper() == 'OR' and one_result:
            break

    return all(result) if link.upper() == 'AND' else any(result)


if __name__ == '__main__':
    data = {'a': 1, 'b': 2, 'c': 1, 'aa': 'a', 'bb': 'bb', 'cc': 'a'}

    # # 单字段校验
    # test_one_col = {'a': {'!=': '[b]', '=': 1, 'IN': ["[a]", 2, 3]}}
    # print(check_one_col(data, test_one_col))

    # (c==1) and ((a==b or a in [2, 'a', c]) or (b==1))     ==>  True
    test_1 = {'AND': [{'c': {'=': 1}}, {'OR': [{'a': [{'=': '[b]'}, {'IN': [2, 'a', '[c]']}]}, {'b': {'=': 1}}]}]}
    # (c==1) and ((a==b or a in [2, 'a', 'c']) or (b==1))     ==>  False
    test_2 = {'AND': [{'c': {'=': 1}}, {'OR': [{'a': [{'=': '[b]'}, {'IN': [2, 'a', 'c']}]}, {'b': {'=': 1}}]}]}
    # (c==1) and ((a==b and a in [2, 'a', c]) or (b==1))     ==>  False
    test_3 = {'AND': [{'c': {'=': 1}}, {'OR': [{'a': {'=': '[b]', 'IN': [2, 'a', '[c]']}}, {'b': {'=': 1}}]}]}
    # (c==1) and ((a!=b and aa=='a') or (b==1))     ==>  True
    test_4 = {'AND': [{'c': {'=': 1}}, {'OR': [{'AND': [{'a': {'!=': '[b]'}}, {'aa': {'=': 'a'}}]}, {'b': {'=': 1}}]}]}

    # print(check_conditions(data, test_4))
