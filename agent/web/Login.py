from flask import Blueprint, jsonify,request, render_template, flash, redirect, url_for, session

from agent.util import RSA_PUBLIC_KEY, rsa_decrypt, rsa_key, gen_salt, pwd_hash, log
from agent.memory import UserInfo



login_bp = Blueprint("login", __name__, "/account")

# app = Flask(__name__)

user_db = {}

@login_bp.route("/")
def index():
    """首页：登录成功后跳转地址，未登录则重定向到登录页"""
    if "username" not in session:  # 校验登录态
        return redirect(url_for("login.login"))
    return render_template("application.html", username=session["username"], user_id=session["user_id"])

@login_bp.route("/register", methods=["GET", "POST"])
def register():
    """注册接口：GET渲染页面，POST处理注册请求"""
    if request.method == "GET":
        # 传给前端RSA公钥，用于密码加密
        return render_template("register.html", rsa_public_key=RSA_PUBLIC_KEY)

    # POST请求：处理注册
    username = request.form.get("username", "").strip()
    cipher_pwd = request.form.get("password", "")  # 前端加密后的密码密文
    phone = request.form.get("phone", None)
    email = request.form.get("email", None)

    # 1. 基础校验
    if not username or not cipher_pwd or not phone:
        flash("用户名和密码,电话不能为空！")
        return render_template("register.html", rsa_public_key=RSA_PUBLIC_KEY)

    userinfo = UserInfo(user_name=username, phone=phone)
    existsUser = userinfo.queryFromDb(userinfo)
    if existsUser:
        flash(f"用户名: { username } 或者手机号： {phone}  已存在注册用户！")
        return render_template("register.html", rsa_public_key=RSA_PUBLIC_KEY)

    # 2. 后端私钥解密密码 → 明文
    try:
        plain_pwd = rsa_decrypt(cipher_pwd)
    except Exception as e:
        log.error(f"Password descrypt fail! Exception: {e}")
        flash(f"密码解密失败：{str(e)}")
        return render_template("register.html", rsa_public_key=RSA_PUBLIC_KEY)

    # 3. 生成盐值 + 密码加盐哈希 → 存储（不可逆）
    salt = gen_salt()
    hash_pwd = pwd_hash(plain_pwd, salt)

    userinfo.pass_word = hash_pwd
    userinfo.email = email if email else None
    userinfo.salt = salt
    result = userinfo.insertToDb([userinfo])
    log.debug(f"Insert to data result: {result}")

    flash("注册成功！请登录")
    return redirect(url_for("login.login"))

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    """登录接口：GET渲染页面，POST处理登录请求"""
    if request.method == "GET":
        next_url = request.args.get("next","/")
        return render_template("login.html", rsa_public_key=RSA_PUBLIC_KEY, next_url=next_url)

    # POST请求：处理登录
    username = request.form.get("username", "").strip()
    cipher_pwd = request.form.get("password", "")
    # 1. 基础校验
    if not username or not cipher_pwd:
        flash("用户名和密码不能为空！")
        return render_template("login.html", rsa_public_key=RSA_PUBLIC_KEY)

    #  查询数据库用户信息是否存在
    userInfo = UserInfo(user_name=username, phone=username, email=username)
    userInfos = userInfo.queryFromDb(userInfo, queryCondition=" or ")
    if not userInfos:
        log.info(f"用户：{username} 未查询到！请检查用户名是否正确！")
        flash(f"用户名： {username} 不存在, 请检查用户名是否正确或者注册新用户！")
        return render_template("login.html", rsa_public_key=RSA_PUBLIC_KEY)

    # 2. 解密前端密码 + 加盐哈希校验
    try:
        plain_pwd = rsa_decrypt(cipher_pwd)
        # user_info = user_db[username]
        # 前端明文密码 + 数据库盐值 → 哈希，与数据库存储值对比
        if pwd_hash(plain_pwd, userInfos[0]["salt"]) != userInfos[0]["pass_word"]:
            flash("输入密码错误！")
            return render_template("login.html", rsa_public_key=RSA_PUBLIC_KEY)
    except Exception as e:
        flash(f"登录失败：{str(e)}")
        log.error(f"Exception: {e}")
        return render_template("login.html", rsa_public_key=RSA_PUBLIC_KEY)

    # 3. 登录成功：写入session维护登录态，跳转到首页/
    session["username"] = username
    session["user_id"] = userInfos[0]["id"]
    return redirect(url_for("login.index"))

@login_bp.route("/logout")
def logout():
    """退出登录：清除session"""
    session.pop("username", None)
    session.pop("user_id", None)
    flash("已成功退出登录")
    return redirect(url_for("login.login"))

@login_bp.route("/logoff", methods=["post"])
def logoff():
    try:
        user_id = session["user_id"]
        log.info(f"Current ready delete user id : {user_id}")
        deleteUser = UserInfo(id=user_id)
        result = deleteUser.deleteFromDb(deleteUser)
        log.info(f"Delete user {user_id} Success! Result: {result}")
        session.pop("username", None)
        session.pop("user_id", None)
        flash("已成功注销用户")
        return jsonify({
            "success": True,
            "msg": "success"
        })
    except Exception as e:
        log.error(f"Logoff user fail! Exception: {e}")
        return jsonify({
            "success": False,
            "msg": "服务异常，请稍后再试！"
        })




# with app.test_request_context():
#     print(url_for("index"))