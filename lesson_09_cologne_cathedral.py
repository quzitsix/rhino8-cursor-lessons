# ============================================================
# Lesson 9（综合进阶）：德国科隆大教堂（曲线 → 曲面 参数化模型）
# 对应文档：第三部分(曲线/曲面/Brep) + 第五部分示例场景(建筑)
# ------------------------------------------------------------
# 真实参考（维基/UNESCO）：拉丁十字平面、双塔约 157m、中殿内高 43.35m、
#   四分肋拱顶(quadripartite ribbed vault)、飞扶壁(flying buttress)、
#   开放式八边形尖塔(openwork spire)、西立面玫瑰窗、尖券侧窗、小尖塔。
# 本模型按比例缩放(单位:米的相对值)，抓住这些哥特核心特征。
#
# ★ 本课重点：用“曲线”生成“曲面”——
#   · 肋拱顶 = 点阵 NURBS 曲面(web) + 沿尖拱曲线的拱肋(pipe)
#   · 飞扶壁 = 三点圆弧曲线 → pipe 成拱券
#   · 八边形尖塔 = 方→八边形 Loft + 棱线 pipe(开放感)
#   · 尖券窗 = 两段圆弧曲线 → 平面填充
# ------------------------------------------------------------
# 运行方法：Rhino 8 → ScriptEditor（Python 3）→ 粘贴 → F5
#   （几何较多，生成需要几秒，请耐心等待）
# ============================================================

import rhinoscriptsyntax as rs
import math

SQ3 = math.sqrt(3.0)


# =================== 通用工具 ===================
def 准备图层(名称, 颜色):
    if not rs.IsLayer(名称):
        rs.AddLayer(名称, 颜色)
    rs.CurrentLayer(名称)


def 多边形(cx, cy, r, n, z, 旋转=0.0):
    """返回 n 边形闭合点列（位于水平面 z 高度）。"""
    pts = []
    for k in range(n):
        a = 旋转 + 2.0 * math.pi * k / n
        pts.append([cx + r * math.cos(a), cy + r * math.sin(a), z])
    pts.append(pts[0])
    return pts


def 尖拱曲线(p0, p1, 矢高比=0.6, 段数=14):
    """在 p0、p1（等高起拱点）之间生成一条【哥特尖拱】曲线(开放)。
    用两段等边圆弧交于尖顶——这是哥特拱的几何本质，可作拱肋/拱券。"""
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    dx, dy = x1 - x0, y1 - y0
    D = math.hypot(dx, dy)
    if D < 1e-6:
        return None
    ux, uy = dx / D, dy / D
    R = D
    h = D * 矢高比
    vscale = h / (R * SQ3 / 2.0)

    平面pts = []
    for i in range(段数 + 1):                      # 左弧 180°→120°
        a = math.radians(180 + (120 - 180) * i / 段数)
        平面pts.append((D + R * math.cos(a), R * math.sin(a) * vscale))
    for i in range(1, 段数 + 1):                   # 右弧 60°→0°（跳过尖顶重复点）
        a = math.radians(60 + (0 - 60) * i / 段数)
        平面pts.append((R * math.cos(a), R * math.sin(a) * vscale))

    世界pts = [[x0 + ux * s, y0 + uy * s, z0 + v] for (s, v) in 平面pts]
    return rs.AddInterpCurve(世界pts)


def 管(曲线, 半径):
    """把一条曲线变成圆管(石质拱肋/构件的观感)。"""
    if 曲线 is None:
        return None
    try:
        return rs.AddPipe(曲线, [0.0, 1.0], [半径, 半径], cap=2)
    except Exception:
        return None


