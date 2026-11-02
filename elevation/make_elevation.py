"""校舎外観 立面図（写真からの推定） DXF 生成。単位 mm、実寸1:1、想定縮尺1/100(A3)。"""
import math, ezdxf
from ezdxf.addons.drawing import matplotlib as dmpl

# ---- 推定寸法（写真から比率推定。実測で書き換え可） ----
CORE_W = 3600          # 左端 階段室
BAY = 4500             # スパン
NB = 8                 # スパン数
COL = 600              # 柱幅（見付）
GL, FL2, FL3, RFL = 0, 3800, 7400, 11000
PARA = 12200           # パラペット天端
COL_TOP = 12500        # 柱頭
CORE_TOP = 13000
BAL_H = 1100           # バルコニー手摺壁高さ
SLAB = 200
CANOPY = (3000, 3300)  # 1F 庇鼻先

doc = ezdxf.new("R12")
doc.header["$DWGCODEPAGE"] = "ANSI_932"
doc.header["$INSUNITS"] = 4
for name, color in [("外形", 7), ("柱", 7), ("開口", 4), ("ブレース", 1),
                    ("庇", 5), ("設備", 3), ("寸法", 2), ("通り芯", 6), ("文字", 7)]:
    doc.layers.add(name, color=color)
doc.styles.add("JP", font="msgothic.ttc")
msp = doc.modelspace()

def L(p, q, layer): msp.add_line(p, q, dxfattribs={"layer": layer})
def R(x1, y1, x2, y2, layer):
    msp.add_polyline2d([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], close=True, dxfattribs={"layer": layer})
def T(s, x, y, h=250, layer="文字", align=None):
    t = msp.add_text(s, dxfattribs={"layer": layer, "height": h, "style": "JP"})
    if align: t.set_placement((x, y), align=align)
    else: t.dxf.insert = (x, y)

def window(x1, x2, y1, y2, panes=4, transom=None):
    R(x1, y1, x2, y2, "開口")
    w = (x2 - x1) / panes
    for i in range(1, panes): L((x1 + w*i, y1), (x1 + w*i, y2), "開口")
    if transom: L((x1, transom), (x2, transom), "開口")

def xbrace(x1, x2, y1, y2, t=300):
    """枠付きX形鉄骨ブレース（耐震補強）"""
    R(x1, y1, x2, y2, "ブレース")
    R(x1+t, y1+t, x2-t, y2-t, "ブレース")
    ix1, iy1, ix2, iy2 = x1+t, y1+t, x2-t, y2-t
    for (ax, ay, bx, by) in [(ix1, iy1, ix2, iy2), (ix1, iy2, ix2, iy1)]:
        dx, dy = bx-ax, by-ay; n = math.hypot(dx, dy)
        ox, oy = -dy/n*t/2, dx/n*t/2
        L((ax+ox, ay+oy), (bx+ox, by+oy), "ブレース")
        L((ax-ox, ay-oy), (bx-ox, by-oy), "ブレース")

x0 = CORE_W
xs = [x0 + BAY*i for i in range(NB + 1)]     # 通り芯
XE = xs[-1]

# ---- 外形・GL ----
L((-1500, GL), (XE + 1500, GL), "外形")
R(0, GL, CORE_W, CORE_TOP, "外形")               # 階段室
for y in (FL2+1500, FL3+1500):                    # 階段室 縦長窓
    R(CORE_W-900, y, CORE_W-500, y+1800, "開口")
for x in range(600, CORE_W-900, 600): L((x, GL), (x, CORE_TOP), "外形")  # パネル目地
R(x0, RFL - SLAB, XE, PARA, "外形")              # 最上部 庇・パラペット帯

