
import os

# os.environ.setdefault("profile", "dev")
from langchain.agents import create_agent

from agentServer.AgentStateMiddleware import CustomMiddleware
from config import global_config
from langchain_deepseek import ChatDeepSeek

'''
    # 模型初始化，模型可以和执行解耦，支持动态和静态模型
    example: 
        静态模型：
            在创建 agent时，直接传入模型，在整个执行期间模型不能改变
            agent = create_agent("deepseek-chat")
            
        动态模型：
            在创建agent 时，可以指定模型，或者不指定模型，通过中间件的方式在运行时动态选择
            合适的模型。
            
'''

print(f"Current ENV : {global_config.ENV}")

# 静态模型示例
# agent = create_agent("deepseek-chat")
# message = {
#     "messages": [
#         {
#             "role": "user",
#             "content": "tell me your name"
#         }
#     ]
# }
#
#
# results = agent.invoke(message, system_prompt="You are a helpful assistant")
# print(f"Agent execute result:  {results['messages'][-1]}")

''' 动态模型示例- 调用方式  '''
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse, dynamic_prompt
from pydantic import Field, BaseModel
from tools.AgentTool import getlocation,queryWeather,handleToolError
from middletool.TimeStatictisUtil import before_model, after_model
from middletool.TheDataTools import saveData,getData



deepSeekChatModel = ChatDeepSeek(model="deepseek-chat")
deepSeekReasonerModel = ChatDeepSeek(model="deepseek-reasoner")

messageNew = {
    "messages": [
        {
            "role": "user",
            "content": "查询北京的位置信息，并查询杭州的天气情况？ "
        }
    ],
    "otherInfo": {"time": "2025-12-24", "calss": "CustomState"}
}

saveMesage ={
    "messages": [{"role": "user", "content": "Save the following user: userId: abc123, name: Foo, age: 25, email: foo@langchain.dev"}]
}

queryMessage = {
    "messages": [{"role": "user", "content": "Get user info for user with id 'abc123'"}]
}

toolsExe = [getlocation, queryWeather,saveData,getData]

class customAgent(BaseModel):
    useType: str = Field(description="使用的模型类型")
    userId: str = Field(description="用户id")


# 动态提示词
@dynamic_prompt
def dynamicPrompt(request: ModelRequest) -> str:
    useType = request.runtime.context.useType
    if useType == "reasoner":
        return f"你是一位非常厉害的助手，可以详细讲解执行的每一步原理及过程。"
    else :
        return f"你是一位厉害的助手，可以返回正确的信息并以良好的格式展示结果"


@wrap_model_call
def dynamic_model_select(request: ModelRequest, handle) -> ModelResponse:
    """根据输入信息的长度和要求，选择合适的模型"""
    print(f"ModelRequest: {request}， handle: {handle} ")
    length = len(request.messages[-1].content)
    model = deepSeekChatModel

    customAgent = request.runtime.context;
    print(f"userId: {customAgent.userId}, useType: {customAgent.useType},")
    useType = customAgent.useType
    if length > 50 and useType == "reasoner":
        model = deepSeekReasonerModel
    return handle(request.override(model=model))


# customMiddleware = CustomMiddleware(Customstate())
dynamic_agent = create_agent(
    model=deepSeekChatModel,
    middleware=[dynamic_model_select, handleToolError, dynamicPrompt, before_model, after_model],
    tools=toolsExe
)

results = dynamic_agent.invoke(saveMesage, system_prompt="You are a helpful assistant",
                               context=customAgent(useType="reasoner", userId="887766433"))
print(f"Agent execute result:  {results['messages'][-1]}")

if __name__ == "__main__":
    pass
