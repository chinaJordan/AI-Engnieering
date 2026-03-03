from langchain.agents.middleware import before_model, after_model
from agent.util.TimeStatictisUtil import TimeUtil,global_instance_map

from agent.util import log



@before_model
def before_model(state, runtime):
    TimeUtil.callStart("deepseek-model")
    log.info(f"当前开始计算时间！")

@after_model
def after_model(state, runtime):
    timeutil = global_instance_map.get("deepseek-model");
    timeutil.callEnd()
    log.info(timeutil.computeSpandTime())
    global_instance_map.pop("deepseek-model")
    log.info("模型计时结束！")
