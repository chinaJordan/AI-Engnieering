""" 存储配置的相关类，传统数据库，向量库，非结构化存储统一配置 """
from typing import Literal

from pydantic import BaseModel, Field


class PgSqlConfig(BaseModel):
    user: str = Field(description="数据库连接用户名")
    password: str = Field(description="数据库连接密码")
    host: str = Field(description="数据库连接地址")
    port: int = Field(description="数据库连接端口")
    dbname: str = Field(description="数据库连接名称")
    connect_timeout: int = Field(20, description="数据库连接超时时间,单位 s")
    sslmode: Literal["disable", "allow", "prefer", "require", "verify-ca", "verify-full"] = \
        Field("require", description="数据库连接是否使用SSL加密, 默认 require")


class PgDBConfigDTO(BaseModel):
    postgresql: PgSqlConfig = Field(description="Postgresql 数据库配置")