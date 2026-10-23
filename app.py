"""课堂人脸验证考勤系统 —— 登录页 demo。

仅用于演示登录流程，不包含业务逻辑。
注意：账号密码写死在代码里，正式版必须改为数据库 + 密码哈希（werkzeug.security）。
"""

import os

from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-secret-change-me")

# 演示账号：正式版改成 users 表
USERS = {
    "admin": {"password": "admin123", "name": "系统管理员", "role": "管理员"},
    "teacher": {"password": "teacher123", "name": "任课教师", "role": "任课教师"},
}


@app.get("/login")
def login_page():
    return render_template("login.html")


@app.post("/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = USERS.get(username)
    if user is None or user["password"] != password:
        flash("账号或密码不正确")
        return render_template("login.html", username=username), 401
    session["user"] = {"username": username, "name": user["name"], "role": user["role"]}
    return redirect(url_for("index"))


@app.get("/")
def index():
    user = session.get("user")
    if user is None:
        return redirect(url_for("login_page"))
    return render_template("index.html", user=user)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(debug=True)
