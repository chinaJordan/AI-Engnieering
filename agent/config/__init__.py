
from .dto import PgDBConfigDTO as PgDBConfig, PgSqlConfig, ServerConfigDTO, AIModelConfigDTO, ModelInfo, CommonConfig
from .LoadPropertiesIntoEnv import getServerConfig, getPgDbConfig, getAiConfig
from .EnvConfig import initConfig

# 初始化配置
initConfig()

__all__ = [
    "PgDBConfig",
    "PgSqlConfig",
    "ServerConfigDTO",
    "AIModelConfigDTO",
    "CommonConfig",
    "ModelInfo",
    "getServerConfig",
    "getPgDbConfig",
    "getAiConfig"
]