# ---- 各スパン ----
for i in range(NB):
    a, b = xs[i] + COL/2, xs[i+1] - COL/2
    bay = i + 1
    # 2F・3F 手摺壁帯
    for fl in (FL2, FL3):
        if bay in (5,) or (bay == 6 and fl == FL2):
            continue
        R(a, fl - SLAB, b, fl + BAL_H, "外形")
    # 上階の窓（手摺壁上に見える部分）
    for fl, top in ((FL2, FL3 - SLAB), (FL3, RFL - SLAB)):
        braced = bay == 5 or (bay == 6 and fl == FL2)
        if braced:
            xbrace(a, b, fl - SLAB, top)
            window(a+600, b-600, fl+900, fl+2700, 4)
        else:
            window(a+300, b-300, fl+BAL_H, fl+2800, 4)
            L((a, top), (b, top), "外形")
    # 1F
    if bay <= 4:
        R(a, CANOPY[0], b, CANOPY[1], "庇")
        window(a, b, GL, CANOPY[0]-100, 5, transom=2400)
        if bay == 3:
            m = (a + b) / 2
            R(m-900, GL, m+900, 2400, "開口")       # 両開き扉
            L((m, GL), (m, 2400), "開口")
        if bay == 4:
            R(a+1300, GL, b-1300, 2400, "開口")
            L(((a+b)/2, GL), ((a+b)/2, 2400), "開口")
    elif bay in (5, 6):
        xbrace(a, b, GL, FL2 - SLAB)
        R(a+300, GL, b-300, 800, "外形")            # 腰壁
        window(a+700, b-700, 1000, 2600, 3)
    else:
        L((a, FL2 - SLAB), (b, FL2 - SLAB), "外形")
        window(a+300, b-300, 900, 2800, 4)
        if bay == 8:                                # 屋外機・囲いフェンス
            R(a+300, GL, a+2600, 1900, "設備")
            for k in range(1, 6):
                L((a+300+k*383, GL), (a+300+k*383, 1900), "設備")
            T("屋外機", a+1450, 2000, 200, "設備", ezdxf.enums.TextEntityAlignment.BOTTOM_CENTER)
    if bay == 4:
        L((xs[0], CANOPY[1]), (xs[4], CANOPY[1]), "庇")

# 柱
for x in xs:
    R(x - COL/2, GL, x + COL/2, COL_TOP, "柱")

# ---- 通り芯 ----
for k, x in enumerate(xs):
    L((x, -3000), (x, -900), "通り芯")
    msp.add_circle((x, -3400), 400, dxfattribs={"layer": "通り芯"})
    T(f"X{k+1}", x, -3400, 300, "通り芯", ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

# ---- 寸法（線＋文字で作図：JW_CAD互換重視） ----
def hdim(x1, x2, y):
    L((x1, y), (x2, y), "寸法")
    for x in (x1, x2):
        L((x, y-150), (x, y+150), "寸法"); L((x-100, y-100), (x+100, y+100), "寸法")
    T(f"{int(x2-x1):,}", (x1+x2)/2, y+80, 220, "寸法", ezdxf.enums.TextEntityAlignment.BOTTOM_CENTER)
def vdim(y1, y2, x, label=None):
    L((x, y1), (x, y2), "寸法")
    for y in (y1, y2):
        L((x-150, y), (x+150, y), "寸法"); L((x-100, y-100), (x+100, y+100), "寸法")
    t = msp.add_text(f"{int(y2-y1):,}", dxfattribs={"layer": "寸法", "height": 220, "style": "JP", "rotation": 90})
    t.set_placement((x-80, (y1+y2)/2), align=ezdxf.enums.TextEntityAlignment.BOTTOM_CENTER)

for i in range(NB): hdim(xs[i], xs[i+1], -1600)
hdim(0, CORE_W, -1600)
hdim(0, XE, -2400)  # 全長は下段
for y1, y2 in ((GL, FL2), (FL2, FL3), (FL3, RFL), (RFL, PARA)):
    vdim(y1, y2, XE + 1200)
vdim(GL, PARA, XE + 2200)
for y, s in ((GL, "GL"), (FL2, "2FL"), (FL3, "3FL"), (RFL, "RFL")):
    L((XE + 700, y), (XE + 1600, y), "寸法")
    T(s, XE + 2800, y, 250, "寸法")

# ---- 表題 ----
T("校舎 南面立面図（写真より推定）  S=1/100", 0, -4800, 400)
T("※寸法は写真比率からの推定値。スパン4,500・階高3,800/3,600/3,600を仮定。実測により要修正。", 0, -5400, 250)
T("※X形ブレース：耐震補強（枠付き鉄骨ブレース）  左手の別棟は省略", 0, -5850, 250)

out = "/home/user/ai_work/elevation/校舎立面図.dxf"
doc.saveas(out, encoding="cp932")

# プレビューPNG
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
font_manager.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams["font.family"] = "WenQuanYi Zen Hei"
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
doc.styles.get("JP").dxf.font = "wqy-zenhei.ttc"
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)
fig = plt.figure(figsize=(16, 7)); ax = fig.add_axes([0, 0, 1, 1])
Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(msp)
fig.savefig("/home/user/ai_work/elevation/preview.png", dpi=150, facecolor="white")
print("ok", out)
