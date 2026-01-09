from typing import List

from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    type: str = Field("deepseek", description="模型的类型，即模型的提供商, 默认 deepseek")
    name: str = Field("deepseek-chat", description="模型的名称, 默认 deepseek-chat")
    url: str = Field("https://api.deepseek.com", description="模型的访问地址")
    beta_url: str | None = Field(None, description="模型的测试功能地址，如果使用模型的测试功能，需要配置完整路径")
    apikey: str | None = Field(None, description="模型的访问Token, 必传")


class AIModelConfigDTO(BaseModel):
    ai: List[ModelInfo] = Field(description="AI 模型配置信息, 必传字段")

