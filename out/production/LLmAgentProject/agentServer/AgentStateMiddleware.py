from langchain.agents.middleware import AgentState,AgentMiddleware
from typing import Any


class CustomeStats(AgentState):
    otherInfo: dict


class CustomMiddleware(AgentMiddleware):
    state_schema = CustomeStats

    def before_model(self, state: CustomeStats, runtime) -> dict[str, Any] | None:
        print(f"State: {state}, Runtime: {runtime}")
