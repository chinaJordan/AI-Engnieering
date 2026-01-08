# 演示仅模型调用
import asyncio
import time

from config import global_config
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.rate_limiters import  InMemoryRateLimiter
from pydantic import BaseModel,Field
from middletool.TheDataTools import saveData,getData

chatModel = init_chat_model("deepseek-chat")

''' 限流器使用 '''

rateLimit = InMemoryRateLimiter(requests_per_second=3, check_every_n_seconds=0.1, max_bucket_size=20)

'''' 普通调用，调用模型，直到完成再返回结果 '''


def blockCallModel():
    promptTemplate = PromptTemplate.from_template("你好，你的问题是 {question},请告诉我这个问题答案",
                                                  template_format="f-string")

    messages = {
        "role": "user",
        "content": [
            {"type": "text", "text": "讲一个笑话"},
            {"type": "text", "text": "告诉我未来人工智能是如何发展的"
             }
        ]
    }




    # chatModel.with_structured_output(WeatherInfo)
    promptTemplate.format(question="讲一下关于北京的情况")
    response = chatModel.invoke([messages])
    print("开始调用模型！")
    # modelWithTool = chatModel.bind_tools([getData,saveData])
    # response = modelWithTool.invoke(queryMessage)
    print(f"Model Response: {response}")


def streamCallModel():
    promptTemplate = PromptTemplate.from_template("你好，你的问题是 {question},请告诉我这个问题答案",
                                                  template_format="f-string")

    configInfo = {
        "userId": "test123",
        "threadId": "thread-123456"
    }

    response = chatModel.stream(promptTemplate.format_prompt(question="生成一段100字以内的关于小白兔和大灰狼的故事"),
                                config=configInfo)

    chatModel.astream_events();
    tempStr = ""
    for chunk in response:
        tempStr += chunk.content
        if len(tempStr) > 20:
            print(f"{tempStr}")
            tempStr = ""

    print(f"{tempStr}")


''' 异步事件方式调用 '''
async def anotherEventStream():
    promptTemplate = PromptTemplate.from_template("你好，你的问题是 {question},请告诉我这个问题答案",
                                                  template_format="f-string")
    configInfo = {
        "userId": "test123",
        "threadId": "thread-123456"
    }

    tempStr = ""
    async for event in chatModel.astream_events(promptTemplate.format_prompt(question="生成一段100字以内的关于孔子求学的故事"), config=configInfo):
        if event["event"] == "on_chat_model_start":
            print(f"The input:  {event['data']['input']} ")

        elif event["event"] == "on_chat_model_stream":
            print(f"Token: {event['data']['chunk'].text}")

        elif event["event"] == "on_chat_model_end":
            print(f"Full message: {event['data']['output'].text}")

        else:
            print("Current no data!")
            pass

    # print(f"{tempStr}")


''' 批量调用 '''
def batchQuery():
    # promptTemplate = PromptTemplate.from_template("你好，你的问题是 {question},请告诉我这个问题答案",
    #                                               template_format="f-string")
    configInfo = {
        "userId": "test123",
        "threadId": "thread-123456"
    }
    chatModel.rate_limiter = rateLimit
    model_with_struct = chatModel.with_structured_output(json_schem)
    responses = model_with_struct.batch_as_completed(inputs=["讲一下关于北京的情况","讲一下关于杭州的情况","讲一下关于南京的情况", "讲一下关于上海的情况", "讲一下关于江苏的情况"], config=configInfo)
    for response in responses:
        print(response)


''' 结构化输出数据 '''

class WeatherInfo(BaseModel):
    name: str = Field(description="城市名字", default="")
    weather: str = Field(description="当前城市天气")
    landscape: str = Field(description="当前城市景色")

# json 格式
json_schem = {
    "title": "WeatherInfo",
    "type": "object",
    "description": "存储一个返回的天气信息",
    "properties":{
        "name": {
            "type": "string",
            "description": "城市名字"
        },
        "weather": {
            "type": "string",
            "description": "城市天气情况"
        },
        "landscape": {
            "type": "string",
            "description": "城市景点名字"
        }
    },
    "required": ["name", "weather", "landscape"]
}


if __name__ == "__main__":
    # streamCallModel()
    # asyncio.run(anotherEventStream())
    # time.sleep(10)
    blockCallModel()
    # batchQuery()


