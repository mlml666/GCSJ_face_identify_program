"""课堂人脸验证考勤系统 —— 一期 Web 端（登录 + 打卡机）。

包含两部分：
  1. 登录页 demo：跑通「登录 → 工作台 → 退出」；
  2. 打卡机（kiosk）：把「教师上传照片」改成「学生站到笔记本前刷脸」——
     笔记本就是打卡机，摄像头抓拍后走 1:1 比对。当前比对是桩实现（响应带
     mock=True），接入 face_recognition 后只需替换 _mock_verify，接口与前端不用改。

约定：接口响应统一 {code, message, data}，业务码见 docs/规范-接口说明规范.md。

注意：
  - 账号与考勤状态都放内存，重启即清空，仅供演示；正式版落 SQLite。
  - 摄像头只在安全上下文可用（localhost 或 HTTPS）。打卡机就跑在这台笔记本上，
    用 http://127.0.0.1:5000/kiosk 打开；用局域网 IP（http://192.168.x.x:5000）
    打开会拿不到摄像头。
  - 本分支代码基于登录 demo，不合并进 main。

运行：.\\conda\\python.exe app.py   →  http://127.0.0.1:5000/kiosk
"""

from datetime import datetime

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from config import (
    ALLOWED_EXTENSIONS,
    FACE_MATCH_THRESHOLD,
    MAX_CONTENT_LENGTH,
    PERMANENT_SESSION_LIFETIME,
    SECRET_KEY,
)

# ---------------------------------------------------------------- 应用初始化
app = Flask(__name__)
app.secret_key = SECRET_KEY  # 会话签名密钥，缺失时由 config.py 提供开发缺省值
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH  # 超过上限时 Flask 返回 413
app.config["PERMANENT_SESSION_LIFETIME"] = PERMANENT_SESSION_LIFETIME  # 登录会话有效期

# 演示账号表。正式版改为 users 表：
#   username / password_hash（werkzeug.security 生成）/ role / 关联教师
DEMO_USERS = {
    "admin": {"password": "admin123", "name": "系统管理员", "role": "管理员"},
    "teacher": {"password": "teacher123", "name": "任课教师", "role": "任课教师"},
}


# ---------------------------------------------------------------- 统一响应封装
def ok(data=None, message="ok"):
    """成功响应，业务码 0。"""
    return jsonify({"code": 0, "message": message, "data": data})


def err(code, message, http_status=400):
    """失败响应，code 用接口规范里的业务码（1001 参数、1002 文件、4001 业务冲突…）。"""
    return jsonify({"code": code, "message": message, "data": None}), http_status


@app.errorhandler(413)
def _payload_too_large(_error):
    """上传超限：按接口规范返回 1002，而不是 Flask 默认的 HTML 页面。"""
    return err(1002, "单张照片不能超过 5MB", 413)


# ---------------------------------------------------------------- 打卡机演示数据
# 演示名单：正式版从 student 表按课程名单读取，并按学号升序
DEMO_STUDENTS = [
    {"student_no": f"20241320{index:02d}", "name": f"演示学生{index:02d}"} for index in range(1, 13)
]

# 一次考勤任务的状态。正式版落 SQLite：
#   attendance_session(id, course_id, date, status) + attendance_record(...)
KIOSK = {
    "course": "机器学习（周三 3-4 节）",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "students": DEMO_STUDENTS,
    "index": 0,
    "records": [],
}


def _kiosk_state():
    """组装打卡机当前状态：进度、当前学生、汇总。"""
    total = len(KIOSK["students"])
    index = KIOSK["index"]
    present = sum(1 for record in KIOSK["records"] if record["status"] == "出勤")
    base = {
        "course": KIOSK["course"],
        "date": KIOSK["date"],
        "index": index,
        "total": total,
        "present": present,
    }
    if index >= total:
        base.update({"done": True, "current": None, "records": KIOSK["records"]})
        return base
    base.update({"done": False, "current": KIOSK["students"][index]})
    return base


def _mock_verify(force_fail=False):
    """1:1 比对桩：返回「比对距离」（欧氏距离，越小越像，保留四位小数）。

    真实实现（邓先斌负责）应：
      1. 现场照片提 128 维特征；
      2. 与 face 表里该学号的存档特征算欧氏距离（face_recognition.face_distance）；
      3. 距离 <= FACE_MATCH_THRESHOLD 判通过。
    桩实现固定返回一对距离值，响应里带 mock=True，避免演示时被当成真实准确率。
    """
    if force_fail:
        return 0.8731  # 距离大 = 不像，模拟未通过
    return 0.3125      # 距离小 = 像，模拟通过


# ---------------------------------------------------------------- 登录
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
    # 让 PERMANENT_SESSION_LIFETIME（config.py）真正生效：关浏览器后 8 小时内仍有效
    session.permanent = True
    return redirect(url_for("index"))


