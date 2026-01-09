import os
import re
from typing import Any, List

from langchain.agents import create_agent

# from agentServer.AgentStateMiddleware import CustomMiddleware
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

print(f"Current ENV : {os.environ.get('profile')}")

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
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse, dynamic_prompt, \
    HumanInTheLoopMiddleware, InterruptOnConfig, ShellToolMiddleware,HostExecutionPolicy
from pydantic import Field, BaseModel
from agent.tools.AgentTool import getlocation, queryWeather, handleToolError
from agent.tools.ContextInfoStore import ReviewRequest, ReviewResponse, ReviewContxtInfo
from langchain.messages import AIMessageChunk, ToolMessage, AIMessage
from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver

from agent.middletool.TimeStatictisUtil import before_model, after_model
from agent.middletool.TheDataTools import saveData, getData
from agent.middletool.MessageContextProcess import trimMessage



deepSeekChatModel = ChatDeepSeek(model="deepseek-chat")
deepSeekReasonerModel = ChatDeepSeek(model="deepseek-reasoner")

messageNew = {
    "messages": [
        {
            "role": "user",
            "content": "查询北京的位置信息，并查询杭州的天气情况, 并在执行前执行脚本 "
        }
    ],
    "otherInfo": {"time": "2025-12-24", "calss": "CustomState"}
}

saveMesage = {
    "messages": [{"role": "user",
                  "content": "Save the following user: userId: abc123, name: Foo, age: 25, email: foo@langchain.dev"}]
}

queryMessage = {
    "messages": [{"role": "user", "content": "Get user info for user with id 'abc123'"}]
}

toolsExe = [getlocation, queryWeather, saveData, getData]

interupts = []


def split_str_by_length(text: str, line_len: int) -> str:
    """
    按照固定长度拆分每行数据，兼容中英文混合
    :param text:
    :param line_len:
    :return:
    """
    if not text:
        return ""
    # 通过正则表达式来进行分割，兼容完全没有明显分割的场景
    pattern = rf'.{{1,{line_len}}}(?=[\s，。！？；：,.!?;:]|$|(?<=[a-zA-Z])(?=[\u4e00-\u9fa5])|(?<=[\u4e00-\u9fa5])(?=[a-zA-Z]))'
    lines = [line.strip() for line in re.findall(pattern, text) if line.strip()]
    return ''.join(lines)

class customAgent(BaseModel):
    useType: str = Field(description="使用的模型类型")
    userId: str = Field(description="用户id")


''' 渲染IA响应消息并打印 '''
def renderMessage(messageModel: str, message: Any) -> None:
    if messageModel == "messages":
        if isinstance(message, AIMessageChunk):
            if message.text:
                print(f"{message.text}", end="|")
            if message.tool_call_chunks:
                print(f"{message.tool_call_chunks}")

    elif messageModel == "custom":
        print(f"{message}")
    elif messageModel == "updates":
        for model, msg in message.items():
            if model in ("model", "tools"):
                if isinstance(msg, ToolMessage):
                    print(f"Tool Response: {msg.content_blocks}")
                elif isinstance(msg, AIMessage) and msg.tool_calls:
                    print(f"Tool Call: {msg.tool_calls}")
            elif model == "__interrupt__":
                print(f"===== interrupt:   {msg}")
                value = msg[0].value
                id = msg[0].id
                reviewRequest = ReviewRequest(actionName=value["review_configs"][0]["action_name"],
                                              actions=value["review_configs"][0]["allowed_decisions"], id=id,
                                              content= {k: v for k, v in value.items() if k == "action_requests" } )
                ReviewContxtInfo.putRequest(id, reviewRequest)
            else:
                print(f"<========> AllResponse: {message} ")


    else:
        raise Exception(f"不支持的消息模式： {messageModel}, 当前合法的参数： 【messages， custom, updates】")


def resumeConversion(reviewRequest: ReviewRequest) -> List[dict[str,Any]]:
    if not ReviewContxtInfo.reviewRequestMap:
        return []
    return [
        {
            "type": "edit",
            "edited_action": {

            }
        }
        if "请求或者拒绝" in value["description"]
        else {
            "type": "approve"
        }
        for value in reviewRequest.content["action_requests"]

    ]







# 动态提示词
@dynamic_prompt
def dynamicPrompt(request: ModelRequest) -> str:
    print(f"Current request: {request.runtime.context}")
    useType = "chat"
    if useType == "reasoner":
        return f"你是一位非常厉害的助手，可以详细讲解执行的每一步原理及过程。"
    else:
        return f"你是一位厉害的助手，可以返回正确的信息并以良好的格式展示结果"


