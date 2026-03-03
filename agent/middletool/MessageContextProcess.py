import json
from typing import Any, cast

from langchain.agents.middleware import before_model, after_model
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from langchain.messages import RemoveMessage, SystemMessage, HumanMessage, AIMessage

from langgraph.graph.message import REMOVE_ALL_MESSAGES

from agent.util import log, getValue, putValue
from agent.config.constant import ConfigConstantKey
from agent.agentServer.model import MODEL_CONTEXT
from agent.agentServer.store.default import DefaultTemporaryStore

from agent.prompt import summarizeMsgPrompt


TEMP_STORE = DefaultTemporaryStore()

# 预定义常量
DEFAULT_MAG_LEN = 20
# 默认消息大小不超过20K
DEFAULT_MSG_SIZE = 20 * 1024

# 默认当前上下文消息过期时间，默认一天，单位： 秒
DEFAULT_EXPIRE_TIME = 3600 * 24


@before_model
def trimMessage(state: AgentState, runtime: Runtime)-> dict[str,Any] | None:
    """ 对当前会话消息进行裁剪，只保留最新的6轮对话信息 """
    log.info(f"Current agentState: {state}, Runtime: {runtime}")

    log.info(f"Current messges total num: {len(state['messages'])}")
    currentMsgs = state.get("messages", None)
    if not currentMsgs:
        log.info(f"Current have no messages! Don't need to do any thing!")
        return None
    msglen = len(currentMsgs)
    if msglen > 6:
        fisrtMessage = currentMsgs[0]
        newMsgs = [fisrtMessage]
        newMsgs.append(currentMsgs[-5:])
    else:
        return None
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *newMsgs
        ]
    }

@before_model
def summarizeMesaage(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    '''
        对当前会话进行总结，如果当前会话消息轮次超过6轮，则会将除了第一条和最后一条的消息进行总结
    '''
    messages = state.get("messages", None)
    log.info(f"Current messages length: {len(messages)}")
    if not messages:
        return None

    if len(messages) < 6:
        return None
    log.info(f"Messages len great than 6, need to summarize message!")

    try:
        summarize_model = MODEL_CONTEXT.get("deepseek-chat")
        if not summarize_model:
            log.info(f"Can't find model : deepseek-chat, use default model!")
            summarize_model = next(iter(MODEL_CONTEXT.values()))

        newMessages = messages[0:1]

        content = ",".join(m.content for m in messages[1:-1])
        input = [
            SystemMessage(content="总结以下的输入内容，在保证语义和内容完整的情况下，用尽可能少的文字进行描述"),
            HumanMessage(content=content)
        ]
        log.info(f"Current model: {summarize_model}, current messages: {input}")
        summarize_msg = summarize_model.invoke(input)
        log.info(f"Model summarize finish, finall message: {summarize_msg}")

        newMessages.append(summarize_msg)
        newMessages.append(messages[-1:][0])
        log.info(f"After process return messages, the newMessages: {newMessages}")
    except Exception as e:
        log.error(f"Summarize messages Fail! exception: {e}")
        return None

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *newMessages
        ]
    }

