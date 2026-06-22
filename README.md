# 星火智能游戏 · Rhino 8 + Cursor 预习教程

一套循序渐进的 **Rhino 8 Python 建模 + Cursor AI 编程** 学习 Demo，配套《星火-智能游戏》课前预习材料。

从几何基础到数学建模（贝塞尔/NURBS/Brep），再到 CLI 自动化控制 Rhino，最后用一个综合项目串起整个流程。

## 学习路线

完整指南见 [`00_学习指南.md`](./00_学习指南.md)。

| 文件 | 主题 | 学什么 |
|------|------|--------|
| `00_学习指南.md` | 总指南 | 总路线 + Cursor 用法 + 5 天计划 |
| `lesson_01_rhino_basics.py` | 基础对象 | 点 / 线 / 曲线 / 曲面 / 实体 |
| `lesson_02_bezier_curve.py` | 贝塞尔曲线 | 控制点如何决定曲线（含 De Casteljau 手算对照） |
| `lesson_03_bezier_surface.py` | 贝塞尔曲面 | 控制网格如何决定曲面 |
| `lesson_04_nurbs.py` | NURBS | 权重 / 节点 / 精确圆 |
| `lesson_05_brep.py` | Brep | 实体的面 / 边 / 顶点 + 布尔运算 |
| `lesson_06_curve_to_form.py` | 由曲线造形 | 挤出 / 旋转 / 放样 / 扫掠 |
| `lesson_07_cli_control.py` | CLI 控制 | COM 与 rhinocode 外部自动化 |
| `lesson_08_capstone_future_building.py` | 综合项目 | 由曲线生成未来建筑 |
| `cli_batch_commands.txt` | 命令宏 | Rhino 命令行批处理 |

## 如何运行

### 内部脚本（lesson_01 ~ 06、08）

在 **Rhino 8** 里运行，无需额外安装 Python：

1. 打开 Rhino 8
2. 命令行输入 `ScriptEditor` 回车
3. 新建脚本，粘贴对应 `lesson_xx.py` 内容
4. 按 `F5` 运行
5. 看不到图形就在命令行输入 `Zoom Extents`

> Rhino 8 内置 CPython 3.9，ScriptEditor 顶部选 **Python 3**。

### 外部控制（lesson_07）

需要外部 Python + `pywin32`，或使用 Rhino 自带的 `rhinocode` CLI：

```bash
pip install pywin32
python lesson_07_cli_control.py
```

或（推荐，能连已运行的 Rhino）：

```bash
# 先在 Rhino 命令行执行一次 StartScriptServer
rhinocode list
rhinocode command "_-Circle 0,0,0 5"
rhinocode script "<你的项目路径>/rhino_lessons/lesson_01_rhino_basics.py"
```

## 涉及概念

- **Bézier 曲线/曲面**：用少量控制点拉出的光滑曲线/曲面，自由造型的基础
- **NURBS**：带权重和节点的升级版，能精确表示圆/椭圆等
- **Brep**：用"面 + 边 + 顶点"描述实体边界
- **CLI 控制**：在 Rhino 外部用脚本 / AI 驱动建模

## License

MIT
