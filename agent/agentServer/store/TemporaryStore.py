'''
    接口约束，继承自 CustomStore, 该接口实现是一个约束规则，表示临时存储
'''

from agent.agentServer.store import CustomStore
from typing import Any



class TemporaryStore(CustomStore):

    def insertByTimeout(self, key: str, expire: float, data: Any ) -> bool:
        '''
        带有过期时间插入操作，时间单位： 秒
        实现类需要自己判断空值及异常场景。
        :param key:
        :param expire:
        :param data:
        :return:
        '''
        ...