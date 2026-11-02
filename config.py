"""项目配置：所有可变参数集中在这里，禁止散落到业务代码中。

约定见 docs/规范-运行规范.md 第四节；
敏感值一律从环境变量读取，仓库里只保留开发缺省值。
"""

import os
from datetime import timedelta

# ---------------------------------------------------------------- 安全与会话
# 会话签名密钥：开发环境用缺省值，试运行/演示前必须通过环境变量注入真实值
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret-change-me")

# 登录会话有效期：一节大课内不掉线即可
PERMANENT_SESSION_LIFETIME = timedelta(hours=8)


# ---------------------------------------------------------------- 上传限制
# 单张照片上限 5MB（需求：P0-03 / 接口规范 1002 错误码）
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

# 只接受 jpg / jpeg / png，服务端二次校验扩展名
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


# ---------------------------------------------------------------- 人脸比对
# 1:1 比对距离阈值（欧氏距离，越小越像；distance <= 该值 判为通过），默认 0.6。
# 调整必须写操作日志（P1-04）
FACE_MATCH_THRESHOLD = 0.6
