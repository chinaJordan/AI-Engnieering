import os
from util import log
from config import getPgDbConfig, getServerConfig, getAiConfig


API_KEY = "_API_KEY"

if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ.setdefault("DEEPSEEK_API_KEY", "sk-12324u934934898439")


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
