# ============================================================
# Lesson 5：Brep（Boundary Representation，边界表示）
# 对应文档：第三部分「Brep」+「Grasshopper 中的 Brep 使用方式」
# ------------------------------------------------------------
# 一句话理解：Brep 用"边界"来描述一个实体。
#   一个实体 = 若干【面 Face】缝合起来；
#   每个面的轮廓 = 若干【边 Edge】；
#   边与边相交 = 若干【顶点 Vertex】。
#   层级：Solid(Brep) → Faces → Edges → Vertices
# 几乎所有"实体"（盒子、球、布尔运算结果）在 Rhino 里都是 Brep。
# ------------------------------------------------------------
# 运行方法：Rhino 8 → ScriptEditor → 粘贴 → F5
# ============================================================

import Rhino
import rhinoscriptsyntax as rs


def 检查Brep结构(brep, 名称):
    """打印一个 Brep 的面 / 边 / 顶点数量。"""
    print(f"  [{名称}] 面 Faces = {brep.Faces.Count}, "
          f"边 Edges = {brep.Edges.Count}, "
          f"顶点 Vertices = {brep.Vertices.Count}, "
          f"封闭实体 = {brep.IsSolid}")


def 演示Brep():
    旧图层 = rs.CurrentLayer()
    doc = Rhino.RhinoDoc.ActiveDoc

    if not rs.IsLayer("Lesson5_Brep"):
        rs.AddLayer("Lesson5_Brep", [200, 120, 255])
    rs.CurrentLayer("Lesson5_Brep")

    print("== Brep 结构演示 ==")

    # ---- 1) 一个盒子就是最简单的 Brep：6 个面、12 条边、8 个顶点 ----
    盒子 = Rhino.Geometry.Box(
        Rhino.Geometry.Plane.WorldXY,
        Rhino.Geometry.Interval(0, 10),
        Rhino.Geometry.Interval(0, 10),
        Rhino.Geometry.Interval(0, 10),
    )
    盒brep = 盒子.ToBrep()
    doc.Objects.AddBrep(盒brep)
    检查Brep结构(盒brep, "盒子")

    # ---- 2) 布尔运算：盒子 - 球 = 带凹陷的 Brep（面/边/顶点变多）----
    球 = Rhino.Geometry.Sphere(Rhino.Geometry.Point3d(10, 10, 10), 5)
    球brep = 球.ToBrep()
    公差 = doc.ModelAbsoluteTolerance
    结果 = Rhino.Geometry.Brep.CreateBooleanDifference(盒brep, 球brep, 公差)

    if 结果:
        for b in 结果:
            # 往 X 方向挪开一点，避免和原盒子重叠看不清
            b.Translate(Rhino.Geometry.Vector3d(15, 0, 0))
            doc.Objects.AddBrep(b)
            检查Brep结构(b, "盒子减球")

    doc.Views.Redraw()
    rs.CurrentLayer(旧图层)
    rs.Command("_-Zoom _Extents")
    print("✅ Lesson 5 完成：Brep 结构 + 布尔运算")


演示Brep()

# ===== 概念小结 =====
# - Brep = Boundary Representation：用"面+边+顶点"的边界来定义实体。
# - 盒子：6 面 / 12 边 / 8 顶点；布尔挖洞后这些数量都会增加。
# - 在 Grasshopper 里，Brep 是处理实体的核心数据类型（Deconstruct Brep
#   就是把它拆成 Faces / Edges / Vertices）。
#
# ===== 练习 =====
# 1. 把球半径改成 8，重新看"盒子减球"的面/边数量变化。
# 2. 改成 CreateBooleanUnion（并集），把两个盒子合并。
# 3. 用 Cursor 提问："Brep 和 Mesh（网格）有什么区别？游戏引擎更喜欢哪种？"
