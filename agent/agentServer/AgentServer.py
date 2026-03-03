import os
import re
from typing import Any, List

from langchain.agents import create_agent
from agent.config import EnvConfig

from agent.util import log



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


''' 动态模型示例- 调用方式  '''
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse, dynamic_prompt, \
    HumanInTheLoopMiddleware, InterruptOnConfig, ShellToolMiddleware,HostExecutionPolicy
from pydantic import Field, BaseModel
from agent.tools.AgentTool import getlocation, queryWeather, handleToolError
from agent.tools.ContextInfoStore import ReviewRequest, ReviewResponse, ReviewContxtInfo
from langchain.messages import AIMessageChunk, ToolMessage, AIMessage
from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver

from agent.middletool.TimeStatictisTool import before_model, after_model
from agent.middletool.TheDataTools import saveData, getData
# from agent.middletool import beforeModelReloadMessage, afterProcessMessages
from agent.middletool.tool import filterMessages

from agent.agentServer.model import MODEL_CONTEXT
from agent.config.constant import ConfigConstantKey
from agent.memory.short import CustomAgentState
from agent.agentServer.MultiAgentManager import getCurrentAgent





toolsExe = [getlocation, queryWeather, saveData, getData,filterMessages]

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
    outPut = [format_str_with_adapt(line) for line in lines]
    return "".join(outPut)


def format_str_with_adapt(text:str) -> str:
    '''
    将字符串进行合理的分段和换行，使格式看起来更清晰些
    :param text:
    :return:

    all_match =  r"(?<!^)(?=\s*---\s*|[\u4e00-\u9fa5a-zA-Z0-9，。！？；：,.!?;:【】()（）])"

    only_flag_special_char_match = r"(?<!^)(?=\s*---\s*|\*\*[^*]+\*\*)"

    '''
    pattern = r"(?<!^)(?=\s*---\s*|\*\*[^*]+\*\*|([：:])(\d+\.)|(\d+\.)\s*(\*\*))"
    # 替换：在匹配的位置插入换行符
    formatted_text = re.sub(pattern, "\n", text)
    # 额外清理：多个换行合并为一个，去除首尾空白
    formatted_text = re.sub(r"\n+", "\n", formatted_text).strip()
    return formatted_text

class customAgent(BaseModel):
    useType: str = Field(description="使用的模型类型")
    userId: str = Field(description="用户id")


''' 渲染IA响应消息并打印 '''
def renderMessage(user_id: str, messageModel: str, message: Any) -> None:
    if messageModel == "messages":
        if isinstance(message, AIMessageChunk):
            if message.text:
                print(f"AI message >>: {message.text}", end="|")
            if message.tool_call_chunks:
                print(f"Tool message >>: {message.tool_call_chunks}")

    elif messageModel == "custom":
        print(f"Custom message >>: {message}")
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
                processValue = {**value}
                if isinstance(processValue, dict):
                    processValue.pop("allowAction", False)
                    processValue.pop("description",)
                reviewRequest = ReviewRequest(id=id, actions=value["allowAction"], actionName=value["description"],
                                              content=processValue)
                # reviewRequest = ReviewRequest(actionName=value["review_configs"][0]["action_name"],
                #                               actions=value["review_configs"][0]["allowed_decisions"], id=id,
                #                               content= {k: v for k, v in value.items() if k == "action_requests" } )
                ReviewContxtInfo.putRequest(user_id, id, reviewRequest)
            else:
                print(f"<========> AllResponse: {message} ")


    else:
        raise Exception(f"不支持的消息模式： {messageModel}, 当前合法的参数： 【messages， custom, updates】")


def resumeConversion(reviewRequest: ReviewRequest) -> List[dict[str, Any]]:
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


# customMiddleware = CustomMiddleware(Customstate())
interruptOnConfig = InterruptOnConfig(allowed_decisions=["approve", "reject"],
                                      description="请确认当前请求是允许还是拒绝")


# dynamic_model_select,

# dynamicPrompt
dynamic_agent = create_agent(
    model=MODEL_CONTEXT.get(ConfigConstantKey.DEEPSEEK_CHAT_MODEL),
    middleware=[handleToolError, before_model, after_model,
                HumanInTheLoopMiddleware(interrupt_on={"getlocation": interruptOnConfig}),
                ],
    tools=toolsExe,
    state_schema=CustomAgentState,
    checkpointer=InMemorySaver()
)

def resumeExecute(user_id: str, resumeResponse: list[ReviewResponse]) -> Any:
    if not resumeResponse:
        raise Exception("Resume response can't be null, check if input has any problem!")
    # use_agent = getCurrentAgent(user_id)

    resumeResponseMap = {rsp.id: rsp.model_dump() for rsp in resumeResponse}
    log.info(f"Current user {user_id} resume response is :  {resumeResponseMap}")

    return __resumeRequest(user_id, resumeResponseMap)
    # for streamModel, streamRsp in use_agent.stream(Command(resume=resumeResponseMap), config={"configurable": {"thread_id": "stream-123"}},
    #                  stream_mode=["messages", "updates", "custom"])