def 尖券窗闭合(基点, w, sh, 朝向="Y", 矢高比=0.62, 段数=10):
    """生成闭合的尖券窗轮廓(竖边+尖拱)，返回曲线，可用于填充玻璃。"""
    def 弧(cx, cv, R, a0, a1):
        return [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / 段数)),
                 cv + R * math.sin(math.radians(a0 + (a1 - a0) * i / 段数)))
                for i in range(段数 + 1)]
    h = w * 矢高比
    vscale = h / (w * SQ3 / 2.0)
    P = [(0.0, 0.0), (0.0, sh)]
    P += [(s, sh + v * vscale) for (s, v) in 弧(w, 0, w, 180, 120)]
    P += [(s, sh + v * vscale) for (s, v) in 弧(0, 0, w, 60, 0)][1:]
    P += [(w, 0.0), (0.0, 0.0)]
    x0, y0, z0 = 基点
    if 朝向 == "Y":
        世界 = [[x0 + u, y0, z0 + v] for (u, v) in P]
    else:
        世界 = [[x0, y0 + u, z0 + v] for (u, v) in P]
    return rs.AddPolyline(世界)


# =================== 肋拱顶 ===================
def 肋拱顶一跨(x0, x1, y0, y1, zs, 矢高, 肋半径=0.35):
    """一个矩形开间的四分肋拱：
    - web 腹板：用 min(两向正弦) 生成交叉拱的点阵 NURBS 曲面
    - 对角拱肋 + 横向拱肋：沿尖拱曲线生成圆管
    """
    nu = nv = 11
    wx, wy = x1 - x0, y1 - y0
    pts = []
    for i in range(nu):
        u = i / (nu - 1.0)
        for j in range(nv):
            v = j / (nv - 1.0)
            x = x0 + wx * u
            y = y0 + wy * v
            z = zs + 矢高 * min(math.sin(math.pi * u), math.sin(math.pi * v))
            pts.append([x, y, z])
    rs.AddSrfPtGrid((nu, nv), pts)

    # 对角拱肋（两条交叉的尖拱）
    d = math.hypot(wx, wy)
    管(尖拱曲线([x0, y0, zs], [x1, y1, zs], 矢高比=矢高 / d), 肋半径)
    管(尖拱曲线([x1, y0, zs], [x0, y1, zs], 矢高比=矢高 / d), 肋半径)
    # 横向拱肋（开间前缘）
    管(尖拱曲线([x0, y0, zs], [x1, y0, zs], 矢高比=矢高 / wx), 肋半径)


# =================== 八边形开放尖塔 ===================
def 八边形尖塔(cx, cy, z底, 半径, 高, 棱半径=0.25, 颜色=None):
    """方/八边形过渡 + 八边形锥尖 + 八条棱线管(开放式尖塔观感)。"""
    八底 = 多边形(cx, cy, 半径, 8, z底, 旋转=math.pi / 8)
    apex = [cx, cy, z底 + 高]
    # 八个三角面(锥尖)
    for i in range(8):
        rs.AddSrfPt([八底[i], 八底[i + 1], apex])
    # 八条棱线做成细管(强调骨架/开放感)
    for i in range(8):
        棱 = rs.AddLine(八底[i], apex)
        管(棱, 棱半径)
    # 顶部十字花尖
    rs.AddLine(apex, [cx, cy, z底 + 高 + 高 * 0.12])


