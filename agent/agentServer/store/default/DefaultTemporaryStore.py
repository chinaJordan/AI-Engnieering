
import threading
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
from agent.util import log
from agent.agentServer.store import TemporaryStore, CustomStore

class DefaultTemporaryStore(TemporaryStore, CustomStore):
    """基于本地内存的临时存储实现类"""

    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._expiry_times: Dict[str, datetime] = {}

    def insertByTimeout(self, key: str, expire: Optional[float] = None, data: Any = None ) -> bool:
        '''
        根据指定的key,数据存储数据，如果过期时间存在，则设置过期时间，否则
        :param key:  存储数据键，不能为空
        :param expire:  过期时间，单位秒
        :param data:   存储数据
        :return: bool
        '''
        if not key:
            raise ValueError("Key cannot be empty")

        if not expire:
            try:
                with self._lock:
                    self._store[key] = data
                    return True

            except Exception as e:
                log.info(f"Put key: {key} to local temporary store fail! Exception: {e}")
                return False

        try:
            with self._lock:
                self._store[key] = data
                ttl = timedelta(seconds=expire)
                expire_time = ttl + datetime.now()
                self._expiry_times[key] = expire_time
                # self._expiry_times.setdefault(key, expire_time)

        except Exception as e:
            log.info(f"Put key: {key} to local temporary store fail! expire time: {expire},  Exception: {e}")
            return False

        return True


    def insert(self, key: str, data: Any) -> bool:
        '''
            数据插入接口，根据指定的key 和 value, 将数据存储下来
            如果插入失败，会打印日志异常，并返回 False. 成功返回 True
        '''
        if not key:
            raise ValueError("Key cannot be empty")
        try:
            with self._lock:
                self._store[key] = data
        except Exception as e:
            log.info(f"Insert data to local temporary store Fail! key : {key}, Exception: {e} ")
            return False

        return True

    def update(self, key: str, newData: Any) -> bool:
        '''
            根据指定的key 和新数据，更新数据。
            如果更新失败，会打印失败信息， 并返回False, 更新成功返回 True
        :param key:
        :param newData:
        :return:
        '''
        if not key:
            raise ValueError("Key cannot be empty")
        try:
            with self._lock:
                self._store[key] = newData
        except Exception as e:
            log.info(f"Update data to local temporary store Fail! key : {key}, Exception: {e} ")
            return False

        return True

    def delete(self, key: str) -> bool:
        '''
        根据指定的key 删除数据，子类自己需要判断key 不存在时候处理逻辑
        :param key:
        :return:
        '''
        if not key:
            raise ValueError("Key cannot be empty")
        try:
            with self._lock:
                self._store.pop(key, None)
                log.info(f"[Temporary store] Delete key {key} success!")
        except Exception as e:
            log.info(f"Insert data to local temporary store Fail! key : {key}, Exception: {e} ")
            return False

        return True

    def query(self, key: str) -> Any:
        '''
        根据指定的key 查询数据，并返回。
        如果 key 不存在或者已经过期，则返回None
        :param key:
        :return:
        '''
        if not key:
            raise ValueError("Key cannot be empty")
        try:
            result = self._store.get(key, None)
            if not result:
                return result

            if self._expiry_times.__contains__(key):
                not_expire = datetime.now() > self._expiry_times[key]
                if not not_expire:
                    return result
                else:
                    with self._lock:
                        log.info(f"Key exists time arraive! delete key : {key}")
                        self._expiry_times.pop(key, None)
                    return None

            return result
        except Exception as e:
            log.info(f"Insert data to local temporary store Fail! key : {key}, Exception: {e} ")
            return None



if __name__ == "__main__":
    key = "test"
    data = "Hello, Baby!"
    tempStore = DefaultTemporaryStore()

    tempStore.insert(key, data)
    tempStore.insert(key, 'Hey, this a new data!')

    tempStore.insertByTimeout(key, 10, data)

    rsult = tempStore.query(key)
    print(f"Query result: {rsult}")


