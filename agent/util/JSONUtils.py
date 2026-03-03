import json


def isJson(input: str)-> bool:
    '''
    判断输入内容是否是json 格式，如果是json 格式返回True, 不是返回False
    :param input:
    :return:
    '''
    if not input:
        return False

    try:
        json.loads(input)
        return True
    except (json.JSONDecodeError, TypeError):
        return False
