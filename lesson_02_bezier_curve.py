# ============================================================
# Lesson 2：贝塞尔曲线 Bézier Curve
# 对应文档：第三部分「Bézier Curve，贝塞尔曲线」
# ------------------------------------------------------------
# 核心思想：用少数几个"控制点"，就能拉出一条光滑曲线。
#   - 曲线一定通过【第一个】和【最后一个】控制点
#   - 中间的控制点像"磁铁"，把曲线往自己方向吸，但曲线不一定经过它们
# ------------------------------------------------------------
# 运行方法：Rhino 8 → ScriptEditor → 粘贴 → F5
# ============================================================

import rhinoscriptsyntax as rs

# ---- 用 De Casteljau 算法手动计算贝塞尔曲线 ----
# 这样能真正"看懂"贝塞尔曲线是怎么算出来的，而不是只调一个 API。

def lerp(a, b, t):
    """两点之间线性插值：t=0 在 a，t=1 在 b。"""
    return [a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t]


def de_casteljau(控制点, t):
    """对任意数量控制点求 t 处的贝塞尔曲线点（递归逐层插值）。"""
    点 = list(控制点)
    while len(点) > 1:
        点 = [lerp(点[i], 点[i + 1], t) for i in range(len(点) - 1)]
    return 点[0]


def 手动贝塞尔曲线(控制点, 采样数=50):
    """按公式逐点采样，连成折线（模拟贝塞尔曲线）。"""
    采样点 = [de_casteljau(控制点, i / 采样数) for i in range(采样数 + 1)]
    return rs.AddPolyline(采样点)


def 演示贝塞尔曲线():
    旧图层 = rs.CurrentLayer()

    # === 控制点（4 个 = 三次贝塞尔，最常用）===
    控制点 = [[0, 0, 0], [3, 8, 0], [9, 8, 0], [12, 0, 0]]

    # --- 图层1：画出控制点和控制多边形（辅助理解）---
    if not rs.IsLayer("Lesson2_控制"):
        rs.AddLayer("Lesson2_控制", [180, 180, 180])
    rs.CurrentLayer("Lesson2_控制")
    for p in 控制点:
        rs.AddPoint(p)
    rs.AddPolyline(控制点)  # 控制多边形（灰色折线）

    # --- 图层2：手动算法生成的曲线（红色）---
    if not rs.IsLayer("Lesson2_手动曲线"):
        rs.AddLayer("Lesson2_手动曲线", [255, 0, 0])
    rs.CurrentLayer("Lesson2_手动曲线")
    手动曲线 = 手动贝塞尔曲线(控制点)

    # --- 图层3：Rhino 原生贝塞尔曲线（蓝色），用来对照验证 ---
    if not rs.IsLayer("Lesson2_原生曲线"):
        rs.AddLayer("Lesson2_原生曲线", [0, 100, 255])
    rs.CurrentLayer("Lesson2_原生曲线")
    # AddCurve + degree=3 ：用 4 个控制点生成的就是一条三次贝塞尔曲线
    原生曲线 = rs.AddCurve(控制点, 3)

    rs.CurrentLayer(旧图层)
    rs.Command("_-Zoom _Extents")

    print("✅ Lesson 2 完成：贝塞尔曲线已创建")
    print("   灰色 = 控制点/控制多边形")
    print("   红色 = 手动算法(De Casteljau)生成")
    print("   蓝色 = Rhino 原生曲线（两者应几乎重合）")
    print("   手动曲线长度:", round(rs.CurveLength(手动曲线), 2))
    print("   原生曲线长度:", round(rs.CurveLength(原生曲线), 2))


演示贝塞尔曲线()

# ===== 概念小结 =====
# - 4 个控制点 → 三次(degree=3)贝塞尔曲线，是建模里最常用的。
# - 曲线被"夹"在控制多边形内部（凸包性质）。
# - 拖动中间控制点 → 曲线整体跟着弯，是"自由造型"的基础。
#
# ===== 练习 =====
# 1. 把控制点改成 3 个 [[0,0,0],[6,10,0],[12,0,0]]，degree 改成 2（二次贝塞尔）。
# 2. 把中间某个控制点的 Y 抬高到 20，观察曲线被"吸"得更厉害。
# 3. 用 Cursor 提问："为什么贝塞尔曲线一定经过首尾控制点？"
