from datetime import timedelta

from flask import Flask, url_for, request,redirect,session
from agent.web.Login import login_bp
from agent.web.ChatServer import chat_bp
from agent.util import log, putValue
from agent.config.constant import ConfigConstantKey


all_bluprints = [login_bp, chat_bp]
app = Flask(__name__)

# 1. 配置session密钥（必填，用于加密session，生产环境替换为随机复杂字符串）
app.secret_key = "flask_rsa_auth_2025_secure_key_liwen"
# 2. 配置session持久化（可选）
app.config["SESSION_TYPE"] = "filesystem"

# 2. ✅ 核心配置：设置Session过期时间 → 示例：2小时过期
app.permanent_session_lifetime = timedelta(hours=2)
# 支持的时长单位：days(天)、hours(小时)、minutes(分钟)、seconds(秒)
# 示例：2小时过期 → timedelta(hours=2)
# 示例：30分钟过期 → timedelta(minutes=30)

#  生产环境配置，可持久化存储。
# 2. ✅ Flask-Session核心配置（Redis存储）
# app.config["SESSION_TYPE"] = "redis" # 指定Session存储方式：redis
# app.config["SESSION_REDIS"] = redis.Redis(
#     host="127.0.0.1",
#     port=6379,
#     password="", # 你的Redis密码
#     db=0 # 数据库编号
# )
# app.config["SESSION_PERMANENT"] = True # 开启永久有效
# app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=12) # 12小时过期
# app.config["SESSION_USE_SIGNER"] = True # 开启Session签名（防篡改）
# app.config["SESSION_KEY_PREFIX"] = "flask_session:" # Redis键前缀




#  配置全局拦截方法，如果未登录跳转登录页面
# 作用：每次请求到达后端，执行视图函数前，都会先执行该函数
@app.before_request
def check_login_status():
    # 1. ✅ 配置白名单：无需登录即可访问的路径/端点，必须放行！
    white_list = [
        # 放行登录页、静态文件、首页
        "/login",
        "login.login",
        "/register",
        "/",
        "static",  # 放行所有静态文件（css/js/img）
        "login.static",  # 放行蓝图的静态文件（你的login.static端点）
        "chat.static"
    ]

    # 2. 判断当前请求是否在白名单内 → 是则直接放行
    current_path = request.path  # 当前请求路径
    current_endpoint = request.endpoint  # 当前请求端点
    log.info(f"Current path: {current_path}, Current endpoint: {current_endpoint}")
    if current_path in white_list or current_endpoint in white_list:
        return None  # 放行，继续执行原请求

    # print(f"Current seesion: {session.get('username')}")
    # 3. ✅ 校验登录态：未登录 → 跳转到登录页
    if not session.get(ConfigConstantKey.USERNAME):
        return redirect(url_for("login.login", next=current_path))

    #  下面这两个参数，控制动态更新session 的过期时间，session.permanent == True , 表示让
    #  permanent_session_lifetime 参数生效， session.modified == True, 表示让浏览器更新当前会话过期时间
    session.permanent = True
    session.modified = True

    # 登录成功后，将session 中用户ID 存储到上下文信息中
    putValue(ConfigConstantKey.USER_ID, session.get(ConfigConstantKey.USER_ID))

    # 4. 已登录 → 放行，执行原视图函数
    return None


@app.context_processor
def inject_global_vars():
    """向所有Jinja2模板注入全局变量"""
    return {
        "is_login": bool(session.get("user_id")),  # 是否登录（布尔值）
        "username": session.get("username", ""),  # 当前登录用户名
        "user_id": int(session.get("user_id", -1))   # 用户ID
    }


for bluprint in all_bluprints:
    app.register_blueprint(bluprint)

print("=== 当前已注册的路由端点 ===")
for rule in app.url_map.iter_rules():
    log.info(f"端点名：{rule.endpoint} → 路由地址：{rule.rule}")
if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")


