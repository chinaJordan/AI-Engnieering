import datetime
import json
from typing import Any

from flask import Blueprint, url_for,render_template,request,jsonify,session

from agent.agentServer.AgentServer import inputMsg, resumeExecute
from agent.util import log, isJson
from agent.config.constant import ConfigConstantKey

from agent.tools.ContextInfoStore import ReviewContxtInfo,ReviewRequest, ReviewResponse
from agent.util import putValue



# app = Flask(__name__)
chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/welcome")
def firstRoute():
    return "this is first route!"

@chat_bp.route("/submit", methods=["POST","GET"])
def submit():
    if request.method == "POST":
        user = request.form.get("username")
        phone = request.form.get("phone")
        log.info(f"Server side receive: user: {user}, phone: {phone}")
    else:
        user = "default"
        phone = "default"
    return render_template("application.html",  username=user, phone=phone)

@chat_bp.route("/index/<username>", methods=["GET", "POST"])
def index(username: str):
    # return "this is first Page! %s" % escape(username)
    log.info(f"username: {username}")
    # ,username=username, phone="*"
    return render_template("welcome.html")


@chat_bp.route("/chat/welcome")
def chat_page():
    username = session["username"]
    return render_template("application.html", username=username)

# ========== 2. 核心异步接口：接收用户消息，返回对话响应（无页面刷新） ==========
@chat_bp.route("/api/chat", methods=["POST", "OPTIONS", "GET"])
def chat_api():
    # 1. 接收前端AJAX提交的用户输入内容
    user_id = session.get(ConfigConstantKey.USER_ID)
    input_content = request.json.get("msg", "")
    user_input = input_content.strip() if isinstance(input_content, str) else input_content
    log.info(f"Current user: {user_id} input content: {user_input}")
    isInteractiveInput = request.json.get("is_interactive", False);


    interactive = False
    # 2. 对话逻辑处理（可替换为AI接口/业务逻辑，这里模拟后端响应）
    if not user_input:
        return jsonify({"code": 0, "msg": "请输入对话内容！"})

    if ReviewContxtInfo.getReviewRequest(user_id):
        ReviewContxtInfo.removeReviewMessage(user_id)
        log.info(f"Remove user {user_id} review messages success!")

    if isInteractiveInput or isJson(user_input):
        reviewResponses = __resolveNessageToReviewResponse(user_input)
        response = resumeExecute(session.get(ConfigConstantKey.USER_ID), reviewResponses)
        # jsonReqeust = json.load(user_input)

    else:
        response = inputMsg(user_input, session.get(ConfigConstantKey.USER_ID))

    # 模拟后端返回的响应内容（实际开发可对接LLM/数据库/自定义逻辑）
    now_time = datetime.datetime.now().strftime("%H:%M:%S")
    reviewReqeust = ReviewContxtInfo.getReviewRequest(session.get(ConfigConstantKey.USER_ID))
    if reviewReqeust:
        interactive = True
        if isinstance(reviewReqeust, dict):
            reviewReqeust = [v for v in reviewReqeust.values()][0]
        response = reviewReqeust
        log.info(f"Current return review info is : {response}")
    bot_response = f"【{now_time} AI灵狐回复】ANSWER(^-^): \n{response}"

    # 3. 返回JSON格式数据（前端AJAX接收，实现无刷新渲染）
    return jsonify({
        "code": 200,
        "msg": user_input,  # 用户输入的内容
        "bot_msg": bot_response,  # 后端返回的响应内容
        "interactive": interactive,
        "reviewRequest": reviewReqeust.model_dump_json() if interactive else None
    })


def __resolveNessageToReviewResponse(input: Any)-> list[ReviewResponse]:
    '''
        将输入的内容转为 ReviewResponse 对象， 并返回
    :param input:
    :return:
    '''
    if isinstance(input, str):
        loadContent = json.loads(input)
    else:
        loadContent = input
    if isinstance(loadContent, list):
        return [ReviewResponse(**item) for item in loadContent]
    else:
        return [ReviewResponse(**loadContent)]

# with app.test_request_context():
#     print(url_for("static", filename="style.css"))