# =================== 塔楼 ===================
def 建造塔楼(x0, y0, tw, 塔身高, 过渡高, 尖顶高):
    cx, cy = x0 + tw / 2.0, y0 + tw / 2.0

    # 塔身：底方框 → 顶略收方框（loft 收分）
    缩 = tw * 0.10
    底 = [[x0, y0, 0], [x0 + tw, y0, 0], [x0 + tw, y0 + tw, 0], [x0, y0 + tw, 0], [x0, y0, 0]]
    顶方 = [[x0 + 缩, y0 + 缩, 塔身高], [x0 + tw - 缩, y0 + 缩, 塔身高],
            [x0 + tw - 缩, y0 + tw - 缩, 塔身高], [x0 + 缩, y0 + tw - 缩, 塔身高],
            [x0 + 缩, y0 + 缩, 塔身高]]
    rs.AddLoftSrf([rs.AddPolyline(底), rs.AddPolyline(顶方)])

    # 四角竖向棱柱(管)：哥特竖向线条
    for px, py in [(x0, y0), (x0 + tw, y0), (x0 + tw, y0 + tw), (x0, y0 + tw)]:
        管(rs.AddLine([px, py, 0], [px, py, 塔身高]), 0.4)

    # 钟楼尖券窗：每面 1 个高窄 lancet
    win_w = tw * 0.34
    for off, 朝向, bx, by in [
        (None, "Y", x0 + tw / 2.0 - win_w / 2.0, y0 - 0.05),          # 前面
        (None, "X", x0 - 0.05, y0 + tw / 2.0 - win_w / 2.0),          # 左面
        (None, "X", x0 + tw + 0.05, y0 + tw / 2.0 - win_w / 2.0),     # 右面
    ]:
        c = 尖券窗闭合([bx, by, 塔身高 * 0.6], win_w, 塔身高 * 0.18, 朝向=朝向, 矢高比=0.9)
        s = rs.AddPlanarSrf(c)
        if s:
            rs.ObjectColor(s, [40, 45, 70])

    # 方 → 八边形 过渡（loft）
    顶方线 = rs.AddPolyline([顶方[0], 顶方[1], 顶方[2], 顶方[3], 顶方[0]])
    八半径 = (tw / 2.0 - 缩) * 0.95
    八线 = rs.AddPolyline(多边形(cx, cy, 八半径, 8, 塔身高 + 过渡高, 旋转=math.pi / 8))
    rs.AddLoftSrf([顶方线, 八线])

    # 八边形开放尖塔
    八边形尖塔(cx, cy, 塔身高 + 过渡高, 八半径, 尖顶高)

    # 四角小尖塔（pinnacle）
    for px, py in [(x0 + 缩, y0 + 缩), (x0 + tw - 缩, y0 + 缩),
                   (x0 + tw - 缩, y0 + tw - 缩), (x0 + 缩, y0 + tw - 缩)]:
        八边形尖塔(px, py, 塔身高, tw * 0.10, 尖顶高 * 0.30, 棱半径=0.12)


# =================== 飞扶壁 ===================
def 飞扶壁(墙x, 外x, y, 墙顶z, 墩顶z, 墩底z):
    """外侧扶壁墩 + 飞券(三点圆弧→管) + 墩顶小尖塔。"""
    # 扶壁墩（细高方柱）
    w = 1.4
    墩 = [[外x - w, y - w, 墩底z], [外x + w, y - w, 墩底z], [外x + w, y + w, 墩底z], [外x - w, y + w, 墩底z],
          [外x - w, y - w, 墩顶z], [外x + w, y - w, 墩顶z], [外x + w, y + w, 墩顶z], [外x - w, y + w, 墩顶z]]
    rs.AddBox(墩)
    # 墩顶小尖塔（增重稳定 + 装饰）
    八边形尖塔(外x, y, 墩顶z, w * 1.1, 6.0, 棱半径=0.12)
    # 飞券：从墩顶斜向上连到中殿墙顶，用三点圆弧做出拱
    起 = [外x, y, 墩顶z - 2.0]
    终 = [墙x, y, 墙顶z]
    中 = [(外x + 墙x) / 2.0, y, max(墩顶z, 墙顶z) + 4.0]
    弧 = rs.AddArc3Pt(起, 终, 中)
    管(弧, 0.6)
    # 飞券下方的承托小拱
    弧2 = rs.AddArc3Pt([外x, y, 墩顶z - 6.0], [墙x, y, 墙顶z - 5.0],
                       [(外x + 墙x) / 2.0, y, 墩顶z - 3.0])
    管(弧2, 0.4)


