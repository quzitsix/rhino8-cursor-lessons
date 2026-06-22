# ============================================================
# Lesson 6：由曲线生成曲面 / 体块
# 对应文档：第三部分预习建议「一个由曲线生成的三维曲面或体块」
# ------------------------------------------------------------
# 4 种最常用的"从曲线造形体"的方法：
#   1. Extrude  挤出：把曲线沿直线方向拉成体
#   2. Revolve  旋转：把曲线绕轴旋转一周成体（造瓶子/花瓶）
#   3. Loft     放样：在多条截面曲线之间蒙皮成面
#   4. Sweep    扫掠：让一条截面沿一条路径滑动成面
# ------------------------------------------------------------
# 运行方法：Rhino 8 → ScriptEditor → 粘贴 → F5
# ============================================================

import rhinoscriptsyntax as rs
import math


def 演示_挤出():
    if not rs.IsLayer("Lesson6_挤出"):
        rs.AddLayer("Lesson6_挤出", [255, 100, 100])
    rs.CurrentLayer("Lesson6_挤出")

    底面 = rs.AddCircle([0, 0, 0], 4)
    路径 = rs.AddLine([0, 0, 0], [0, 0, 12])
    实体 = rs.ExtrudeCurve(底面, 路径)
    rs.CapPlanarHoles(实体)  # 封口变成实体
    print("   挤出：圆 → 圆柱")


def 演示_旋转():
    if not rs.IsLayer("Lesson6_旋转"):
        rs.AddLayer("Lesson6_旋转", [100, 200, 255])
    rs.CurrentLayer("Lesson6_旋转")

    # 一条"花瓶轮廓线"（X 是半径，Z 是高度），绕 Z 轴转一圈
    轮廓点 = [[2, 0, 0], [4, 0, 3], [3, 0, 6], [5, 0, 10], [4, 0, 14]]
    轮廓 = rs.AddInterpCurve([[15 + p[0], p[1], p[2]] for p in 轮廓点])
    曲面 = rs.AddRevSrf(轮廓, ([15, 0, 0], [15, 0, 1]))
    print("   旋转：轮廓线 → 花瓶曲面")


def 演示_放样():
    if not rs.IsLayer("Lesson6_放样"):
        rs.AddLayer("Lesson6_放样", [120, 220, 120])
    rs.CurrentLayer("Lesson6_放样")

    # 三条大小不同的圆，从下到上放样成"喇叭/树干"
    截面 = [
        rs.AddCircle([35, 0, 0], 5),
        rs.AddCircle([35, 0, 6], 2),
        rs.AddCircle([35, 0, 12], 4),
    ]
    rs.AddLoftSrf(截面)
    print("   放样：3 条截面圆 → 蒙皮曲面")


def 演示_扫掠():
    if not rs.IsLayer("Lesson6_扫掠"):
        rs.AddLayer("Lesson6_扫掠", [220, 180, 80])
    rs.CurrentLayer("Lesson6_扫掠")

    # 路径：一条波浪曲线；截面：一个小圆 → 扫出一根弯曲管子
    路径点 = [[50 + i, 3 * math.sin(i / 2.0), 0] for i in range(0, 21, 2)]
    路径 = rs.AddInterpCurve(路径点)
    截面 = rs.AddCircle(rs.CurveStartPoint(路径), 1.2)
    # 截面需要立起来对准路径起点，这里简单演示用 Sweep1
    rs.AddSweep1(路径, [截面])
    print("   扫掠：截面圆沿波浪路径 → 弯管")


def 演示由曲线造形():
    旧图层 = rs.CurrentLayer()
    print("== 由曲线生成体块 ==")
    演示_挤出()
    演示_旋转()
    演示_放样()
    演示_扫掠()
    rs.CurrentLayer(旧图层)
    rs.Command("_-Zoom _Extents")
    print("✅ Lesson 6 完成：挤出 / 旋转 / 放样 / 扫掠")


演示由曲线造形()

# ===== 概念小结 =====
# 这是 Rhino 建模的"主力打法"：先画曲线 → 再用命令生成面/体。
#   挤出 Extrude → 等截面的柱状体
#   旋转 Revolve → 回转体（瓶/碗/灯）
#   放样 Loft    → 多截面渐变体（船体/塔楼表皮，见 lesson_08）
#   扫掠 Sweep   → 沿路径的管状体（管道/栏杆）
#
# ===== 练习 =====
# 1. 把放样的三个圆半径改成 6→1→6，做一个"沙漏"。
# 2. 旋转演示里给轮廓多加两个点，做更复杂的花瓶。
# 3. 用 Cursor 提问："Loft 和 Sweep 各适合做什么？举游戏场景的例子。"
