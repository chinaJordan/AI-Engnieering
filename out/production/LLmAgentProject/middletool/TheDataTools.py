from typing import Any

from langchain.tools import tool, ToolRuntime

@tool
def saveData(runtime: ToolRuntime, userInfo: dict[str,Any]) -> str:
    """将用户数据保存到数据库"""
    if not dict:
        print("要保存的数据为空！")
        return "None"
    store = runtime.store
    store.put("users", dict["userId"],userInfo);
    print(f"Save user id {dict['userId']} success!")
    return "success"


@tool
def getData(runtime: ToolRuntime, userId: str) -> dict:
    """根据用户ID查询用户信息"""
    if not userId:
        print("UserId is empty, please input a content!")
        return {}
    store = runtime.store;
    result = store.get("users",userId);
    print(f"查询用户ID： {userId} 信息成功， 返回结果： {result}")
    return result