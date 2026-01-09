from langchain.agents.middleware import before_model, after_model
from agent.util.TimeStatictisUtil import TimeUtil,global_instance_map



@before_model
def before_model(state, runtime):
    TimeUtil.callStart("deepseek-model")
    print(f"当前开始计算时间！")

@after_model
def after_model(state, runtime):
    timeutil = global_instance_map.get("deepseek-model");
    timeutil.callEnd()
    print(timeutil.computeSpandTime())
    global_instance_map.pop("deepseek-model")
    print("模型计时结束！")
