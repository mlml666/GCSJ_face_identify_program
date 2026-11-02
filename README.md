# 课堂人脸验证考勤系统（FACS）

> 成都信息工程大学人工智能学院 · 课程工程实践项目 · 一期 PC 浏览器 Web 端
> 用「按名单顺序点名 + 打卡机摄像头现场抓拍 1:1 人脸验证」替代人工点名，把单节课考勤从约 15 分钟压缩到 5 分钟以内。

**验收指标**：整节课（一个班）点名 ≤ 5 分钟；正常光照识别准确率 ≥ 90%（合格线 85%）；考勤数据准确率 100%；单次比对响应 ≤ 2 秒。

## 当前进度

| 阶段 | 状态 |
| --- | --- |
| 需求基线（优先级清单 + 会议纪要 + SRS） | 🟡 待双方签字（SRS V1.1 待修订） |
| 技术方案与 dlib / face_recognition 验证 | ⬜ 未开始 |
| 环境与数据准备 | 🟡 部分就绪（conda 环境已建、Flask 能跑；dlib / face_recognition 未验证；学生照片未收集） |
| 开发实现（Web 端一期） | 🟢 登录页 demo + 打卡机页面 demo 完成 |
| 特征库 / 测试 / 培训试运行 / 验收 | ⬜ 未开始 |

代码现状：**登录页 demo**（`feature/login-demo`）+ **打卡机页面 demo**（`feature/kiosk-camera`），按约定均不合并进 `main`。

页面口径：系统共 **5 个页面**（登录、点名/打卡机、学生管理、记录查询、统计）。已实现登录页与打卡机页面；原型阶段交付 **4 张**（点名、学生管理、记录查询、统计，不含登录）。

## 快速开始

```powershell
git clone https://github.com/mlml666/GCSJ_face_identify_program.git
cd GCSJ_face_identify_program

# 1. 创建项目内虚拟环境（Anaconda，装在 .conda\ 下，不进仓库）
conda env create -p .conda -f environment.yml

# 2. 切到有代码的分支并运行
git checkout feature/login-demo
.\.conda\python.exe app.py        # 浏览器打开 http://127.0.0.1:5000

# 3. 打卡机演示（笔记本当终端，需用 localhost 才给摄像头）
git checkout feature/kiosk-camera
.\.conda\python.exe app.py        # 打开 http://127.0.0.1:5000/kiosk
```

演示账号：`admin / admin123`、`teacher / teacher123`（仅演示，正式版必须替换）。

打卡机页面操作：学生站进虚线框 → 画面稳定且画质达标自动抓拍 → 显示比对结果与比对距离 → 自动切到下一位。键盘：`Enter` 手动抓拍、`M` 演示比对失败、`空格` 记缺勤、`R` 重置演示。当前比对是桩（响应 `mock: true`）：比对距离固定为 0.3125（通过）/ 0.8731（未通过），判定规则 `distance <= threshold`，**不代表真实准确率**。

环境细节、IDE 指定解释器、排错方式见 [环境说明](docs/环境说明-conda虚拟环境使用.md)。

## 技术栈

