import os
from agent.util import log
from agent.config import getPgDbConfig, getServerConfig, getAiConfig


API_KEY = "_API_KEY"

# 模拟 key:  sk-12423jkdjfkjdjgfk343
if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ.setdefault("DEEPSEEK_API_KEY", "sk-642839b326e34ba19a8149815e9ec60b")


def initConfig():
    pgDbConfig = getPgDbConfig()
    aiModelConfig = getAiConfig()
    for aimodelinfo in aiModelConfig.ai:
        if not aimodelinfo.apikey:
            apikey = os.environ.get(aimodelinfo.type.upper() + API_KEY)
            if not apikey:
                raise Exception(f"Ai model apiKey must config! Model name: {aimodelinfo.name} !")
            aimodelinfo.apikey = apikey

    serverConfig = getServerConfig()
    log.debug(f"Load config success! pgConfig: {pgDbConfig},  aiConfig: {aiModelConfig}, serverConfig: {serverConfig}")
