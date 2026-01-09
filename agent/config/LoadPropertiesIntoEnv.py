from agent.util import log
import os
from typing import Any
from agent.util import loadYamlFile, readPropertyFile

from agent.config import AIModelConfigDTO, PgDBConfig, ServerConfigDTO

DEFAULT_PROFILE_CONFIG = "resource/application"

PARENT_PATH = "resource/"
YAML_SUFFIX = ".yaml"
PROPERTIES_SUFFIX = ".properties"

""" 配置变量名 """
SERVER_KEY = "server"
AI_KEY = "ai"
PG_DB_KEY = "postgresql"


#  存储当前加载到环境的配置
CURRENT_CONTEXT_CONFIG: dict[str, Any] = {}


def loadProperties(filetype=".yaml"):
    global CURRENT_CONTEXT_CONFIG
    loadYamlContent = None
    propertiesLoadContent = None

    if not filetype:
        filetype = YAML_SUFFIX
    profile = os.environ.get("profile") if os.environ.get("profile") else None
    if not profile:
        currentProfileName = DEFAULT_PROFILE_CONFIG + filetype
    else:
        currentProfileName = DEFAULT_PROFILE_CONFIG + "-" + profile + filetype
    log.info(f"Current load profile name : {currentProfileName}, Ready to load !")

    if filetype == YAML_SUFFIX:
        # 通过yaml 文件加载
        loadYamlContent = loadYamlFile(currentProfileName)
        log.debug(f"Load yaml content: {loadYamlContent}")
    elif filetype == PROPERTIES_SUFFIX:
        propertiesLoadContent = readPropertyFile(None,currentProfileName)
        log.debug(f"Load properties content: {propertiesLoadContent}")
    else:
        raise Exception("Not support file type, current support config file type: [.yaml, .yml, .properties] !")


    # 初始化配置
    try:
        if loadYamlContent:
            aiModelConfig = AIModelConfigDTO.model_validate(loadYamlContent)
            if not aiModelConfig:
                raise Exception("AI config can't be null!")
            CURRENT_CONTEXT_CONFIG.setdefault(AI_KEY, aiModelConfig)

            serverConfig = ServerConfigDTO.model_validate(loadYamlContent)
            if not serverConfig:
                raise Exception("Server config can't be null!")
            CURRENT_CONTEXT_CONFIG.setdefault(SERVER_KEY, serverConfig)

            pgdbConfig = PgDBConfig.model_validate(loadYamlContent)
            if not pgdbConfig:
                raise Exception("Postgresql config can't be null!")
            CURRENT_CONTEXT_CONFIG.setdefault(PG_DB_KEY, pgdbConfig)

        elif propertiesLoadContent:
            aiModelConfig = AIModelConfigDTO.model_validate(propertiesLoadContent)
            if not aiModelConfig:
                raise Exception("AI config can't be null!")
            CURRENT_CONTEXT_CONFIG.setdefault(AI_KEY, aiModelConfig)

            serverConfig = ServerConfigDTO.model_validate(propertiesLoadContent)
            if not serverConfig:
                raise Exception("Server config can't be null!")
            CURRENT_CONTEXT_CONFIG.setdefault(SERVER_KEY, serverConfig)

            pgdbConfig = PgDBConfig.model_validate(propertiesLoadContent)
            if not pgdbConfig:
                raise Exception("Postgresql config can't be null!")
            CURRENT_CONTEXT_CONFIG.setdefault(PG_DB_KEY, pgdbConfig)
        else:
            raise Exception(f"Load config from file: {currentProfileName} is null, please check path or file is Correct!")

    except Exception as e:
        log.error(f"Load config from file fail! please check config is Correct ! current config file: {currentProfileName}, Exception: {e}")


loadProperties(filetype=".yaml")


def getPgDbConfig() -> PgDBConfig:
    return CURRENT_CONTEXT_CONFIG.get(PG_DB_KEY)


def getAiConfig() -> AIModelConfigDTO:
    return CURRENT_CONTEXT_CONFIG.get(AI_KEY)


def getServerConfig() -> ServerConfigDTO:
    return CURRENT_CONTEXT_CONFIG.get(SERVER_KEY)



