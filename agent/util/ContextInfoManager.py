""" 上下文信息管理， 这里可以存储一些需要全局访问的数据，目前只是单机访问，不支持集群，如果需要集群访问，可自定义实现 """

from typing import Any

from agent.util import log

CONTEXT_INFO: dict[str, Any] = {}

def putValue(key: str, value: Any)-> bool:
    '''
    存储指定的key 和 value, 但不允许key 或者value 为None
    :param key:    不能为None
    :param value:  不能为Nones
    :return:   bool
    '''
    if not key or not value:
        log.info(f"Key and value can't be None!")
        return False

    CONTEXT_INFO.setdefault(key, value)
    return True

def getValue(key: str) -> Any:
    """
        根据指定的key, 查找对应的值，如果找到则返回，否则返回None
        Key 不允许为None
     """
    if not key:
        raise Exception("Key can't be None! Please input a value!")

    return CONTEXT_INFO.get(key, None)

def deleteKey(key: str)-> bool:
    if not key:
        raise Exception("Key can't be None! Please input a value!")
    try:
        CONTEXT_INFO.pop(key)
    except Exception as e:
        log.error(f"Delete key : {key} fail! Exception: {e}")
        return False

    return True




