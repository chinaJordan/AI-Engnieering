from typing import Any

from langchain.agents.middleware import AgentState, AgentMiddleware, before_model

from agent.util import log
from agent.agentServer.model import MODEL_CONTEXT

class CustomeStats(AgentState):
    use_model: str
    otherInfo: dict


class CustomMiddleware(AgentMiddleware):
    state_schema = CustomeStats


@before_model()
def dynamicModelChoose(state: CustomeStats, runtime) -> dict[str,Any]:
    if not state:
        return None

    use_model = state["use_model"]
    currentModel = MODEL_CONTEXT.get(use_model)
    if not currentModel:
        log.info(f"Can't find model name: {use_model}, use default Model!")
        currentModel = next(iter(MODEL_CONTEXT.values()))
    log.info(f"Current use model: {currentModel}")

    return {
        "model": currentModel
    }

if __name__ == "__main__":
    currentModel = dynamicModelChoose(state=CustomeStats(use_model="open-ai"), runtime=None)
    log.info(f"find model info: {currentModel}")

