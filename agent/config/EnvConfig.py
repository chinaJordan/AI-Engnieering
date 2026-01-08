import importlib
import os
from agent.util import log

# config env
DEEP_SEEK_KEY = "sk-642839b326e34bc19v8140915e9****"
ENV = "dev"

if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ.setdefault("DEEPSEEK_API_KEY", DEEP_SEEK_KEY)

def initConfig():
    log.info("Load config file start!")
    env = os.getenv("profile")
    # 赋值全局变量
    global ENV
    ENV = env
    config = ".EnvConfig"
    if not env:
        log.info(f"profile not config, use default config!")
        # config = f".EnvConfig_{env}"
    try:
        config = f".EnvConfig_{env}"
        active_config = importlib.import_module(config,package="config")
        log.info(f"Load config file : {config} success!")
        raise Exception("Env value is null")
    except ImportError:
        log.error(f"Can't find config file : {config}")

initConfig()