# =================== 耳堂（拉丁十字横翼）===================
def 建造耳堂(y_t, 臂深, 臂伸, 内x, 朝向, 墙高, 屋脊z, 中殿宽):
    """在中殿一侧伸出一条横翼(transept arm)。
    朝向 'L'：向 -X 伸；'R'：向 +X 伸。内x 为与中殿连接处的 X。"""
    y0 = y_t - 臂深 / 2.0
    y1 = y_t + 臂深 / 2.0
    if 朝向 == "L":
        外x = 内x - 臂伸
        端x = 外x
    else:
        外x = 内x + 臂伸
        端x = 外x
    xa, xb = min(内x, 外x), max(内x, 外x)

    # 横翼两侧长墙 + 实体
    准备图层("Dom_耳堂", [223, 214, 192])
    rs.AddBox([[xa, y0, 0], [xb, y0, 0], [xb, y1, 0], [xa, y1, 0],
               [xa, y0, 墙高], [xb, y0, 墙高], [xb, y1, 墙高], [xa, y1, 墙高]])

    # 端墙山花（朝外）
    脊y = y_t
    rs.AddSrfPt([[端x, y0, 墙高], [端x, y1, 墙高], [端x, 脊y, 屋脊z]])

    # 横翼坡屋顶（沿 X 方向起脊）
    准备图层("Dom_耳堂顶", [108, 64, 54])
    rs.AddSrfPt([[xa, y0, 墙高], [xb, y0, 墙高], [xb, 脊y, 屋脊z], [xa, 脊y, 屋脊z]])
    rs.AddSrfPt([[xa, y1, 墙高], [xb, y1, 墙高], [xb, 脊y, 屋脊z], [xa, 脊y, 屋脊z]])

    # 端立面玫瑰窗 + 尖券门
    准备图层("Dom_耳堂窗", [90, 130, 205])
    法向 = [-1, 0, 0] if 朝向 == "L" else [1, 0, 0]
    cz = 墙高 * 0.6
    eps = -0.4 if 朝向 == "L" else 0.4
    rs.AddCircle(rs.PlaneFromNormal([端x + eps, y_t, cz], 法向), 臂深 * 0.16)
    rs.AddCircle(rs.PlaneFromNormal([端x + eps, y_t, cz], 法向), 臂深 * 0.09)
    for k in range(12):
        a = 2 * math.pi * k / 12
        rs.AddLine([端x + eps, y_t + 臂深 * 0.09 * math.cos(a), cz + 臂深 * 0.09 * math.sin(a)],
                   [端x + eps, y_t + 臂深 * 0.16 * math.cos(a), cz + 臂深 * 0.16 * math.sin(a)])


