# 课堂人脸验证考勤系统（FACS）

成都信息工程大学人工智能学院课程工程实践项目。一期做 PC 浏览器 Web 端：教师按名单顺序点名、学生现场照片与存档照片做 1:1 人脸验证、考勤记录自动统计。

## 当前状态

- 一期范围：PC 浏览器 Web 端（教师端 + 管理端）；学生手机自助页放二期
- 需求阶段：已产出《需求优先级清单 V1.1》《需求调研会议纪要》，待双方签字；《软件需求规格说明书》V1.1 待修订
- 代码：只有一个最简登录页 demo，在 `feature/login-demo` 分支，**未合入 main**

## 技术栈

Python 3.9 / Flask 3 / SQLite / HTML + Bootstrap 5 / face_recognition（未接入）

## 目录结构

```
.
├─ README.md
├─ requirements.txt            依赖清单
├─ environment.yml             conda 环境定义（团队统一）
├─ .conda/                     项目内虚拟环境（本地生成，不进 Git）
├─ docs/
│  ├─ 环境说明-conda虚拟环境使用.md
│  ├─ 规范-运行规范.md
│  ├─ 规范-接口说明规范.md
│  ├─ PROGRESS.md              团队进度看板
│  ├─ AI_SYNC.md               给 AI 的进度快照（换人/换 AI 先读这个）
│  ├─ BRANCHING.md             分支、提交、合并规范
│  ├─ progress/                6 名成员的个人进度
│  ├─ 项目资料/                群文件里的原始文档
│  └─ 交付物/                  我们产出、待甲方签字的文档
├─ app.py                      登录 demo（只在 feature/login-demo 分支）
└─ templates/                  同上
```

## 环境准备（Anaconda，环境装在项目内）

```powershell
conda env create -p .conda -f environment.yml    # 首次创建，约 2—5 分钟
.\.conda\python.exe -c "import flask; print(flask.__version__)"   # 验证
```

细节与排错见 [环境说明](docs/环境说明-conda虚拟环境使用.md)。

## 本地运行

```powershell
git checkout feature/login-demo     # 目前唯一有代码的分支
.\.conda\python.exe app.py          # 浏览器打开 http://127.0.0.1:5000
```

demo 账号：`admin / admin123`、`teacher / teacher123`（仅演示用，正式版必须替换掉）

开发约束见 [运行规范](docs/规范-运行规范.md)；新增接口前先读 [接口说明规范](docs/规范-接口说明规范.md)。

## 分支

| 分支 | 用途 | 现状 |
| --- | --- | --- |
| `main` | 稳定主干，只接受 PR 合入 | 文档基线，无业务代码 |
| `develop` | 集成分支，功能分支先合这里 | 与 main 一致 |
| `feature/login-demo` | 最简登录页 demo | 唯一有代码的分支，不并入 main |

详见 [docs/BRANCHING.md](docs/BRANCHING.md)。

## 协作流程

1. `git checkout develop && git pull`
2. `git checkout -b feature/<模块>-<简述>`
3. 提交前同步更新 `docs/PROGRESS.md` 和 `docs/AI_SYNC.md`
4. push 后提 PR 到 `develop`，至少 1 人评审再合

## 红线

- 学生照片、人脸特征向量、`.db` 数据库文件一律不进 Git
- `feature/login-demo` 等实验分支不直接合入 `main`
- 人数与工期口径未确认（TBD-1 / TBD-2），文档里不要写死

## 文档索引

- 使用说明：[docs/环境说明-conda虚拟环境使用.md](docs/环境说明-conda虚拟环境使用.md)
- 运行规范：[docs/规范-运行规范.md](docs/规范-运行规范.md)
- 接口规范：[docs/规范-接口说明规范.md](docs/规范-接口说明规范.md)
- 团队进度：[docs/PROGRESS.md](docs/PROGRESS.md)
- AI 同步：[docs/AI_SYNC.md](docs/AI_SYNC.md)
- 分支规范：[docs/BRANCHING.md](docs/BRANCHING.md)
- 个人进度：[docs/progress/](docs/progress)
- 原始材料：[docs/项目资料/](docs/项目资料)
- 待签交付物：[docs/交付物/](docs/交付物)
