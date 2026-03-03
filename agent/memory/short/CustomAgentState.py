from langchain.agents import AgentState

from typing import NotRequired


class CustomAgentState(AgentState):
    user_id: str
    message_len: NotRequired[int]
    extra_val: NotRequired[dict]

    @classmethod
    def getNewInstance(cls, state: AgentState) -> "CustomAgentState":
        if not state:
            return CustomAgentState(user_id=None, message_len=None, extra_val=None)

        if isinstance(state, CustomAgentState):
            return CustomAgentState(user_id=state.user_id, message_len=state.message_len,
                                    extra_val={k: v for k, v in state.extra_val.items() if state.extra_val},
                                    messages=[msg for msg in state.messages if state.messages],
                                    jump_to=state.jump_to, structured_response=state.structured_response)

        else:
            return CustomAgentState(messages=[msg for msg in state.messages if state.messages],
                                    jump_to=state.jump_to, structured_response=state.structured_response)