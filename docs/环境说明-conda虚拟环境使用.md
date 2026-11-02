# 开发环境说明（Anaconda / 项目内虚拟环境）

本项目把虚拟环境**创建在项目目录内部**（`.conda\`），不装进全局 base。好处：路径固定、互不干扰、删掉重装即可还原，换电脑只要重跑一遍命令。

> `.conda\` 体积约 500MB–1GB，已在 `.gitignore` 中排除，**不进 Git**。团队成员各自在本地创建。

## 一、环境信息

| 项 | 值 |
| --- | --- |
| 环境位置 | `<仓库根目录>\.conda`（示例：`E:\GCSJ_face_identify_program\.conda`；换机器换成自己的仓库路径即可） |
| Python 版本 | 3.9.25（实际创建结果） |
| Flask 版本 | 3.0.3 |
| 解释器 | `.conda\python.exe` |
| 依赖清单 | `environment.yml`、`requirements.txt` |
| 包管理器 | 优先 conda 建环境，依赖优先用 conda 装 |

## 二、首次创建（新成员先做这一步）

方式一：按统一清单创建（推荐，团队口径一致）

```powershell
cd <仓库根目录>
conda env create -p .conda -f environment.yml
```

方式二：手动两步

```powershell
conda create -p .conda python=3.9 -y
conda install -p .conda flask=3.0.3 -y     # 推荐用 conda 装 Flask
```

如果网络正常、想用 pip 也行：

```powershell
.\.conda\python.exe -m pip install -r requirements.txt
```

> 本项目实测：`conda install -p .conda flask=3.0.3` 最稳（本机 pip 安装时会在临时目录反复失败），装完版本为 Flask 3.0.3。

创建完验证一下：

```powershell
.\.conda\python.exe -c "import sys, flask; print(sys.version); print('flask', flask.__version__)"
```

期望输出 Python 3.9.x 和 `flask 3.0.3`。

## 二之二、依赖唯一来源

**依赖只认 `requirements.txt`**。`environment.yml` 只负责 Python 版本与 `pip`，不再声明第三方包——两份清单各写一遍迟早不同步。装依赖一律：

```powershell
.\.conda\python.exe -m pip install -r requirements.txt
```

## 二之三、国内网络加速（国内机器建议先配）

```powershell
# pip 镜像（只配一次，写进用户级配置）
.\.conda\python.exe -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# conda 镜像（写进 ~/.condarc；改完 conda clean -i 清索引缓存）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
```

### 人脸识别依赖（下一阶段用，**现在不要装**）

> 这两步要等邓先斌在真机上验证后再写进 `requirements.txt`。dlib 在 Windows 上源码编译常失败，用预编译轮子：

```powershell
.\.conda\python.exe -m pip install dlib-bin -i https://pypi.tuna.tsinghua.edu.cn/simple
.\.conda\python.exe -m pip install face_recognition --no-deps
.\.conda\python.exe -m pip install numpy Pillow click -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 三、日常使用

### 方式 A：不激活，直接用解释器（推荐）

避免各种 shell 钩子问题，命令最短：

```powershell
.\.conda\python.exe app.py
```

装依赖同样用绝对路径：

```powershell
.\.conda\python.exe -m pip install -r requirements.txt
```

### 方式 B：激活环境

```powershell
conda activate <仓库根目录>\.conda
python app.py
conda deactivate
```

如果 `conda activate` 报 `CommandNotFoundError: Your shell has not been properly configured`：

```powershell
conda init powershell     # 然后关掉窗口重开
```

## 四、IDE 里指定解释器（必做，否则跑的还是 base）

**PyCharm**
`Settings → Project → Python Interpreter → Add Interpreter → Conda Environment → Existing`
→ 解释器路径填 `<仓库根目录>\.conda\python.exe`（把尖括号部分换成你的实际路径）

**VS Code**
`Ctrl+Shift+P → Python: Select Interpreter → Enter interpreter path`
→ 粘贴同上路径

确认方法：IDE 右下角显示的版本应为 3.9，而不是 Anaconda base 的 3.12。

## 五、依赖变更

- 只加 Python 包：改 `requirements.txt`，然后 `.\.conda\python.exe -m pip install -r requirements.txt`
- 要改 Python 版本或加 conda 级依赖：改 `environment.yml`，删掉 `.conda` 重建

导出当前实际环境（排查用，不必提交）：

```powershell
conda env export -p .conda > environment-lock.txt
```

## 六、常见问题

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `conda activate` 报 shell 未初始化 | PowerShell 没配钩子 | `conda init powershell` 后重开终端 |
| 运行时报 `ModuleNotFoundError: flask` | 用成了全局 python | 用 `.\.conda\python.exe`，或换 IDE 解释器 |
| 端口 5000 被占用 | 上一个进程没退 | `netstat -ano \| findstr :5000` 找到 PID，`taskkill /PID <pid> /F`；或临时改端口 |
| 环境损坏、装啥都报错 | 装依赖时中断 | 删掉 `.conda` 目录，按第二节重建 |
| 装 dlib / face_recognition 失败 | Windows 缺编译环境 | 不要硬编，改用预编译 whl 或 conda-forge 的 dlib，详见后续环境验证记录 |

## 七、清理

### 7.1 只清缓存，不动环境（日常）

```powershell
# conda 包缓存：约 330MB，删掉不影响已建好的环境，只是下次装依赖会重新下载
Remove-Item -Recurse -Force .conda-pkgs

# Python 字节码缓存：运行时自动重建
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Where-Object { $_.FullName -notlike '*\.conda\*' } | Remove-Item -Recurse -Force
```

清理后环境照常可用，验证：

```powershell
.\.conda\python.exe -c "import flask; print(flask.__version__)"
```

### 7.2 连环境一起删（重装）

```powershell
# 先停掉正在跑的 flask 进程
Remove-Item -Recurse -Force .conda, .conda-pkgs
```

重装即回到干净状态，项目代码与文档不受影响。`.tmp` 是 pip 的临时目录，被 `.gitignore` 忽略，删不掉也不影响使用。
