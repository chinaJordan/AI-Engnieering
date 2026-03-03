from typing import  Any
from typing_extensions import override

from langchain.agents.middleware import AgentMiddleware
from langgraph.runtime import Runtime

from agent.memory.short import CustomAgentState
from agent.util import log,putValue,getValue



class StateManegerMiddleware(AgentMiddleware):

    @override
    def before_agent(self, state: CustomAgentState, runtime: Runtime) -> dict[str, Any] | None:
        log.info(f"Current agent state: {state}, Current runtime : {runtime}")
        
        user_id = state.user_id
        if not user_id:
            log.error(f"Can't get current user_id in conversation! Please check param is correct!")
