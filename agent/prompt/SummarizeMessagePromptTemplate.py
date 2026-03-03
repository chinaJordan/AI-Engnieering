
'''
    提示词模版管理，所有的提示词模版统一在这里进行管理
'''
import json
from typing import Any

SUMMARIZE_TEMPLATE = """f'hello, this is a content {content} '"""

def summarizeMsgPrompt(content: Any)-> str:
    """
    总结提示词模版，将输入的内容按照指定的格式进行总结并返回
    :param content:
    :return:
    """
    template =  '''
        请按照以下要求对当前内容进行总结，要求总结后内容字数尽可能少，内容够精炼，同时不损失关键内容信息，保证语义的完整性。
        比如：
        输入内容：[
            {
                "role": "system",
                "content": "你好你是一位非常厉害的助手，擅长调用各种工具和处理复杂任务，你能够理解复杂的内容，同时擅长推理，写作，翻译，对话等各种场景,你可以在保证信息准确的前提下给予最恰当的回复，同时需要保证回复的内容合规合法，不能超出当前的道德要求和法规法规要求！"
            },
            {
                "role": "user",
                "content": "我想买一件衣服，大小呢在175左右，款式最新的，另外天气情况帮我统计下，看看未来最近7天的天气怎么样？"
            }
        ]
        
        返回格式：
            [ 
            {
                "role": "system",
                "content": "你是AI助手，擅长调用工具、处理复杂任务，比如对话，翻译，推理，写作等，同时保证回复内容符合公序良俗，且保证信息的准确性。"
            },
            {
                "role": "user",
                "content": "买一件款式最新的衣服，大小175左右。查询未来7天天气情况。"
            }
        ]
        要求返回的格式和输入的格式保持一致，同时只对内容进行总结提炼。
        
        当前输入的内容是：
            %(content)s
    '''
    return template % {"content": content}

if __name__ == "__main__":
    template_str = 'f"Hello, {name}! Age: {age}"'

    # 2. 动态替换变量（通过 locals()/globals() 传参）
    name = "Henry"
    age = 40
    result = eval(template_str)
    print(result)  # 输出：Hello, Henry! Age: 40.
    content = [
        {
            "role": "system",
            "content": "Hello, you are good at process data, traslate, coding, generation and other complex task!"
        }
    ]

    # json_content = json.dumps(content)
    template = summarizeMsgPrompt(content)

    print(f"Template:  {template}")
    # print(f"Process template: {template % content}")