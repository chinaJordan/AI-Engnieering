import os
import threading
import time
import weakref

# 弱引用map
# global_instance_map = weakref.WeakValueDictionary()

# 普通map
global_instance_map = {}

map_lcok = threading.Lock()

class TimeUtil:



    def __init__(self, name: str, start: int, end: int):
        if not name:
            raise ValueError("name must't be null or Empty!")
        if start < 0:
            raise ValueError("start time must great than 0!")
        if end < 0:
            raise ValueError("end time must great than 0!")
        self.name = name
        self.start = start
        self.end = end
        with map_lcok:
            global_instance_map.setdefault(name, self)

    @classmethod
    def callStart(cls, name: str):
        startTime = time.time_ns()
        return cls(name, startTime, 0)


    def callEnd(self):
        endTime = time.time_ns()
        self.end = endTime

    ''' 计算耗时，单位纳秒 '''
    def computeSpandTime(self) -> str:
        responseTemplate = "start time: {start}, end time: {end}, 耗时：{cost} 秒！"
        return responseTemplate.format(start=self.start, end=self.end, cost=(self.end - self.start) / 10**9)

# if __name__ == "__main__":
#     TimeUtil.callStart("first")
#     try:
#         time.sleep(2)
#     except KeyboardInterrupt:
#         print(f"当前线程被意外中断唤醒了！")
#         raise InterruptedError(f"休眠线程被意外中断了, 线程名字： {threading.current_thread().name}")
#
#     timeUtil = global_instance_map.get("first");
#     if isinstance(timeUtil, TimeUtil):
#         timeUtil.callEnd()
#     else :
#         print("Class type not match!")
#
#     print(f"find instance by first: {global_instance_map.get('first')} ")
#     print(timeUtil.computeSpandTime())
#     del timeUtil
#     global_instance_map.pop("first")
#     print(f" After del instance, find instance by first: {global_instance_map.get('first')}, global_instance_map :{global_instance_map.__len__()} ")
#



