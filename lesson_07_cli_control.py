# ============================================================
# Lesson 7：CLI / 外部控制 Rhino
# 对应文档：第二部分「Rhino 脚本控制方式」+ 高级 CLI 指南
# ------------------------------------------------------------
# 这个脚本【在 Rhino 外部】运行（在 Cursor 的终端里 python 运行），
# 通过 Windows COM 接口连接 Rhino，发命令让它建模、存盘。
# 这就是"用代码 / Agent 自动驱动 Rhino"的基础。
# ------------------------------------------------------------
# 运行前提：
#   1. 已安装 Rhino 8
#   2. pip install pywin32
# 运行方法（在 Cursor 终端）：
#   cd <你的项目路径>\rhino_lessons
#   python lesson_07_cli_control.py
# ============================================================

import time
import os

try:
    import win32com.client
except ImportError:
    raise SystemExit("缺少 pywin32，请先运行：pip install pywin32")


def 连接Rhino(最长等待秒=90):
    """连接 Rhino 的 COM 自动化对象。

    注意（Rhino 8 实测要点）：
    - GetActiveObject 经常失败：Rhino 不会注册到 COM 运行对象表(ROT)，
      所以外部 COM 通常【连不上你已经开着的那个 Rhino】，只能新启动一个。
    - 不要读 rhino.Version：Rhino 的 COM 对象没有这个属性，会抛 AttributeError。
      正确的就绪判断是能否拿到 GetScriptObject。
    """
    try:
        rhino = win32com.client.GetActiveObject("Rhino.Application")
        print("已连接到运行中的 Rhino 实例")
    except Exception:
        print("未能连接已运行实例（COM 限制），正在启动一个新的 Rhino...")
        print("首次启动含加载/授权，可能需要 30~90 秒，请耐心等待。")
        rhino = win32com.client.Dispatch("Rhino.Application")

    try:
        rhino.Visible = True
    except Exception:
        pass

    # 轮询直到能拿到脚本对象（说明 Rhino 已完全加载），而不是去读 .Version
    起点 = time.time()
    while time.time() - 起点 < 最长等待秒:
        try:
            if rhino.GetScriptObject is not None:
                print("Rhino 已就绪")
                return rhino
        except Exception:
            pass
        time.sleep(3)

    raise TimeoutError("等待 Rhino 就绪超时；请确认 Rhino 已完全打开后重试")


def 外部建模():
    rhino = 连接Rhino()

    # === 用 RunScript 发送和命令行一样的指令 ===
    print("\n--- 创建基本几何体 ---")
    rhino.RunScript("! _-Circle 0,0,0 5", 0)
    rhino.RunScript("! _-Sphere 0,0,5 3", 0)
    rhino.RunScript("! _-Box 10,0,0 20,10,0 5", 0)
    rhino.RunScript("! _-Zoom _Extents", 0)

    # === 也可以让 Rhino 去运行一个 .py 脚本文件 ===
    # 例如运行我们前面写的 lesson_01：
    # 脚本 = r"<你的项目路径>\rhino_lessons\lesson_01_rhino_basics.py"
    # rhino.RunScript(f'! _-RunPythonScript "{脚本}"', 0)

    # === 存盘 ===
    保存目录 = os.environ.get("TEMP", r"C:\temp")
    保存路径 = os.path.join(保存目录, "rhino_cli_demo.3dm")
    rhino.RunScript(f'! _-SaveAs "{保存路径}"', 0)

    print(f"\n✅ Lesson 7 完成：外部 CLI 控制成功")
    print(f"   文件已保存到：{保存路径}")


if __name__ == "__main__":
    外部建模()

# ===== 三种控制方式对比（文档第二部分核心）=====
#   方式1  cli_batch_commands.txt  在 Rhino 内部读命令文件   最简单的批处理
#   方式2  lesson_01~06 (ScriptEditor) 内部 Python          参数化建模、复杂逻辑
#   方式3  本脚本 (外部 COM)        在 Cursor 终端 python    自动化流水线 / AI 驱动
#
# ===== ⭐ 更推荐：rhinocode CLI（官方推荐，能连"已经开着"的 Rhino）=====
# COM 连不上已运行的 Rhino，而 rhinocode 可以。步骤：
#   1) 把 Rhino System 目录加入 PATH。
#      安装路径因人而异（常见 C:\Program Files\Rhino 8 或 D:\Program Files\Rhino 8）。
#      先用注册表查出本机真实路径：
#        (Get-ItemProperty 'HKLM:\SOFTWARE\McNeel\Rhinoceros\8.0\Install').ExePath
#      下文用 <RHINO_SYSTEM> 代表该 ExePath 所在的 System 目录。
#      ⚠ 不要用 setx PATH "$env:PATH;..."（会污染/截断 PATH）。
#      ---- 临时（仅当前终端，最安全，先用它测试）----
#        $env:Path += ';<RHINO_SYSTEM>'
#      ---- 永久（只改用户变量、自动查重、无截断）----
#        $rhino = '<RHINO_SYSTEM>'
#        $userPath = [Environment]::GetEnvironmentVariable('Path','User')
#        if ($userPath -notlike "*$rhino*") {
#            $newPath = if ([string]::IsNullOrEmpty($userPath)) { $rhino } else { "$userPath;$rhino" }
#            [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
#        }
#      永久写入后需【重开终端】生效。
#      ---- 或者不改 PATH，直接全路径调用 ----
#        & '<RHINO_SYSTEM>\RhinoCode.exe' list
#   2) 在已打开的 Rhino 命令行里运行一次：StartScriptServer
#      （想每次自动开，可把它加进 Rhino 的启动命令）
#   3) 在终端里：
#        rhinocode list                       # 列出运行中的 Rhino 实例
#        rhinocode command "_-Circle 0,0,0 5" # 在 Rhino 里画个圆
#        rhinocode script "<你的项目路径>\rhino_lessons\lesson_01_rhino_basics.py"
#   4) 多个实例时用 --rhino <id> 指定，例如：
#        rhinocode --rhino rhinocode_remotepipe_7029 script foo.py
#
# ===== 练习 =====
# 1. 用 rhinocode script 让"已开着的 Rhino"直接跑 lesson_08 综合项目。
# 2. 改 RunScript / rhinocode command，自动建一座 5 层小塔。
# 3. 用 Cursor 提问："Rhino 的 rhinocode CLI 和 COM 控制各有什么优缺点？"
