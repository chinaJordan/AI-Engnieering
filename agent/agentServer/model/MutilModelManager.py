
from agent.util import log
from agent.config import getAiConfig

from langchain.chat_models import BaseChatModel, init_chat_model


MODEL_MANAGER_CONTEXT: dict[str, BaseChatModel] = {}
def initAndLoadModel():
    """ 初始化配置模型，将模型按照名字和 model 的关系存储到当前环境 """
    configModel = getAiConfig()
    loadModels = []
    try:
        for modelinfo in configModel.ai:
            # beta=modelinfo.beta_url, 这参数不是有些模型的关键字，传了会报错，暂时先保留
            model = init_chat_model(model=modelinfo.name, model_provider=modelinfo.type, base_url=modelinfo.url, api_key=modelinfo.apikey)
            MODEL_MANAGER_CONTEXT.setdefault(modelinfo.name, model)
            loadModels.append(modelinfo.name)
    except Exception as e:
        log.error(f"初始化模型失败，请检查配置文件是否正确，错误信息：{e}")
        raise Exception(f"Init model {modelinfo.name} fail! Please check config if Corrrect!")

    log.debug(f"Multi model load finish ! Loaded model: 【 {loadModels} 】")


# if __name__ == "__main__":
#     modelUse = initAndLoadModel()
