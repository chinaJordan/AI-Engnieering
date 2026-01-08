from typing import Any

from langchain.agents.middleware import before_model
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from langchain.messages import RemoveMessage

from langgraph.graph.message import REMOVE_ALL_MESSAGES


@before_model
def trimMessage(state: AgentState, runtime: Runtime)-> dict[str,Any] | None:
    """ 对当前会话消息进行裁剪，只保留最新的6轮对话信息 """
    print(f"Current agentState: {state}, Runtime: {runtime}")

    print(f"Current messges total num: {len(state['messages'])}")
    currentMsgs = state.get("messages", None)
    if not currentMsgs:
        print(f"Current have no messages! Don't need to do any thing!")
        return None
    msglen = len(currentMsgs)
    if msglen > 20:
        fisrtMessage = currentMsgs[0]
        newMsgs = [fisrtMessage]
        newMsgs.append(currentMsgs[-5:])
    else:
        return None
    return {
        "messages":[
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *newMsgs
        ]
    }


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



