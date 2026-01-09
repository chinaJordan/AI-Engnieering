
from .dto import PgDBConfigDTO as PgDBConfig, PgSqlConfig, ServerConfigDTO, AIModelConfigDTO, ModelInfo
from .LoadPropertiesIntoEnv import getServerConfig, getPgDbConfig, getAiConfig
from .EnvConfig import initConfig

# 初始化配置
initConfig()

__all__ = [
    "PgDBConfig",
    "PgSqlConfig",
    "ServerConfigDTO",
    "AIModelConfigDTO",
    "ModelInfo",
    "getServerConfig",
    "getPgDbConfig",
    "getAiConfig"
]