@wrap_model_call
def dynamic_model_select(request: ModelRequest, handle) -> ModelResponse:
    """根据输入信息的长度和要求，选择合适的模型"""
    # print(f"ModelRequest: {request}， handle: {handle} ")
    length = len(request.messages[-1].content)
    model = deepSeekChatModel

    customAgent = request.runtime.context;
    print(f"userId: {customAgent.userId}, useType: {customAgent.useType},")
    useType = customAgent.useType
    if length > 50 and useType == "reasoner":
        model = deepSeekReasonerModel
    return handle(request.override(model=model))


# customMiddleware = CustomMiddleware(Customstate())
interruptOnConfig = InterruptOnConfig(allowed_decisions=["approve", "reject"],
                                      description="请确认当前请求是允许还是拒绝")

''' 一些特定使用的middleware 工具 '''
hostCommandMiddleware = ShellToolMiddleware(workspace_root="/opt", execution_policy=HostExecutionPolicy(),
                        startup_commands=["echo 'Please count the times have used!'"], shell_command="/bin/sh")


# dynamic_model_select,

dynamic_agent = create_agent(
    model=deepSeekChatModel,
    middleware=[ handleToolError, trimMessage, dynamicPrompt, before_model, after_model,
                HumanInTheLoopMiddleware(interrupt_on={"getlocation": interruptOnConfig}),
                ],
    tools=toolsExe,
    checkpointer=InMemorySaver()
)

''' 普通阻塞式调用 '''
# results = dynamic_agent.invoke(messageNew, system_prompt="You are a helpful assistant",
#                                context=customAgent(useType="reasoner", userId="887766433"))
# print(f"Agent execute result:  {results['messages'][-1].pretty_print()}")

'''
    stream message call 
    stream_model: updates, messages, custom
    
'''

def inputMsg(msg: str) -> str:
    if not str:
        print(f"User input is Empty, use defalut input!")

    messageNew = {
        "messages": [
            {
                "role": "system",
                "content": "你是一个非常棒的助手，擅长处理各种复杂问题，能够独立分析问题和解决问题，尤其擅长进行各种工具调用，以及 \
                           进行各种校验和核对，你应该基于真实信息进行回复，如果获取不到，请主动告诉用户不擅长，不要随便胡乱回复，以及执行没有经过审核\
                           的危险动作！"
            },
            {
                "role": "user",
                "content": msg
            }
        ],
        "otherInfo": {"time": "2025-12-24", "calss": "CustomState"}
    }
    outPutMessages = []
    tempMsg = ""

    # customAgent(useType="reasoner", userId="887766433")
    for streamModel, streamRsp in dynamic_agent.stream(messageNew, config={"configurable": {"thread_id": "stream-123"}},
                                                       stream_mode=["messages", "updates", "custom"],
                                                       context={"useType":"develop", "userId": "h123456"}):
        # print(f"Stream model: {streamModel}, Stream response: {streamRsp}")
        if streamModel == "messages":
            if isinstance(streamRsp, tuple) and len(streamRsp) > 0:
                if hasattr(streamRsp[0], "content"):
                    tempMsg = streamRsp[0].content
                    if tempMsg:
                        outPutMessages.append(tempMsg.strip().rstrip("\n").rstrip("\r"))

        renderMessage(streamModel, streamRsp)
    if len(tempMsg) > 0:
        outPutMessages.append(tempMsg)

    decisions = {}
    for k, v in ReviewContxtInfo.reviewRequestMap.items():
        decisions[k] = {
            "decisions": resumeConversion(v)
        }
    print(f"Decisons: {decisions}")
    if decisions and len(decisions) > 0:
        for streamModel, streamRsp in dynamic_agent.stream(Command(resume=decisions), config={"configurable": {"thread_id": "stream-123"}},
                                                           stream_mode=["messages", "updates", "custom"]):
            # print(f"Stream model: {streamModel}, Stream response: {streamRsp}")
            if streamModel == "messages":
                if isinstance(streamRsp, tuple) and len(streamRsp) > 0:
                    if hasattr(streamRsp[0], "content"):
                        tempMsg = streamRsp[0].content
                        if tempMsg:
                            outPutMessages.append(tempMsg.strip().rstrip("\n").rstrip("\r"))
            renderMessage(streamModel, streamRsp)
        if len(tempMsg) > 0:
            outPutMessages.append(tempMsg)
    return split_str_by_length("".join(outPutMessages),50)

if __name__ == "__main__":
    userMessage = ""
    while True:
        message = input("请输入你的内容：退出输入： 【'exit','q', 'Q','quit'】")
        if message in ["exit","q", "Q","quit"]:
            print(f"System exit 0!")
            break
        userMessage = userMessage + message.strip()
        resp = inputMsg(userMessage)
        resp = split_str_by_length("".join(resp),50)
        print(f"AI respoonse: {resp}")
    pass
