import json
from typing import Any

from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain.agents.middleware import wrap_tool_call
from pydantic import BaseModel, Field
from langgraph.config import get_stream_writer


class LocationResponse(BaseModel):
    latitude: str = Field(description="维度信息")
    longitude: str = Field(description="经度信息")


@tool(description="根据输入的城市名字，查询城市的经纬度信息")
def getlocation(cityName: str) -> LocationResponse:
    if not cityName:
        raise Exception("cityName is null")
    print(f"find city: {cityName} location: 30.26°N， 120.16°E")
    # {"latitude": "30.26°N", "longitude": "120.16°E}?
    write = get_stream_writer()
    write(f"Look for the info in {cityName}")
    write(f"Accquire data for city: {cityName}")
    print(f"Response data: {LocationResponse(latitude='30.26°N', longitude='120.16°E').model_dump_json()}")
    # print(f"Convert JSON Success!")
    # f"latitude: 30.26°N, longitude: 120.16°E "
    return LocationResponse(latitude='30.26°N', longitude='120.16°E')


@tool(description="根据输入的城市名字，查询天气情况")
def queryWeather(city: str) -> str:
    "查询天气信息"
    return f"当前城市： {city} 天气是晴，风力2级， 空气质量优。"


@wrap_tool_call
def handleToolError(request, handle):
    "处理工具调用异常"
    try:
        return handle(request)
    except Exception as e:
        print(f"Tool call Exception: {e}")
        return ToolMessage(content=f"Tool call error, please check input, exception: {e}",
                           tool_call_id=request.tool_call["id"])