# =================== 主程序 ===================
def 建造科隆大教堂(中殿宽=14.0, 侧廊宽=7.0, 开间=12.0, 开间数=5,
                   高侧墙=30.0, 拱矢高=10.0, 侧廊高=17.0,
                   塔宽=12.0, 塔身高=60.0, 塔过渡=12.0, 塔尖高=44.0):
    旧图层 = rs.CurrentLayer()

    nave_len = 开间 * 开间数
    cx0, cx1 = 0.0, 中殿宽                      # 中殿(central vessel) X 范围
    左廊x = cx0 - 侧廊宽
    右廊x = cx1 + 侧廊宽
    脊x = (cx0 + cx1) / 2.0
    crown = 高侧墙 + 拱矢高

    # ---------- 1) 中殿高侧墙（带高侧窗 clerestory）----------
    准备图层("Dom_中殿墙", [225, 216, 195])
    for wx0, wx1 in [(cx0 - 0.4, cx0), (cx1, cx1 + 0.4)]:
        墙 = [[wx0, 0, 侧廊高], [wx1, 0, 侧廊高], [wx1, nave_len, 侧廊高], [wx0, nave_len, 侧廊高],
              [wx0, 0, 高侧墙], [wx1, 0, 高侧墙], [wx1, nave_len, 高侧墙], [wx0, nave_len, 高侧墙]]
        rs.AddBox(墙)

    准备图层("Dom_高侧窗", [70, 110, 170])
    win_w = 开间 * 0.5
    for b in range(开间数):
        yc = b * 开间 + 开间 / 2.0 - win_w / 2.0
        for wx, 朝向 in [(cx0 - 0.45, "X"), (cx1 + 0.45, "X")]:
            c = 尖券窗闭合([wx, yc, 侧廊高 + 3.0], win_w, (高侧墙 - 侧廊高) * 0.45, 朝向=朝向, 矢高比=0.95)
            s = rs.AddPlanarSrf(c)
            if s:
                rs.ObjectColor(s, [60, 90, 150])

    # ---------- 2) 侧廊外墙（带尖券窗）+ 斜屋顶 ----------
    准备图层("Dom_侧廊墙", [220, 210, 188])
    for ox in [左廊x, 右廊x]:
        墙 = [[ox - 0.3, 0, 0], [ox + 0.3, 0, 0], [ox + 0.3, nave_len, 0], [ox - 0.3, nave_len, 0],
              [ox - 0.3, 0, 侧廊高], [ox + 0.3, 0, 侧廊高], [ox + 0.3, nave_len, 侧廊高], [ox - 0.3, nave_len, 侧廊高]]
        rs.AddBox(墙)

    准备图层("Dom_侧廊窗", [80, 120, 175])
    for b in range(开间数):
        yc = b * 开间 + 开间 / 2.0 - win_w / 2.0
        for ox in [左廊x - 0.35, 右廊x + 0.35]:
            c = 尖券窗闭合([ox, yc, 4.0], win_w, 侧廊高 * 0.4, 朝向="X", 矢高比=0.8)
            s = rs.AddPlanarSrf(c)
            if s:
                rs.ObjectColor(s, [70, 100, 160])

    准备图层("Dom_侧廊顶", [120, 75, 62])      # 单坡顶：外墙顶 → 中殿墙根
    rs.AddSrfPt([[左廊x, 0, 侧廊高], [左廊x, nave_len, 侧廊高],
                 [cx0, nave_len, 高侧墙 - 2], [cx0, 0, 高侧墙 - 2]])
    rs.AddSrfPt([[右廊x, 0, 侧廊高], [右廊x, nave_len, 侧廊高],
                 [cx1, nave_len, 高侧墙 - 2], [cx1, 0, 高侧墙 - 2]])

    # ---------- 3) 肋拱顶（每个开间一跨）----------
    准备图层("Dom_肋拱顶", [200, 195, 180])
    for b in range(开间数):
        y0 = b * 开间
        y1 = y0 + 开间
        肋拱顶一跨(cx0, cx1, y0, y1, 高侧墙, 拱矢高)
    # 最后一道横向拱肋
    管(尖拱曲线([cx0, nave_len, 高侧墙], [cx1, nave_len, 高侧墙],
              矢高比=拱矢高 / 中殿宽), 0.35)

    # ---------- 4) 飞扶壁（每开间两侧各一）----------
    准备图层("Dom_飞扶壁", [210, 200, 178])
    for b in range(开间数):
        y = b * 开间 + 开间 / 2.0
        飞扶壁(cx0, 左廊x - 4.0, y, 高侧墙 - 2, 侧廊高 + 8.0, 0.0)
        飞扶壁(cx1, 右廊x + 4.0, y, 高侧墙 - 2, 侧廊高 + 8.0, 0.0)

    # ---------- 5) 中殿陡坡主屋顶 ----------
    准备图层("Dom_主屋顶", [110, 65, 55])
    屋脊z = crown + 12.0
    rs.AddSrfPt([[cx0, 0, 高侧墙], [cx0, nave_len, 高侧墙],
                 [脊x, nave_len, 屋脊z], [脊x, 0, 屋脊z]])
    rs.AddSrfPt([[cx1, 0, 高侧墙], [cx1, nave_len, 高侧墙],
                 [脊x, nave_len, 屋脊z], [脊x, 0, 屋脊z]])
    rs.AddSrfPt([[cx0, nave_len, 高侧墙], [cx1, nave_len, 高侧墙], [脊x, nave_len, 屋脊z]])  # 东山墙

    # ---------- 6) 东端半圆室(chevet)：多边形后殿 + 放射小室 ----------
    准备图层("Dom_后殿", [222, 213, 192])
    apse_cx, apse_cy = 脊x, nave_len
    apse_r = 中殿宽 / 2.0 + 1.0
    # 取朝东的半圈(7 段)建后殿墙面
    底环2 = 多边形(apse_cx, apse_cy, apse_r, 14, 0.0, 旋转=-math.pi / 2)
    顶环2 = 多边形(apse_cx, apse_cy, apse_r, 14, 高侧墙 - 4.0, 旋转=-math.pi / 2)
    for i in range(7):
        rs.AddSrfPt([底环2[i], 底环2[i + 1], 顶环2[i + 1], 顶环2[i]])
    # 后殿半锥顶
    apex后 = [apse_cx, apse_cy, 屋脊z - 4.0]
    for i in range(7):
        rs.AddSrfPt([顶环2[i], 顶环2[i + 1], apex后])
    # 放射小礼拜室
    for i in range(3):
        a = -math.pi / 2 + (i + 2) * math.pi / 7
        ccx = apse_cx + apse_r * math.cos(a)
        ccy = apse_cy + apse_r * math.sin(a)
        八边形尖塔(ccx, ccy, 0.0, 2.2, 侧廊高 * 0.8, 棱半径=0.12)

    # ---------- 6b) 侧廊东端封闭墙 ----------
    准备图层("Dom_侧廊墙", [220, 210, 188])
    for ox0, ox1 in [(左廊x, cx0), (cx1, 右廊x)]:
        rs.AddBox([[ox0, nave_len - 0.4, 0], [ox1, nave_len - 0.4, 0],
                   [ox1, nave_len, 0], [ox0, nave_len, 0],
                   [ox0, nave_len - 0.4, 侧廊高], [ox1, nave_len - 0.4, 侧廊高],
                   [ox1, nave_len, 侧廊高], [ox0, nave_len, 侧廊高]])

    # ---------- 7) 双塔（西立面，紧贴立面、罩住侧廊西端）----------
    准备图层("Dom_双塔", [205, 196, 172])
    建造塔楼(左廊x, 0.0, 侧廊宽, 塔身高, 塔过渡, 塔尖高)        # 左塔覆盖左侧廊西端
    建造塔楼(cx1, 0.0, 侧廊宽, 塔身高, 塔过渡, 塔尖高)          # 右塔覆盖右侧廊西端

    # ---------- 8) 西立面（中殿段）+ 玫瑰窗 + 三座尖券门 ----------
    准备图层("Dom_西立面", [218, 209, 186])
    # 立面墙（中殿宽，实体盒到高侧墙）
    rs.AddBox([[cx0, -0.4, 0], [cx1, -0.4, 0], [cx1, 0, 0], [cx0, 0, 0],
               [cx0, -0.4, 高侧墙], [cx1, -0.4, 高侧墙], [cx1, 0, 高侧墙], [cx0, 0, 高侧墙]])
    rs.AddSrfPt([[cx0, -0.2, 高侧墙], [cx1, -0.2, 高侧墙], [脊x, -0.2, 屋脊z]])  # 三角山花

    准备图层("Dom_玫瑰窗", [90, 130, 205])
    玫瑰窗([脊x, -0.5, 高侧墙 * 0.66], 中殿宽 * 0.30, 花瓣数=16)

    准备图层("Dom_大门", [60, 45, 40])
    中门宽 = 中殿宽 * 0.34
    边门宽 = 中殿宽 * 0.18
    门位 = [
        (脊x - 中门宽 / 2.0, 中门宽, 高侧墙 * 0.34),          # 中央大门
        (cx0 + 中殿宽 * 0.10, 边门宽, 高侧墙 * 0.24),         # 左小门
        (cx1 - 中殿宽 * 0.10 - 边门宽, 边门宽, 高侧墙 * 0.24),  # 右小门
    ]
    for bx, w, sh in 门位:
        门 = 尖券窗闭合([bx, -0.5, 0], w, sh, 朝向="Y", 矢高比=0.85)
        s = rs.AddPlanarSrf(门)
        if s:
            rs.ObjectColor(s, [45, 32, 28])

    # ---------- 8b) 耳堂（拉丁十字横翼）----------
    y耳 = nave_len * 0.62
    臂伸 = 侧廊宽 + 6.0
    建造耳堂(y耳, 开间, 臂伸, 左廊x, "L", 高侧墙, 屋脊z, 中殿宽)
    建造耳堂(y耳, 开间, 臂伸, 右廊x, "R", 高侧墙, 屋脊z, 中殿宽)

    # ---------- 9) 交叉部屋脊小塔（flèche，置于十字交叉点）----------
    准备图层("Dom_屋脊小塔", [170, 158, 135])
    八边形尖塔(脊x, y耳, 屋脊z, 2.8, 30.0, 棱半径=0.18)

    # ---------- 10) 地面 ----------
    准备图层("Dom_地面", [165, 170, 165])
    rs.AddPlaneSurface([左廊x - 臂伸 - 14, -侧廊宽 - 18, -0.1],
                       (右廊x - 左廊x) + 2 * 臂伸 + 28, nave_len + 50)

    rs.CurrentLayer(旧图层)
    rs.Command("_-Zoom _Extents")

    print("✅ Lesson 9 完成：科隆大教堂（曲线→曲面 富层次版）")
    print(f"   开间数={开间数}, 中殿长={nave_len}, 中殿冠高={crown}, 塔总高≈{塔身高 + 塔过渡 + 塔尖高}")
    print("   含：肋拱顶 / 飞扶壁 / 八边形开放尖塔 / 高侧窗 / 玫瑰窗 / 后殿")
    print("   💡 改参数：开间数 加长中殿；塔尖高 让尖塔更挺拔；拱矢高 调拱顶起伏")