'''
    stream message call 
    stream_model: updates, messages, custom
    
'''

def inputMsg(msg: str, user_id: str) -> str:
    if not str or not user_id:
        log.error(f"User input is Empty or user_id is Empty!, please Retry!!")
        return "服务内部出错，请联系管理人员处理！"

    # use_agent = getCurrentAgent(user_id)

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
        "otherInfo": {"time": "2025-12-24", "calss": "CustomState"},
        "user_id": user_id
    }

    return __sendRequest(user_id, messageNew)

    # outPutMessages = []
    # tempMsg = ""
    # customAgent(useType="reasoner", userId="887766433")  context={"useType": "develop", "userId": "h123456"}
    # for streamModel, streamRsp in use_agent.stream(messageNew, config={"configurable": {"thread_id": "stream-123"}},
    #                                                    stream_mode=["messages", "updates", "custom"]
    #                                                    ):
    #     # print(f"Stream model: {streamModel}, Stream response: {streamRsp}")
    #     if streamModel == "messages":
    #         if isinstance(streamRsp, tuple) and len(streamRsp) > 0:
    #             if hasattr(streamRsp[0], "content"):
    #                 tempMsg = streamRsp[0].content
    #                 if tempMsg:
    #                     outPutMessages.append(tempMsg.strip().rstrip("\n").rstrip("\r"))
    #
    #     renderMessage(user_id, streamModel, streamRsp)
    #     tempMsg = None
    # return split_str_by_length("".join(outPutMessages), 50)
    # if len(tempMsg) > 0:
    #     outPutMessages.append(tempMsg)
    #     tempMsg = None

    # decisions = {}
    # for k, v in ReviewContxtInfo.reviewRequestMap.items():
    #     decisions[k] = {
    #         "decisions": resumeConversion(v)
    #     }
    # print(f"Decisons: {decisions}")
    # if decisions and len(decisions) > 0:
    #     for streamModel, streamRsp in use_agent.stream(Command(resume=decisions), config={"configurable": {"thread_id": "stream-123"}},
    #                                                        stream_mode=["messages", "updates", "custom"]):
    #         # print(f"Stream model: {streamModel}, Stream response: {streamRsp}")
    #         if streamModel == "messages":
    #             if isinstance(streamRsp, tuple) and len(streamRsp) > 0:
    #                 if hasattr(streamRsp[0], "content"):
    #                     tempMsg = streamRsp[0].content
    #                     if tempMsg:
    #                         outPutMessages.append(tempMsg.strip().rstrip("\n").rstrip("\r"))
    #         renderMessage(user_id, streamModel, streamRsp)
    #     if len(tempMsg) > 0:
    #         outPutMessages.append(tempMsg)


def __sendRequest(user_id: str, messages: Any)-> Any:
    '''
        发送请求到模型,并返回处理后的数据
    :param user_id:
    :param messages:
    :return:
    '''

    use_agent = getCurrentAgent(user_id);
    outPutMessages = []
    for streamModel, streamRsp in use_agent.stream(messages, config={"configurable": {"thread_id": "stream-123"}},
                                                   stream_mode=["messages", "updates", "custom"]
                                                   ):
        # print(f"Stream model: {streamModel}, Stream response: {streamRsp}")
        if streamModel == "messages":
            if isinstance(streamRsp, tuple) and len(streamRsp) > 0:
                if hasattr(streamRsp[0], "content"):
                    tempMsg = streamRsp[0].content
                    if tempMsg:
                        outPutMessages.append(tempMsg.strip().rstrip("\n").rstrip("\r"))

        renderMessage(user_id, streamModel, streamRsp)
        log.info(f"Current model return data: {outPutMessages}")
    return split_str_by_length("".join(outPutMessages), 50)



def __resumeRequest(user_id: str, message: Any)->Any:
    '''
    中断后恢复执行的model 调用， 将输入的消息作为中断的响应传递给中断，让 agent 继续从中断处继续执行。
    :param user_id: 当前的用户ID
    :param message: 恢复执行传入的消息
    :return:
    '''
    use_agent = getCurrentAgent(user_id);
    outPutMessages = []
    for streamModel, streamRsp in use_agent.stream(Command(resume=message), config={"configurable": {"thread_id": "stream-123"}},
                                                   stream_mode=["messages", "updates", "custom"]
                                                   ):
        # print(f"Stream model: {streamModel}, Stream response: {streamRsp}")
        if streamModel == "messages":
            if isinstance(streamRsp, tuple) and len(streamRsp) > 0:
                if hasattr(streamRsp[0], "content"):
                    tempMsg = streamRsp[0].content
                    if tempMsg:
                        outPutMessages.append(tempMsg.strip().rstrip("\n").rstrip("\r"))

        renderMessage(user_id, streamModel, streamRsp)
        log.info(f"Current resume model return data: {outPutMessages}")
    return split_str_by_length("".join(outPutMessages), 50)



