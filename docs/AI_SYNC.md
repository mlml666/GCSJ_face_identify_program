# AI 同步文档

> 给接手的 AI（或新队员）看：先读本文件，再读 [PROGRESS.md](PROGRESS.md)，就知道项目做到哪、下一步做什么、什么不能碰。
> 更新规则：有实质进展就改第一节的 JSON 快照和第二节的最近变更；决策变化再改第三节。

## 一、状态快照（机器可读，优先相信这里）

```json
{
  "project": "GCSJ_face_identify_program",
  "scope": "一期 PC 浏览器 Web 端（教师端 + 管理端），学生手机端二期",
  "phase": "需求基线收尾 / 开发提前启动",
  "updated": "2026-10-23",
  "branches": {
    "main": "docs-only baseline",
    "develop": "same as main, integration target",
    "feature/login-demo": "flask login demo, NOT merged"
  },
  "code": {
    "entry": "app.py",
    "config": "config.py（配置集中处，SECRET_KEY / 上传限制 / 比对阈值）",
    "templates": ["login.html", "index.html"],
    "database": "none yet",
    "face_recognition": "not integrated",
    "static": "none"
  },
  "env": {
    "type": "conda，创建在项目内",
    "path": ".conda/python.exe",
    "python": "3.9.25",
    "flask": "3.0.3",
    "note": "不进 Git，按 docs/环境说明-conda虚拟环境使用.md 重建"
  },
  "done": [
    "需求优先级清单 V1.1（docs/交付物）",
    "需求调研会议纪要 V1.0（docs/交付物）",
    "仓库结构 + 分支规范 + 进度文档",
    "最简登录页 demo（feature/login-demo）",
    "项目内 conda 环境 + 环境使用说明",
    "运行规范 + 接口说明规范"
  ],
  "in_progress": ["SRS V1.1 修订", "登录 demo 评审"],
  "blocked_by": ["TBD-1 人数 30/42", "TBD-2 工期 40/43/55 天"],
  "next": ["TBD 确认后出 SRS V1.1", "五个页面骨架", "数据库表设计", "人脸比对接口桩"],
  "never": ["把 demo 合入 main", "提交学生照片/人脸特征/*.db", "写死未确认的人数与工期"]
}
```

## 二、关键决策（不用再讨论）

1. 一期只做 PC 浏览器 Web 端；学生手机自助页放二期 —— 依据：需求优先级清单 V1.1 第二节
2. 人脸比对走 1:1 验证（现场照片 vs 该生存档照），不做 1:N；阈值以距离 0.6 为起点
3. 学生照片由教师/管理员在 Web 端上传或批量导入，不依赖学生自助上传
4. 接口统一 REST/JSON，响应格式 `{code, message, data}`，二期移动端直接复用
5. 准确率口径：正常光照 ≥90%，验收合格线 ≥85%
6. 登录 demo 的账号写死在代码里，正式版必须换成数据库 + 密码哈希

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
git checkout feature/login-demo     # 需要看 demo 时
python app.py                       # http://127.0.0.1:5000
```

动手前先开自己的分支，提交前更新 `docs/PROGRESS.md` 和本文件第一节的 JSON。

## 五、常见坑

- Windows 上 dlib / face_recognition 编译容易失败，先备好预编译 whl，或准备 OpenCV LBPH 备选
- `.db` 和照片目录被 `.gitignore` 排除，换机器要自行重建数据
- `docs/项目资料/` 里有同名文档多个版本，口径冲突未消除前以 TBD 为准
- demo 分支里的账号密码是明文写死的，别直接搬进正式代码