# =================== 玫瑰窗 ===================
def 玫瑰窗(中心, 半径, 花瓣数=16):
    cx, cy, cz = 中心
    rs.AddCircle(rs.PlaneFromNormal([cx, cy, cz], [0, 1, 0]), 半径)
    rs.AddCircle(rs.PlaneFromNormal([cx, cy, cz], [0, 1, 0]), 半径 * 0.62)
    rs.AddCircle(rs.PlaneFromNormal([cx, cy, cz], [0, 1, 0]), 半径 * 0.26)
    for k in range(花瓣数):
        a = 2 * math.pi * k / 花瓣数
        内 = [cx + 半径 * 0.26 * math.cos(a), cy, cz + 半径 * 0.26 * math.sin(a)]
        外 = [cx + 半径 * math.cos(a), cy, cz + 半径 * math.sin(a)]
        rs.AddLine(内, 外)
        pcx = cx + 半径 * 0.80 * math.cos(a)
        pcz = cz + 半径 * 0.80 * math.sin(a)
        rs.AddCircle(rs.PlaneFromNormal([pcx, cy, pcz], [0, 1, 0]), 半径 * 0.11)


# === 运行（改这些参数做出你自己的大教堂）===
建造科隆大教堂(
    中殿宽=14.0,
    侧廊宽=7.0,
    开间=12.0,
    开间数=5,       # 加大 → 中殿更长
    高侧墙=30.0,
    拱矢高=10.0,
    侧廊高=17.0,
    塔宽=12.0,
    塔身高=60.0,     # 改 72 让塔更高
    塔过渡=12.0,
    塔尖高=44.0,     # 改 56 让尖塔更尖锐
)

# ===== 建模方法小结（曲线 → 曲面）=====
# · 哥特尖拱 = 两段等边圆弧交于尖顶（尖拱曲线），是拱肋/拱券/窗头的共同母题
# · 肋拱顶   = min(双向正弦) 点阵 → NURBS 曲面(web) + 沿尖拱曲线的拱肋管
# · 飞扶壁   = 三点圆弧曲线 AddArc3Pt → AddPipe 成石券
# · 八边形尖塔 = 方→八边形 Loft 过渡 + 八条棱线管(开放骨架感) + 锥面
# · 玫瑰窗   = 同心圆 + 放射肋 + 一圈花瓣小圆
# 复杂建筑 = 少量“几何母题函数” + 循环阵列。改参数即得不同教堂。
#
# ===== 进阶练习 =====
# 1. 用 lesson_05 的 Brep 布尔，在墙上真正“挖”出窗洞（而非贴面）。
# 2. 给八边形尖塔加“尖瓣饰(crocket)”：沿棱线等距阵列小三角面。
# 3. 把肋拱顶 web 换成真正的四片独立腹板（按对角线分割）。
# 4. 导出 .3dm，作为课堂导入 UE5 的素材（文档第五部分）。
