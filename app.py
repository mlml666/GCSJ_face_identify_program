"""登录页 demo —— 课堂人脸验证考勤系统（一期 Web 端）。

用途：跑通「登录 → 工作台 → 退出」最小闭环，作为后续页面骨架的起点。
范围：只含教师/管理员登录，不含点名、比对、考勤记录等业务（尚未实现）。
约定：详细规范见 docs/规范-运行规范.md、docs/规范-接口说明规范.md。

注意：
  1. 账号密码写死在 DEMO_USERS 里，仅供演示；正式版必须换成 users 表 + 密码哈希。
  2. 会话使用 Flask 内置 session（签名 cookie），密钥来自 config.py。
  3. 本文件属于 demo，不合并进 main 分支。

运行：.\\conda\\python.exe app.py   →  浏览器打开 http://127.0.0.1:5000
"""

from flask import Flask, flash, redirect, render_template, request, session, url_for

from config import SECRET_KEY

# ---------------------------------------------------------------- 应用初始化
app = Flask(__name__)
app.secret_key = SECRET_KEY  # 会话签名密钥，缺失时由 config.py 提供开发缺省值

# 演示账号表。正式版改为 users 表：
#   username / password_hash（werkzeug.security 生成）/ role / 关联教师
DEMO_USERS = {
    "admin": {"password": "admin123", "name": "系统管理员", "role": "管理员"},
    "teacher": {"password": "teacher123", "name": "任课教师", "role": "任课教师"},
}


# ---------------------------------------------------------------- 页面路由
@app.get("/login")
def login_page():
    """GET /login：渲染登录页。

    返回:
        登录页 HTML（HTTP 200）。
    """
    return render_template("login.html")


@app.post("/login")
def login():
    """POST /login：校验账号密码，通过后写入会话并跳转工作台。

    表单字段:
        username: 账号，去除首尾空格后匹配
        password: 密码（demo 为明文比对；正式版用 generate_password_hash 校验）

    返回:
        成功：302 跳转工作台
        失败：401 + 登录页（页面顶部显示错误提示）
    """
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = DEMO_USERS.get(username)
    # 账号不存在与密码错误共用一句提示，避免泄露「该账号是否已注册」
    if user is None or user["password"] != password:
        flash("账号或密码不正确")
        return render_template("login.html", username=username), 401

    # 会话只存必要信息，不要把密码或完整用户对象写进 cookie
    session["user"] = {
        "username": username,
        "name": user["name"],
        "role": user["role"],
    }
    return redirect(url_for("index"))


@app.get("/")
def index():
    """GET /：工作台首页。

    未登录（会话中没有 user）直接重定向到登录页，避免出现半渲染的空页面。
    """
    user = session.get("user")
    if user is None:
        return redirect(url_for("login_page"))
    return render_template("index.html", user=user)


@app.get("/logout")
def logout():
    """GET /logout：清空会话并回到登录页。

    说明：一期用 GET 便于页面链接直接跳转；
    后续若引入 CSRF 防护，应改为 POST + 令牌校验。
    """
    session.clear()
    return redirect(url_for("login_page"))


# ---------------------------------------------------------------- 启动入口
if __name__ == "__main__":
    # debug=True 开启自动重载与调试堆栈，仅限本地开发；
    # 演示/预验收用：python -m flask --app app run --host 127.0.0.1 --port 5000
    app.run(debug=True)
