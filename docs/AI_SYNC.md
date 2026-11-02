# AI 同步文档

> 给接手的 AI（或新队员）看：先读本文件，再读 [PROGRESS.md](PROGRESS.md)，就知道项目做到哪、下一步做什么、什么不能碰。
> 更新规则：有实质进展就改第一节的 JSON 快照；决策变化再改第二节。`done` 段最多保留最近 5 条，更早的写进 docs/progress/<姓名>.md，不在此重复。

## 一、状态快照（机器可读，优先相信这里）

```json
{
  "project": "GCSJ_face_identify_program",
  "remote": "https://github.com/mlml666/GCSJ_face_identify_program (private, 默认分支 develop)",
  "scope": "一期 PC 浏览器 Web 端（教师端 + 管理端），学生手机端二期",
  "phase": "需求基线收尾 / 开发提前启动",
  "updated": "2026-11-02",
  "branches": {
    "main": "docs-only baseline",
    "develop": "same as main, integration target",
    "feature/login-demo": "flask login demo, NOT merged",
    "feature/kiosk-camera": "kiosk page (laptop camera capture), demo only, NOT merged"
  },
  "code": {
    "entry": "app.py",
    "config": "config.py（配置集中处，SECRET_KEY / 上传限制 / 比对阈值）",
    "templates": ["login.html", "index.html", "kiosk.html"],
    "static": ["css/kiosk.css", "js/kiosk.js"],
    "database": "none yet（打卡机名单与记录暂存进程内存 KIOSK 字典）",
    "face_recognition": "not integrated（打卡机比对走 _mock_verify 桩，响应带 mock=True）"
  },
  "env": {
    "type": "conda，创建在项目内",
    "path": ".conda/python.exe",
    "python": "3.9.25",
    "flask": "3.0.3",
    "verified": "Flask 3.0.3 可运行；dlib / face_recognition 尚未安装验证",
    "note": "不进 Git，按 docs/环境说明-conda虚拟环境使用.md 重建"
  },
  "done": [
    "需求优先级清单 V1.2（现场改为打卡机抓拍）",
    "打卡机页面 demo（feature/kiosk-camera，比对为桩）",
    "最简登录页 demo（feature/login-demo）",
    "项目内 conda 环境 + 环境使用说明",
    "运行规范 + 接口说明规范"
  ],
  "in_progress": ["SRS V1.1 修订（含抓拍口径）", "登录 demo 评审", "打卡机页面联调"],
  "blocked_by": ["TBD-1 人数 30/42", "TBD-2 工期 40/43/55 天"],
  "next": ["TBD 确认后出 SRS V1.1", "剩余 3 个页面骨架（学生管理 / 记录查询 / 统计）", "数据库表设计", "打卡机比对桩换真实 face_recognition"],
  "never": ["把 demo 合入 main", "提交学生照片/人脸特征/*.db", "写死未确认的人数与工期"]
}
```

## 二、关键决策（不用再讨论）

1. 一期只做 PC 浏览器 Web 端；学生手机自助页放二期 —— 依据：需求优先级清单 V1.2 第二节
2. 人脸比对走 1:1 验证（现场照片 vs 该生存档照），不做 1:N；阈值以距离 0.6 为起点
3. 学生照片由教师/管理员在 Web 端上传或批量导入，不依赖学生自助上传
4. 接口统一 REST/JSON，响应格式 `{code, message, data}`，二期移动端直接复用
5. 准确率口径：正常光照 ≥90%，验收合格线 ≥85%
6. 登录 demo 的账号写死在代码里，正式版必须换成数据库 + 密码哈希
7. 现场采集方式定为「打卡机」：用一台笔记本 + 本机摄像头当终端，学生走到跟前刷脸，取代「教师拍照再上传」——依据：需求优先级清单 V1.2 P0-08。分层约定：浏览器只做像素级质量判定（亮度 / 拉普拉斯方差 / 帧差，连续达标自动抓拍），人脸检测与 1:1 比对放后端；「先跟踪再识别」不做实时跟踪，只用「连续多帧稳定」代替（性能与实现成本更划算）
8. 打卡机页面 `http://127.0.0.1:5000/kiosk` 免登录（演示用）；正式版须校验终端绑定的课程与设备，局域网 IP 访问时浏览器不给摄像头，必须用 localhost

## 三、未决问题

| 编号 | 问题 | 影响 | 责任人 |
| --- | --- | --- | --- |
| TBD-1 | 试点班级 30 人还是 42 人 | 并发、5 分钟口径、数据准备量 | 刘青松 |
| TBD-2 | 工期 40/43/55 天哪个为准 | 里程碑与验收时间 | 刘青松 |
| TBD-3 | 甲方名称统一为成都信息工程大学人工智能学院 | SRS 全文 4 处 | 马力 |
| TBD-4 | 文档名用《软件需求规格说明书》还是《软件实施需求规格说明书》 | 交付清单一致性 | 刘青松 |

## 四、接手后的操作顺序

```bash
git checkout develop && git pull
# 读 README.md → docs/PROGRESS.md → 本文件
git checkout feature/login-demo     # 需要看登录 demo 时
git checkout feature/kiosk-camera   # 需要看打卡机时
python app.py                       # http://127.0.0.1:5000/login ；打卡机 http://127.0.0.1:5000/kiosk
```

动手前先开自己的分支，提交前更新 `docs/PROGRESS.md` 和本文件第一节的 JSON。

## 五、常见坑

- Windows 上 dlib / face_recognition 编译容易失败，先备好预编译 whl，或准备 OpenCV LBPH 备选
- `.db` 和照片目录被 `.gitignore` 排除，换机器要自行重建数据
- `docs/项目资料/` 里有同名文档多个版本，口径冲突未消除前以 TBD 为准
- demo 分支里的账号密码是明文写死的，别直接搬进正式代码
- 摄像头只在安全上下文可用：`http://127.0.0.1:5000/kiosk` 可以，`http://192.168.x.x:5000` 不行（浏览器直接拒绝 getUserMedia）
- 打卡机名单与记录是进程内存里的 `KIOSK` 字典，Flask 自动重载会把它清空；正式版必须落 SQLite
- 打卡机返回的比对距离是桩值（固定 0.3125 判通过 / 0.8731 判未通过，欧氏距离越小越像），响应里 `mock: true`，别拿去做准确率统计
