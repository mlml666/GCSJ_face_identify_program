# 分支与协作规范

## 一、分支模型

```
main      稳定主干，只接受 PR 合入，任何时刻可运行
 └─ develop      日常集成分支，功能分支先合这里
     ├─ feature/<模块>-<简述>    一个人一个功能，控制在 2 天内
     ├─ fix/<简述>               缺陷修复
     └─ demo 类实验分支           独立存放，评审通过前不合并
```

## 二、命名规范

- 小写、连字符，不写中文：`feature/login-demo`、`feature/attendance-call`
- 模块名参考需求编号或模块名：`feature/face-match`、`feature/student-manage`
- 修复分支：`fix/upload-size-limit`

## 三、当前分支清单

| 分支 | 负责人 | 内容 | 状态 | 合并去向 |
| --- | --- | --- | --- | --- |
| `main` | 马力 | README、docs（进度/规范/资料/交付物） | 已提交并推送（GitHub 上**非**默认分支） | 不接受直接提交 |
| `develop` | 马力 | 与 main 一致（文档基线 + 环境与规范） | 已提交并推送，GitHub **默认分支** | 接收 `feature/*`、`fix/*` |
| `feature/login-demo` | 马力 | `app.py` + `config.py` + `templates/login.html`、`index.html` | 已提交并推送，未合并 | **不合并**，仅评审参考 |
| `feature/kiosk-camera` | 马力 | 在登录 demo 基线上加打卡机：`/kiosk`、`/api/v1/kiosk/*`、`static/css|js/kiosk.*` | 已提交并推送，未合并 | **不合并**，演示分支；真实比对接入后另开正式分支 |

说明：`feature/kiosk-camera` 已推送到 GitHub，但按当前约定仍是「不合并进 main 的演示分支」；要进主线需先接真实 face_recognition、落 SQLite 记录，再抽成正式 `feature/attendance-*` 分支走 PR 评审。

## 三之二、本次整改分支

`fix/req-review-2026-11-02`：按《FACS 项目审查整改任务清单》做的口径统一与冗余清理（已提交并推送到 GitHub，**不合并**进 `main` / `develop`），评审通过后由负责人决定是合入 `develop` 还是整支丢弃。

## 四、提交信息格式

```
<type>: <中文简述>
```

type 取值：`feat`（功能）、`fix`（修复）、`docs`（文档）、`chore`（杂务）、`refactor`（重构）

示例：

```
feat: 登录页增加错误提示
docs: 更新团队进度与分支说明
chore: 补充 requirements.txt
```

## 五、合并规则

1. 功能分支 → `develop`：提 PR，至少 1 人评审（评审人见 `docs/progress/`）
2. `develop` → `main`：只在里程碑节点合（需求确认 / 方案确认 / 核心功能完成 / 测试完成 / 验收）
3. `main` 禁止直接 push，禁止 force push
4. demo 分支默认不合并；要保留代码就抽成正式 feature 分支再走评审

## 六、GitHub 协同

1. 建仓库后把 `main` 设为默认分支并开启保护：Require PR + 1 approval
2. 新队员 clone 后先 `git checkout develop`
3. push 前本地跑通再提交，不要推明显跑不起来的代码
4. 涉及照片、人脸特征、`*.db` 的文件一律不加进暂存区（`.gitignore` 已覆盖）

## 七、每天同步三件事

```bash
git pull origin develop
# 1. 更新 docs/PROGRESS.md 里自己那一行
# 2. 更新 docs/AI_SYNC.md 第一节 JSON 快照
# 3. 在自己分支上 commit + push
```
