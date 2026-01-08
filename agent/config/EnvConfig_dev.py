import importlib
import os

# config env
DEEP_SEEK_KEY = "sk-642839b326e34bc19v8140915e9****"
ENV = "dev"

if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ.setdefault("DEEPSEEK_API_KEY", DEEP_SEEK_KEY)

# def initConfig():
#     print("Load config file start!")
#     env = os.getenv("profile")
#     # 赋值全局变量
#     global ENV
#     ENV = env
#     config = "EnvConfig"
#     if not env:
#         print(f"profile not config, use default config!")
#         config = f"config_{env}"
#     try:
#         config =  f"config_{env}"
#         active_config = importlib.import_module(config)
#         print(f"Load config file : {config} success!")
#     except ImportError:
#         print(f"Can't find config file : {config}")
