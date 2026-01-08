from typing import Any

from langchain.tools import tool, ToolRuntime

dataStore = {}

@tool
def saveData(runtime: ToolRuntime, userInfo: dict[str,Any]) -> str:
    """将用户数据保存到数据库
        args: dict[str,Any]

        返回数据类型： str
    """
    if not dict:
        print("要保存的数据为空！")
        return "None"
    store = runtime.store
    print(f"Current store type: {type(store)}")
    userId = userInfo['userId'] if userInfo['userId'] else "user1"
    # store[userId] = userInfo;
    dataStore[userId] = userInfo
    print(f"Save user id {userId} success!")
    return "success"


@tool
def getData(runtime: ToolRuntime, userId: str) -> dict:
    """根据用户ID查询用户信息
        args: userId

        返回数据类型： dict[str,Any]
    """
    if not userId:
        print("UserId is empty, please input a content!")
        return {}
    store = runtime.store;
    # result = store.get("users",userId);
    # result = store[userId if userId else "user1"]
    result = dataStore[userId if userId else "user1"]
    print(f"查询用户ID： {userId} 信息成功， 返回结果： {result}")
    return result