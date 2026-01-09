from pydantic import BaseModel, Field


class ServerConfigDTO(BaseModel):
    class Server(BaseModel):
        ip: str | None = Field(description="服务器指定IP，默认127.0.0.1", default="127.0.0.1")
        port: int | None = Field(description="服务器指定端口，默认5000", default=5000, le=65535, ge=1)
        version: str | None = Field(description="服务器版本号，默认1.0.0", default="V1.0.0")
        name: str | None = Field(description="服务器名称，默认 AI-Application", default="AI-Application")

    server: Server = Field(description="服务器配置信息")
