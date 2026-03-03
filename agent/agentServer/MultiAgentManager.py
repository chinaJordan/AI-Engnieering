from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import InMemorySaver

from langchain.agents import create_agent

import threading

from agent.util import getValue, putValue, log
from agent.agentServer.model import MODEL_CONTEXT
from agent.middletool import TimeStatictisTool, beforeModelReloadMessage, afterProcessMessages
from agent.middletool.AgentToolDefine import testCallPhone, testSendEmail

SHARE_TOOLS = [testCallPhone, testSendEmail]
SHARE_MIDLEWARES = [TimeStatictisTool.before_model, TimeStatictisTool.after_model, beforeModelReloadMessage, afterProcessMessages]

__lock = threading.Lock()

def getCurrentAgent(user_id: str) -> CompiledStateGraph:
    if not user_id:
        raise Exception("user_id can't be None, please input the user_id!!")
    graph_state = getValue(user_id)
    if not graph_state:
        newAgent = crateAgent(user_id)
        putValue(user_id, newAgent)
        log.debug(f"Current user_id: {user_id}, create new agent: {newAgent}")
        return newAgent
    # if isinstance(graph_state, CompiledStateGraph):
    log.info(f"Current user_id {user_id} use cached Agent!")
    return graph_state


def crateAgent(user_id: str, model_name="deepseek-chat") -> CompiledStateGraph:
    """
    create new agent, Thread safe.
    if lock success, then again check the agent exists, if exist return, else create new Agent
    :param user_id:
    :return:
    """

    __lock.acquire()
    try:
        graph_state = getValue(user_id)
        if graph_state:
            return graph_state

        newAgent = create_agent(
            model=MODEL_CONTEXT.get(model_name),
            tools=SHARE_TOOLS,
            middleware=SHARE_MIDLEWARES,
            checkpointer=InMemorySaver(),
        )
    finally:
        __lock.release()

    return newAgent
