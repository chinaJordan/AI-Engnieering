''' 文档或者文本内容筛选工具， 过滤一些不合法的内容，将不合法内容替换为 * 字符 '''
from typing import List
import re

from langchain.tools import tool, ToolRuntime


from agent.util import log

''' 默认过滤内容 '''
DEFAULT_FILTER_CONTENT = ["谋杀", "犯罪", "强奸", "手枪", "杀人"]

@tool
def filterMessages(messages: str, runtime: ToolRuntime) -> str:
    """
    根据输入的内容，将输入的内容中的一些特殊字符和词语进行替换，避免不健康或者违反的文字出现在内容中

    :param messages:  输入的消息
    :param runtime:   工具运行时上下文
    :return:
    """
    filter_content = None
    if hasattr(runtime.context, "filter"):
        filter_content = runtime.context.filter
    if not filter_content:
        filter_content = DEFAULT_FILTER_CONTENT

    if len(messages) <= 0:
        log.info(f"Input message is empty, please input content!")
        return messages

    return filterByWords(messages, filter_content)



def filterByWords(input: str, filter_keys: List[str]) -> str:
    '''
    :param input:          要过滤的字符串
    :param filter_keys:    过滤关键字
    :return:      过滤后的内容
    '''
    if len(input) < 1 or len(filter_keys) < 1:
        log.info(f"Input content or fileter_keys is Empty, don't need to execute filter!")
        return input

    replace_char = "*"
    pattern_str = "|".join(re.escape(key) for key in filter_keys)
    pattern_match = re.compile(pattern_str)

    match_result = pattern_match.search(input)
    after_content = input
    if match_result:
        after_content = pattern_match.sub(replace_str, input)
    log.debug(f"After process data: {after_content}")
    return after_content

def replace_str(macth_ob: re.Match) -> str:
    replaceChar = "*"
    match_content = macth_ob.group()
    return replaceChar * len(match_content)


if __name__ == "__main__":
    filter_keys = ["谋杀", "传播不良内容", "投毒", "强奸", "犯罪"]
    input= "这是一个恐怖的故事，有一个人在一天晚上，计划谋杀自己身边的人，但是他不知道用什么方式比较好，就先计划使用投毒，但是见到本人后起了歹意，就" \
    "计划强奸对方，又在网络上传播不良内容，最终因为这起犯罪被法律制裁！"
    after_content = filterByWords(input,filter_keys)
    log.info(f"After filter content: {after_content}")