@before_model
def beforeModelReloadMessage(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    '''
        执行模型调用前，从临时缓存中新加载用户消息到当前会话中
        :param state:
        :param runtime:
        :return:
    '''
    user_id = getValue(ConfigConstantKey.USER_ID)
    current_user_history_msg = TEMP_STORE.query(user_id)
    log.info(f"Current user_id {user_id} history messages is: {current_user_history_msg}")

    if not current_user_history_msg:
        return

    current_input = state["messages"]
    log.info(f"Current agent input messages: {current_input}, user_id: {user_id}")
    cast("list", current_user_history_msg).append(current_input[-1])
    state["messages"] = current_user_history_msg
    # return {
    #     "messages": [
    #         RemoveMessage(id=REMOVE_ALL_MESSAGES),
    #         *current_user_history_msg
    #     ]
    # }


@after_model
def afterProcessMessages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    messages = state["messages"]
    user_id = getValue(ConfigConstantKey.USER_ID)
    if not user_id:
        log.info(f"Context info not have user_id, please check user_id is correct set!")
        raise Exception("Context info can't find user_id info!")

    history_messages = TEMP_STORE.query(user_id)
    try:
        need_process_msg = []
        if not history_messages:
            # 当前消息没有存储或者已经过期
            needProcess = chargeMessagesNeedProcess(history_message=None, newMessages=messages)
            if not needProcess:
                TEMP_STORE.insertByTimeout(user_id, DEFAULT_EXPIRE_TIME, messages)
                return
            else:
                lastMsg = messages[-1]
                need_process_msg = messages[:-1]

        else:
            needProcess = chargeMessagesNeedProcess(history_message=history_messages, newMessages=messages)
            if not needProcess:
                cast("list", history_messages).append(messages[-1])
                TEMP_STORE.insertByTimeout(user_id, DEFAULT_EXPIRE_TIME, history_messages)
                log.info(f"当前消息不需要进行处理，user_id： {user_id}, 当前消息条数； {len(history_messages)}")
                return
            else:
                lastMsg = messages[-1]
                # cast(list, history_messages).append(messages[:-1])
                need_process_msg = history_messages

        summarize_model = MODEL_CONTEXT.get("deepseek-chat")
        if not summarize_model:
            log.info(f"Can't find model : deepseek-chat, use default model!")
            summarize_model = next(iter(MODEL_CONTEXT.values()))

        # content = summarizeMsgPrompt(content="")
        system_msg = SystemMessage(content="请将以下内容进行总结，要求总结后内容足够精炼，简短，同时又不失去关键信息和原有意思，总结后尽可能将相关的内容放在一起。")
        user_msg = HumanMessage(content=__convertObjectToStr(need_process_msg))
        log.info(f"Current model: {summarize_model}, current messages: {user_msg}")
        summarize_msg = summarize_model.invoke([system_msg, user_msg])
        log.info(f"Model summarize finish, finall message: {summarize_msg}")

        new_msg = [messages[0],summarize_msg]
        new_msg.append(lastMsg)
        TEMP_STORE.insertByTimeout(user_id, DEFAULT_EXPIRE_TIME, new_msg)
        log.info(f"User_id: {user_id} , After summarize, the save new msg is: {new_msg}")

    finally:
        # 清空当前会话的所有消息，后续的会话内容从缓存中加载
        log.info(f"After model process End! User_id: {user_id}")
        # return {
        #     "messages": [
        #         RemoveMessage(id=REMOVE_ALL_MESSAGES)
        #     ]
        # }



def chargeMessagesNeedProcess(history_message: list, newMessages: list) -> bool:
    '''
        根据输入的历史消息和当前新的消息，判断是否需要对当前的会话消息进行处理
        处理规则：
            如果消息跳过超过20 条，则进行处理
            如果消息总的大小超过20K，需要进行处理
    :param history_message:
    :param newMessages:
    :return:
    '''
    if not history_message:
        if not newMessages:
            return False

        msg_len = len(newMessages)
        if msg_len > DEFAULT_MAG_LEN:
            log.info(f"当前会话消息超过了默认的消息大小，需要进行处理！ 当前用户：{getValue(ConfigConstantKey.USER_ID)}, 当前消息大小： {msg_len} ")
            return True

        byte_size = len(str(newMessages).encode("utf-8"))
        if byte_size > DEFAULT_MSG_SIZE:
            log.info(f"当前会话消息大小： {byte_size} byte, 已经超过默认的字节数大小，需要进行处理！ user_id; {getValue(ConfigConstantKey.USER_ID)}")
            return True
    else:
        total_len = len(history_message) + len(newMessages)
        if total_len > DEFAULT_MAG_LEN:
            log.info(f"当前会话消息超过了默认的消息大小，需要进行处理！ 当前用户：{getValue(ConfigConstantKey.USER_ID)}, 当前消息大小： {total_len} ")
            return True

        byte_size = len(str(newMessages).encode("utf-8")) + len(str(history_message).encode("utf-8"))
        if byte_size > DEFAULT_MSG_SIZE:
            log.info(f"当前会话消息大小： {byte_size} byte, 已经超过默认的字节数大小，需要进行处理！ user_id; {getValue(ConfigConstantKey.USER_ID)}")
            return True

    return False


def __convertObjectToStr(messages: list) -> str:
    '''
    将传入的消息进行处理，解析出里面的content 字段，将组装后的字符串返回。
    如果出入空，则返回 None
    :param messages:
    :return:
    '''
    if not messages:
        return None

    result = ""
    # template_str = '''
    #     {
    #         "role": %s,
    #         "content": %s
    #     }
    # '''
    iteroter = iter(messages)
    while msg := next(iteroter, None):
        match msg:
            case HumanMessage():
                result += msg.content
            case AIMessage():
                result +=  msg.content
            case _:
                log.info(f"No match message!")

    return result







@before_model
def removeMessage(state: AgentState, runtime: Runtime)-> dict[str,Any] | None:
    """ 对当前会话消息进行裁剪，只保留最新的2轮对话信息 """
    print(f"Current messges total num: {len(state['messages'])}")
    currentMsgs = state.get("messages", None)
    if not currentMsgs:
        print(f"Current have no messages! Don't need to do any thing!")
        return None
    msglen = len(currentMsgs)
    if msglen > 4:
        return {
            "messages": [RemoveMessage(id=m.id) for m in currentMsgs[:2]]
        }
    else:
        return None


if __name__ == "__main__":
    strText = "你好，请问你叫什么名字？"
    print(f"Bytes: {len(strText.encode('utf-8'))}")

    msgs = [
        "你好，我是小花朵",
        "今天，天气真不错，可以去散步了！"
    ]

    # size = asizeof.asizeof(msgs, align=2)
    print(f"Asize of array compute : {1}")