@app.get("/")
def index():
    """GET /：工作台首页，未登录时重定向到登录页。"""
    user = session.get("user")
    if user is None:
        return redirect(url_for("login_page"))
    # 页面清单在视图里算好再传给模板（规范-运行规范 §5.6：模板不做数据构造）。
    # 系统共 5 个页面：登录、点名（打卡机）、学生管理、记录查询、统计；
    # 登录与打卡机已实现，其余 3 个待开发。
    nav_items = [
        {"label": "点名（打卡机）", "href": url_for("kiosk_page")},
        {"label": "学生管理", "href": None},
        {"label": "记录查询", "href": None},
        {"label": "统计报表", "href": None},
    ]
    return render_template("index.html", user=user, nav_items=nav_items)


@app.get("/logout")
def logout():
    """GET /logout：清空会话并回到登录页。

    说明：一期用 GET 便于页面链接跳转；后续加 CSRF 防护时应改为 POST。
    """
    session.clear()
    return redirect(url_for("login_page"))


# ---------------------------------------------------------------- 打卡机页面
@app.get("/kiosk")
def kiosk_page():
    """GET /kiosk：打卡机页面（全屏，摄像头抓拍）。

    该页面不做登录校验，方便把笔记本当终端直接打开；正式版应校验终端绑定的课程。
    """
    return render_template(
        "kiosk.html",
        course=KIOSK["course"],
        date=KIOSK["date"],
        total=len(KIOSK["students"]),
    )


@app.get("/api/v1/kiosk/current")
def kiosk_current():
    """GET 当前待打卡学生与进度。

    返回:
        data.done=True 时表示本次考勤已结束，附带汇总与全部记录。
    """
    return ok(_kiosk_state())


@app.post("/api/v1/kiosk/verify")
def kiosk_verify():
    """POST 现场照片 → 1:1 比对 → 写记录 → 自动进入下一位。

    表单字段:
        file: 现场抓拍的 jpg/png，≤5MB
    查询参数:
        mock=fail 时模拟「未通过」，用于演示异常与人工复核流程

    返回:
        data 含 passed / distance / threshold / status / suggestion / next，
        其中 distance 为比对面部距离（欧氏距离，越小越像），mock=True 表示这是桩结果。
    """
    if KIOSK["index"] >= len(KIOSK["students"]):
        return err(4001, "本次考勤已结束", 409)

    file = request.files.get("file")
    if file is None or not file.filename:
        return err(1001, "未收到现场照片")
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return err(1002, "仅支持 jpg / jpeg / png")
    raw = file.read()
    if not raw:
        return err(1001, "照片内容为空")

    student = KIOSK["students"][KIOSK["index"]]
    distance = _mock_verify(force_fail=request.args.get("mock") == "fail")
    passed = distance <= FACE_MATCH_THRESHOLD
    status = "出勤" if passed else "待核实"

    KIOSK["records"].append({
        "student_no": student["student_no"],
        "name": student["name"],
        "status": status,
        "distance": distance,
        "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "photo_bytes": len(raw),
    })
    KIOSK["index"] += 1

    return ok({
        "student_no": student["student_no"],
        "name": student["name"],
        "passed": passed,
        "distance": distance,
        "threshold": FACE_MATCH_THRESHOLD,
        "status": status,
        "suggestion": "比对通过，已记为出勤" if passed else "光线或角度不佳，可重拍，或由教师人工复核",
        "mock": True,
        "next": _kiosk_state(),
    })


@app.post("/api/v1/kiosk/skip")
def kiosk_skip():
    """POST 跳过当前学生（记为缺勤），进入下一位。

    对应点名页的「标记缺勤」按钮，教师发现学生确实没来时使用。
    """
    if KIOSK["index"] >= len(KIOSK["students"]):
        return err(4001, "本次考勤已结束", 409)

    student = KIOSK["students"][KIOSK["index"]]
    KIOSK["records"].append({
        "student_no": student["student_no"],
        "name": student["name"],
        "status": "缺勤",
        "distance": None,
        "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "photo_bytes": 0,
    })
    KIOSK["index"] += 1
    return ok({"skipped": student, "next": _kiosk_state()})


@app.post("/api/v1/kiosk/reset")
def kiosk_reset():
    """POST 重置演示状态（仅 demo 用）。

    正式版应改为「按课程 + 日期新建一次考勤任务」，历史记录不能清空。
    """
    KIOSK["index"] = 0
    KIOSK["records"].clear()
    return ok(_kiosk_state())


# ---------------------------------------------------------------- 启动入口
if __name__ == "__main__":
    # debug=True 开启自动重载与调试堆栈，仅限本地开发；
    # 打卡机演示建议用：python -m flask --app app run --host 127.0.0.1 --port 5000
    app.run(debug=True, port=5000)
