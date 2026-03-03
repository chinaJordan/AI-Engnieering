''' 存储类实现基类，所有的存储实现都要继承该类并实现该类的方法  '''

from typing import Protocol, Any

class CustomStore(Protocol):

    def insert(self, key: str, data: Any) -> bool:
        '''
            数据插入接口，根据指定的key 和 value, 将数据存储下来
            实现类要自己加参数判断逻辑，并在实现时候说明是否支持None值
        '''
        ...

    def update(self, key: str, newData: Any) -> bool:
        '''
        根据指定的key 和新数据，更新数据。
        子类实现要自己判断参数是否支持None.
        :param key:
        :param newData:
        :return:
        '''
        ...

    def delete(self, key: str)-> bool:
        '''
        根据指定的key 删除数据，子类自己需要判断key 不存在时候处理逻辑
        :param key:
        :return:
        '''
        ...

    def query(self, key: str) -> Any:
        '''
        根据指定的key 查询数据，并返回。
        实现类需要自己处理当key 不存在时处理逻辑，并说明返回结果
        :param key:
        :return:
        '''