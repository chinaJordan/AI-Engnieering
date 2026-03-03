import CustomStore

class PersistentStore(CustomStore):
    '''
        持久化存储接口，所有的持久化实现类都需要实现该接口
    '''

    def insertList(self, key: str, datas: list) -> int:
        '''
        批量插入接口，该接口可接受数组类型，一次插入多条数据
        Note： 实现类需要自己处理异常及判空
        :param key:
        :param datas:
        :return:
        '''
        ...