''' 一些特定使用的middleware 工具 '''
hostCommandMiddleware = ShellToolMiddleware(workspace_root="/opt", execution_policy=HostExecutionPolicy(),
                                            startup_commands=["echo 'Please count the times have used!'"], shell_command="/bin/sh")

# 动态提示词
# @dynamic_prompt
# def dynamicPrompt(request: ModelRequest) -> str:
#     print(f"Current request: {request.runtime.context}")
#     useType = "chat"
#     if useType == "reasoner":
#         return f"你是一位非常厉害的助手，可以详细讲解执行的每一步原理及过程。"
#     else:
#         return f"你是一位厉害的助手，可以返回正确的信息并以良好的格式展示结果"


# @wrap_model_call
# def dynamic_model_select(request: ModelRequest, handle) -> ModelResponse:
#     """根据输入信息的长度和要求，选择合适的模型"""
#     # print(f"ModelRequest: {request}， handle: {handle} ")
#     length = len(request.messages[-1].content)
#     model = MODEL_CONTEXT.get(ConfigConstantKey.DEEPSEEK_CHAT_MODEL)
#
#     customAgent = request.runtime.context;
#     print(f"userId: {customAgent.userId}, useType: {customAgent.useType},")
#     useType = customAgent.useType
#     if length > 50 and useType == "reasoner":
#         model = MODEL_CONTEXT.get(ConfigConstantKey.DEEPSEEK_REASONER_MODEL)
#     return handle(request.override(model=model))

if __name__ == "__main__":
    temptext = "**乾隆与纪晓岚斗智故事**乾隆好以文采权术考验臣子，纪晓岚以机敏应对，留下轶事：1. **巧解“老头子”**：纪晓岚因称乾隆“老头子”被问罪，他机智解释“老”为万岁、“头”为万民之首、“子”为天之骄子，乾隆转怒为喜。2. **茶隐讽贪**：乾隆赐茶时暗指收礼之风，纪晓岚以“只收清水茶礼”自辩清廉，巧妙表忠心。3. **修书机锋**：编纂《四库全书》时，乾隆质疑前朝边患记载，纪晓岚以“存史显本朝太平”平衡史料与政治需求。这些故事多源于野史演绎，历史上纪晓岚更偏文学侍从，君臣“斗智”实为默契互动——纪晓岚以幽默化解困局，乾隆借机敲打臣子。---**2025年国际大事总结**1. **政治安全**：多国大选影响格局；俄乌僵持、中东紧张、朝韩对峙持续。2. **经济科技**：全球经济复苏不均，金砖国家推本币结算；AI治理与太空竞赛加剧。3. **气候能源**：COP30气候大会召开，极端天气频发；可再生能源投资增长，关键矿产竞争激烈。4. **公共卫生与社会**：WHO大流行病协议谈判推进；老龄化与AI就业冲击引关注。5. **中国角色**：推动“一带一路”高质量发展，在中美博弈中寻求有限合作。特点：多极化加速、技术双刃剑效应凸显、全球治理不确定性突出。---**春天写生故事**美院教授林墨与旧友周明远在桃花溪写生重逢。林墨画春光生机，周明远画凋零沉郁，因周母去世、林父离世，二人对春天感悟迥异。最终他们修改彼此画作，融合新生与逝去，达成理解：春天承载时光的痕迹，让观者看见生命的倒影。---**动物笑话**一只蜗牛骑龟背上，龟嫌慢催它快些。蜗牛怒道：“闭嘴！再催我就刹车了！”好的，这里有一个经典的脑筋急转弯：---**问题：**什么东西你越给它，它反而变得越少？（请先思考一下，再看答案哦！）---**答案：****“洞”**（或者“缺口”）。——因为“给”一个洞填补东西（比如土、水），洞的空间就会减少。"
    proceestr = format_str_with_adapt(temptext)
    print(f"Format str: {proceestr}")
    # userMessage = ""
    # while True:
    #     message = input("请输入你的内容：退出输入： 【'exit','q', 'Q','quit'】")
    #     if message in ["exit","q", "Q","quit"]:
    #         print(f"System exit 0!")
    #         break
    #     userMessage = userMessage + message.strip()
    #     resp = inputMsg(userMessage)
    #     resp = split_str_by_length("".join(resp),50)
    #     print(f"AI respoonse: {resp}")
    # pass
