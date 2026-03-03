""" Agent 工具定义类 """
import json

from langchain.tools import tool
from langgraph.types import interrupt, Command

from agent.util import log

@tool
def testSendEmail(subject: str, to: str, content: str):
    """
    发送邮件信息给到指定的用户，
    args:
        subject: 发送的主题
        to: 发送目标对象
        content: 发送的内容
    :param subject:
    :param to:
    :param content:
    :return:
    """
    sendMsg = {
        "allowAction":["approve", "reject"],
        "description": "请确认是否发送以下邮件信息，确认发送请回复OK，不发送请回复 cancel!",
        "from": "AI",
        "to": to,
        "subject": subject,
        "content": content
    }

    response = interrupt(sendMsg)
    log.info(f"Send email to {to} resume exe! Response: {response}")

    if isinstance(response, dict):
        if response["doAction"] == "approve" or (response["doAction"] != "reject"):
            log.info(f"Id: {response['id']}, Send emil: {sendMsg} success!")
            return f"Send email to {to} has successed!"

        else:
            log.info(f"Id: {response['id']}, Cancel send emil to {to} success!")
            return f"Send email to {to} has canceled!"

    else:
        log.info(f"ReviewResponse is {response}, default to send!")
        return f"Send email to {to} default has send success!"
    # if response["reply"]:
    #     log.info(f"Send emil: {sendMsg} success!")
    # else:
    #     log.info(f"Cancel send emil to {to} success!")

@tool
def testCallPhone(phone: str, to: str):
    """
    拨打指定电话给指定用户
    args:
        phone: 拨打电话号码
        to: 拨打电话对象

    """
    callPhone = {
        "allowAction": ["approve", "reject", "edit"],
        "description": "请确认是否拨打以下电话，并呼叫指定用户： 确认回复： OK， 取消回复： cancel!",
        "from": "AI",
        "to": to,
        "phone": phone
    }

    response = interrupt(callPhone)
    log.info(f"Call to {to} resume exe!")

    if isinstance(response, dict):
        if response["doAction"] == "approve" or (response["doAction"] != "reject"):
            log.info(f"Id: {response['id']}, Call people: {callPhone} success!")
            return f"Call to {to} has success!"

        else:
            log.info(f"Id: {response['id']}, Cancel call to {to} success!")
            return f"Call to {to} has canceled!"


    else:
        log.info(f"ReviewResponse is {response}, default to call!")

        return f"Call to {to} default has call success!"

    # if response["reply"]:
    #     log.info(f"Call people: {callPhone} success!")
    # else:
    #     log.info(f"Cancel call to {to} success!")