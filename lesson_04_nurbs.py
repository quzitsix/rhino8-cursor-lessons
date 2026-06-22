# ============================================================
# Lesson 4：NURBS（非均匀有理 B 样条）
# 对应文档：第三部分「NURBS，非均匀有理 B 样条」
# ------------------------------------------------------------
# 一句话理解：NURBS = 贝塞尔曲线/曲面的"加强版"。
#   - 多了【权重 weight】：某个控制点权重越大，曲线越被它吸引。
#   - 多了【节点 knots】：控制曲线各段的影响范围。
#   - 因为有"权重"(有理 Rational)，它能【精确】表示圆、椭圆、圆柱等，
#     而普通贝塞尔曲线只能近似圆。这是 NURBS 最重要的优势。
# ------------------------------------------------------------
# 运行方法：Rhino 8 → ScriptEditor → 粘贴 → F5
# ============================================================

import Rhino
import rhinoscriptsyntax as rs


def 演示_权重影响():
    """同一组控制点，改变中间点权重 → 曲线形状不同。"""
    if not rs.IsLayer("Lesson4_权重对比"):
        rs.AddLayer("Lesson4_权重对比", [255, 120, 0])
    rs.CurrentLayer("Lesson4_权重对比")

    控制点 = [Rhino.Geometry.Point3d(0, 0, 0),
              Rhino.Geometry.Point3d(5, 8, 0),
              Rhino.Geometry.Point3d(10, 0, 0)]

    for 权重 in [0.5, 1.0, 3.0]:
        曲线 = Rhino.Geometry.NurbsCurve.Create(False, 2, 控制点)
        # 给中间控制点设置不同权重（索引 1）
        点 = 曲线.Points
        cp = 点[1]
        点.SetPoint(1, cp.Location, 权重)  # 权重越大越被吸引
        Rhino.RhinoDoc.ActiveDoc.Objects.AddCurve(曲线)

    print("   已生成 3 条曲线：中间点权重 0.5 / 1.0 / 3.0（越大越尖）")


def 演示_精确圆():
    """NURBS 能精确表示圆——这是它比贝塞尔强的关键。"""
    if not rs.IsLayer("Lesson4_精确圆"):
        rs.AddLayer("Lesson4_精确圆", [0, 160, 255])
    rs.CurrentLayer("Lesson4_精确圆")

    圆 = Rhino.Geometry.Circle(Rhino.Geometry.Point3d(20, 0, 0), 5)
    圆曲线 = 圆.ToNurbsCurve()  # 转成 NURBS，内部用了"权重"才能精确成圆
    Rhino.RhinoDoc.ActiveDoc.Objects.AddCurve(圆曲线)
    print("   已生成一个精确的 NURBS 圆（半径 5）")


def 演示_nurbs曲面():
    """带权重的 NURBS 曲面（这里用 rs 高级接口造一个起伏面）。"""
    if not rs.IsLayer("Lesson4_NURBS曲面"):
        rs.AddLayer("Lesson4_NURBS曲面", [120, 200, 120])
    rs.CurrentLayer("Lesson4_NURBS曲面")

    点阵 = []
    for i in range(5):
        for j in range(5):
            x = 30 + i * 3
            y = j * 3
            z = 3.0 if (i + j) % 2 == 0 else 0.0  # 棋盘式起伏
            点阵.append([x, y, z])
    曲面 = rs.AddSrfPtGrid((5, 5), 点阵)
    print("   已生成 5x5 起伏 NURBS 曲面")
    return 曲面


def 演示NURBS():
    旧图层 = rs.CurrentLayer()
    print("== NURBS 演示开始 ==")
    演示_权重影响()
    演示_精确圆()
    演示_nurbs曲面()
    rs.CurrentLayer(旧图层)
    rs.Command("_-Zoom _Extents")
    print("✅ Lesson 4 完成：权重对比 + 精确圆 + NURBS 曲面")


演示NURBS()

# ===== 概念小结 =====
# 贝塞尔 → NURBS 多了两样东西：
#   权重(weight)：调单个控制点的"吸引力"
#   节点(knots) ：把长曲线分段，每段由局部控制点决定（改一点不影响全局）
# "有理(Rational)" = 带权重 → 能精确表示圆/椭圆等二次曲线。
# Rhino 内部几乎所有自由曲线/曲面都是 NURBS。
#
# ===== 练习 =====
# 1. 把权重列表改成 [1, 5, 10]，看曲线越来越尖。
# 2. 用 rs.AddCircle 画个圆，再 rs.ConvertCurveToPolyline 看看它被分成多少段。
# 3. 用 Cursor 提问："为什么普通贝塞尔曲线画不出精确的圆？"
