# ============================================================
# Lesson 3：贝塞尔曲面 Bézier Surface
# 对应文档：第三部分「Bézier Surface，贝塞尔曲面」
# ------------------------------------------------------------
# 核心思想：贝塞尔曲线的"升维"。
#   曲线：一排控制点  →  一条曲线
#   曲面：一个网格控制点(行 x 列)  →  一张曲面
#   抬高/拉低网格里的某个点，曲面就会在那里鼓起/凹陷。
# ------------------------------------------------------------
# 运行方法：Rhino 8 → ScriptEditor → 粘贴 → F5
# ============================================================

import Rhino
import rhinoscriptsyntax as rs


def 演示贝塞尔曲面():
    旧图层 = rs.CurrentLayer()

    # === 4x4 控制网格（16 个控制点）→ 双三次贝塞尔曲面 ===
    # 先在 XY 平面铺一张平网格，再把中间 4 个点抬高，做出"鼓包"。
    行数, 列数 = 4, 4
    间距 = 4.0
    控制点 = []
    for i in range(行数):
        for j in range(列数):
            x = i * 间距
            y = j * 间距
            z = 0.0
            # 中间 (1,1)(1,2)(2,1)(2,2) 这几个点抬高，形成隆起
            if 1 <= i <= 2 and 1 <= j <= 2:
                z = 6.0
            控制点.append(Rhino.Geometry.Point3d(x, y, z))

    # --- 显示控制网格点（辅助理解）---
    if not rs.IsLayer("Lesson3_控制网格"):
        rs.AddLayer("Lesson3_控制网格", [180, 180, 180])
    rs.CurrentLayer("Lesson3_控制网格")
    for p in 控制点:
        rs.AddPoint(p)

    # --- 用 RhinoCommon 创建贝塞尔曲面 ---
    # degree=3（三次）+ 4 个控制点/方向 = 标准贝塞尔曲面
    曲面 = Rhino.Geometry.NurbsSurface.CreateFromPoints(
        控制点,
        行数, 列数,   # U、V 方向的控制点数量
        3, 3          # U、V 方向的阶数（degree）
    )

    if not rs.IsLayer("Lesson3_曲面"):
        rs.AddLayer("Lesson3_曲面", [80, 200, 120])
    rs.CurrentLayer("Lesson3_曲面")

    if 曲面 and 曲面.IsValid:
        曲面ID = Rhino.RhinoDoc.ActiveDoc.Objects.AddSurface(曲面)
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()
        print("✅ Lesson 3 完成：贝塞尔曲面已创建")
        print("   曲面 ID:", 曲面ID)
        print("   灰点 = 4x4 控制网格；中间 4 点被抬高 → 曲面隆起")
    else:
        print("❌ 曲面创建失败，请检查控制点数量是否 = 行数 x 列数")

    rs.CurrentLayer(旧图层)
    rs.Command("_-Zoom _Extents")


演示贝塞尔曲面()

# ===== 概念小结 =====
# - 曲面由 U、V 两个方向的控制点网格决定（这里是 4x4）。
# - 抬高网格里的点 → 曲面在对应位置鼓起，这就是"自由曲面造型"。
# - 它是 NURBS 曲面的特例（权重都相等、节点均匀时）。
#
# ===== 练习 =====
# 1. 把中间抬高的 z 从 6 改成 12，看隆起变高。
# 2. 把网格改成 5x5，把四个角也抬高，做一个"枕头"形状。
# 3. 用 Cursor 提问："贝塞尔曲面和 NURBS 曲面有什么区别？"
