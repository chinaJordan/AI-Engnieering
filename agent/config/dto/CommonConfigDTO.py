""" 通用配置管理类 """

from pydantic import BaseModel, Field

class CommonConfig(BaseModel):
    class Common(BaseModel):
        useLocalModel: bool | None = Field(description="是否启用本地模型，默认不启用", default=False)
        localModelName: str | None = Field(description="本地模型名称，默认为空", default=None)
        localModelUrl: str | None = Field(description="本地模型地址，默认为空", default=None)


    common: Common | None = Field(description="通用配置", default=None)
