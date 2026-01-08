import datetime

from flask import Blueprint, url_for,render_template,request,jsonify,session
from agent.agentServer.AgentServer import inputMsg

# app = Flask(__name__)
chat_bp = Blueprint("chat",__name__)

@chat_bp.route("/welcome")
def firstRoute():
    return "this is first route!"

@chat_bp.route("/submit", methods=["POST","GET"])
def submit():
    if request.method == "POST":
        user = request.form.get("username")
        phone = request.form.get("phone")
        print(f"Server side receive: user: {user}, phone: {phone}")
    else:
        user = "default"
        phone = "default"
    return render_template("application.html",  username=user, phone=phone)

@chat_bp.route("/index/<username>", methods=["GET", "POST"])
def index(username: str):
    # return "this is first Page! %s" % escape(username)
    print(f"username: {username}")
    # ,username=username, phone="*"
    return render_template("welcome.html")
    # name=username,


@chat_bp.route("/chat/welcome")
def chat_page():
    username = session["username"]
    return render_template("application.html", username=username)

# ========== 2. 核心异步接口：接收用户消息，返回对话响应（无页面刷新） ==========
@chat_bp.route("/api/chat", methods=["POST", "OPTIONS", "GET"])
def chat_api():
    # 1. 接收前端AJAX提交的用户输入内容
    user_input = request.json.get("msg", "").strip()

    # 2. 对话逻辑处理（可替换为AI接口/业务逻辑，这里模拟后端响应）
    if not user_input:
        return jsonify({"code": 0, "msg": "请输入对话内容！"})

    # 模拟后端返回的响应内容（实际开发可对接LLM/数据库/自定义逻辑）
    now_time = datetime.datetime.now().strftime("%H:%M:%S")
    response = inputMsg(user_input)
    bot_response = f"【{now_time} AI灵狐回复】ANSWER(^-^): \n{response}"

    # 3. 返回JSON格式数据（前端AJAX接收，实现无刷新渲染）
    return jsonify({
        "code": 200,
        "msg": user_input,  # 用户输入的内容
        "bot_msg": bot_response  # 后端返回的响应内容
    })


# with app.test_request_context():
#     print(url_for("static", filename="style.css"))