| 层 | 选型 |
| --- | --- |
| 运行环境 | Python 3.9.25（conda，项目内 `.conda\`） |
| Web 框架 | Flask 3.0.3 |
| 数据库 | SQLite 3 |
| 前端 | HTML + Bootstrap 5（CDN，无构建工具） |
| 人脸识别 | face_recognition / dlib（**未接入**，128 维特征 + 1:1 比对） |

## 目录结构

```
.
├─ README.md
├─ requirements.txt             pip 依赖清单
├─ environment.yml              conda 环境定义
├─ app.py                       启动入口 + 登录与打卡机路由
├─ config.py                    配置集中处（密钥、上传限制、比对阈值）
├─ templates/                   Jinja2 模板（login / index / kiosk）
├─ static/                      打卡机页面样式与脚本（css/kiosk.css、js/kiosk.js）
├─ docs/
│  ├─ 环境说明-conda虚拟环境使用.md
│  ├─ 规范-运行规范.md           启动、配置、编码、提交前检查
│  ├─ 规范-接口说明规范.md       响应格式、错误码、接口清单与文档模板
│  ├─ PROGRESS.md               团队进度看板
│  ├─ AI_SYNC.md                给 AI 的进度快照（换人先读这个）
│  ├─ BRANCHING.md              分支、提交、合并规范
│  ├─ progress/                 6 名成员的个人进度
│  ├─ 项目资料/                 群文件原始文档（分工、实施计划、SRS 草稿）
│  └─ 交付物/                   待甲方签字的产出物
└─ .conda/                      本地虚拟环境（git 忽略）
```

## 分支

| 分支 | 内容 | 说明 |
| --- | --- | --- |
| `main` | 文档基线 | 稳定主干，只接受 PR |
| `develop` | 文档 + 环境说明 + 规范 | 集成分支，功能分支先合这里 |
| `feature/login-demo` | `app.py`、`config.py`、`templates/login.html` | 登录 demo，**不合并进 main** |
| `feature/kiosk-camera` | `app.py`、`config.py`、`templates/`、`static/` | 打卡机 demo（摄像头抓拍），**不合并进 main** |

协作流程：

```powershell
git checkout develop && git pull
git checkout -b feature/<模块>-<简述>
# 改代码 → 更新 docs/PROGRESS.md 和自己那页 → commit → push → 提 PR 到 develop
```

提交信息格式 `<type>: <中文简述>`，type 取 `feat` / `fix` / `docs` / `chore`。详见 [分支规范](docs/BRANCHING.md)。

## 团队分工

| 成员 | 角色 | 主要负责 | 占比 |
| --- | --- | --- | --- |
| 刘青松 | 组长 / 项目经理 | 计划、进度与风险、对外接口、验收组织 | 17% |
| 马力 | 需求分析师 | 调研、需求规格说明书、原型、优先级清单、用户测试组织 | 15% |
| 邓先斌 | 技术架构师 / 后端组长 | 架构、数据库设计、人脸比对核心与阈值调优、部署 | 20% |
| 阮亚宁 | 后端 / 数据工程师 | 学生与课程管理、考勤记录、统计导出、特征库脚本 | 18% |
| 王彦哲 | 前端工程师 | 点名页、管理端页面、Bootstrap 样式与图表 | 16% |
| 石子墨 | 测试与实施 / 培训讲师 | 测试计划与准确率测试、培训材料、试运行值守、售后 | 14% |

个人进度见 [docs/progress/](docs/progress)。

## 文档索引

| 文档 | 用途 |
| --- | --- |
| [环境说明](docs/环境说明-conda虚拟环境使用.md) | 创建 / 使用 / 排错 / 清理项目内虚拟环境 |
| [运行规范](docs/规范-运行规范.md) | 启动方式、配置约定、编码规范、提交前检查清单 |
| [接口说明规范](docs/规范-接口说明规范.md) | 统一响应、错误码、接口清单（含已实现 4 个打卡机 demo 接口）与单接口模板 |
| [团队进度](docs/PROGRESS.md) | 阶段进度、谁在做什么、阻塞项 |
| [AI 同步](docs/AI_SYNC.md) | 机器可读的进度快照与关键决策 |
| [分支规范](docs/BRANCHING.md) | 分支模型、命名、提交与合并规则 |
| [项目资料](docs/项目资料/) | 群文件原始文档 + 已知口径冲突清单 |
| [交付物](docs/交付物/) | 需求优先级清单 V1.2（现场改为打卡机抓拍）、需求调研会议纪要 |

## 常见问题

| 现象 | 处理 |
| --- | --- |
| `ModuleNotFoundError: flask` | 用错解释器了，改用 `.\.conda\python.exe`，或在 IDE 里把解释器指到 `.conda\python.exe` |
| 端口 5000 被占用 | `netstat -ano \| findstr :5000` 找到 PID 后结束进程，或改 `app.run(port=5001)` |
| `conda activate` 报 shell 未初始化 | `conda init powershell` 后重开终端 |
| 装 dlib / face_recognition 失败 | 别硬编译，改用预编译 whl 或 conda-forge 的 dlib |
| 打卡机页面没有画面、控制台报 `NotAllowedError` | 用 `http://127.0.0.1:5000/kiosk` 打开（局域网 IP 下浏览器不给摄像头），并在地址栏相机图标里允许权限 |

## 红线

- 学生照片、人脸特征向量、`*.db` 数据库文件**一律不进仓库**
- `feature/login-demo` 等实验分支**不直接合入 main**
- 人数与工期口径未确认（TBD-1 30/42 人、TBD-2 40/43/55 天），文档里不要写死
- 采集学生照片前须取得知情同意，数据仅用于本课堂考勤
