"""复杂模板 1：能源央企年度汇报（虚构品牌「岳川能源」）。
考验点：
- 全部用母版 + 自定义版式 + 占位符搭建；页面上的标题占位符是空的，提示文字只在版式里
- 颜色、字体全部是主题引用（schemeClr / +mj-ea），不写死
- 非标准尺寸 10 × 5.625 英寸；母版右下角有曲线装饰，左上角 logo 在母版上
- 内容页有左侧章节导航条（当前章节高亮）、页码域、页脚占位
- 深色内容页用页面级背景 + 配色映射反色
- 示例页：多级要点、两栏、图文（图片占位符）、原生表格、原生图表、KPI 卡片、时间线
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter
from pptx import Presentation
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE, PP_PLACEHOLDER
from pptx.oxml.ns import qn
from pptx.util import Inches

import tpl_kit as K
from make_templates import OUT, drop_slide, grad, rgb, save

W, H = 10.0, 5.625
PX = (1920, 1080)
NAVY, BLUE, TEAL, AMBER = "0F2747", "0B5CAD", "00A19A", "F5A623"
COLORS = {"dk1": "1A1A1A", "lt1": "FFFFFF", "dk2": NAVY, "lt2": "EDF2F7", "accent1": BLUE, "accent2": TEAL,
          "accent3": AMBER, "accent4": "5B6B7F", "accent5": "8CC63F", "accent6": "E4572E",
          "hlink": BLUE, "folHlink": "5B6B7F"}


# ---------- 美术 ----------
def turbine(d, x, base, hgt, ang, col):
    d.polygon([(x - hgt * 0.018, base), (x + hgt * 0.018, base), (x + hgt * 0.007, base - hgt), (x - hgt * 0.007, base - hgt)],
              fill=col)
    cx, cy = x, base - hgt
    for k in range(3):
        a = math.radians(ang + k * 120)
        tip = (cx + math.cos(a) * hgt * 0.55, cy + math.sin(a) * hgt * 0.55)
        side = (cx + math.cos(a + 0.08) * hgt * 0.12, cy + math.sin(a + 0.08) * hgt * 0.12)
        d.polygon([(cx, cy), side, tip], fill=col)
    d.ellipse([cx - hgt * 0.025, cy - hgt * 0.025, cx + hgt * 0.025, cy + hgt * 0.025], fill=col)


def pylon(d, x, base, hgt, col, w=3):
    top, half = base - hgt, hgt * 0.16
    d.line([(x - half, base), (x - half * 0.25, top), (x + half * 0.25, top), (x + half, base)], fill=col, width=w)
    for k in range(1, 7):
        y = base - hgt * k / 7
        s = half * (1 - 0.75 * k / 7)
        d.line([(x - s, y), (x + s, y)], fill=col, width=max(1, w - 1))
        yn = base - hgt * (k - 1) / 7
        sn = half * (1 - 0.75 * (k - 1) / 7)
        d.line([(x - sn, yn), (x + s, y)], fill=col, width=1)
        d.line([(x + sn, yn), (x - s, y)], fill=col, width=1)
    for arm, aw in ((0.82, 0.55), (0.66, 0.42)):
        y = base - hgt * arm
        d.line([(x - hgt * aw * 0.5, y), (x + hgt * aw * 0.5, y)], fill=col, width=w)


def cover_photo():
    w, h = PX
    im = Image.new("RGB", PX)
    d = ImageDraw.Draw(im)
    stops = [(0, (8, 24, 52)), (0.45, (26, 70, 128)), (0.72, (232, 150, 92)), (0.8, (250, 196, 128)), (1, (60, 50, 60))]
    for y in range(h):
        t = y / h
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0)
                d.line([(0, y), (w, y)], fill=tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3)))
                break
    glow = Image.new("RGBA", PX, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([1300, 640, 1640, 980], fill=(255, 214, 150, 220))
    im = Image.alpha_composite(im.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(60)))
    d = ImageDraw.Draw(im)
    random.seed(7)
    ground = [(0, h)] + [(x, 880 + 18 * math.sin(x / 210) + random.uniform(-3, 3)) for x in range(0, w + 1, 12)] + [(w, h)]
    d.polygon(ground, fill=(16, 22, 38))
    for x, s, a in ((1050, 430, 12), (1250, 330, 47), (1420, 520, 80), (1630, 380, 25), (1790, 300, 66)):
        turbine(d, x, 890, s, a, (18, 26, 44))
    for x, s in ((160, 420), (520, 360), (820, 300)):
        pylon(d, x, 900, s, (18, 26, 44))
    for k in range(3):
        d.line([(160 + 60, 900 - 420 * 0.82 + k * 14), (520 - 60, 900 - 360 * 0.82 + 30 + k * 14)], fill=(30, 38, 58), width=2)
        d.line([(520 + 50, 900 - 360 * 0.82 + k * 14), (820 - 50, 900 - 300 * 0.82 + 30 + k * 14)], fill=(30, 38, 58), width=2)
    return save(im, "energy-cover.jpg")


def solar_photo(size=(900, 1080), name="energy-solar.jpg"):
    w, h = size
    im = grad("2D6FB8", "BFD9F2", size, vertical=True)
    d = ImageDraw.Draw(im)
    hz = int(h * 0.42)
    d.rectangle([0, hz, w, h], fill=(70, 96, 70))
    for row in range(9):
        t0, t1 = row / 9, (row + 0.78) / 9
        y0, y1 = hz + 20 + (h - hz) * t0 ** 1.6, hz + 20 + (h - hz) * t1 ** 1.6
        shrink0, shrink1 = 0.5 - 0.5 * t0 ** 1.2, 0.5 - 0.5 * t1 ** 1.2
        x0, x1 = w * shrink0 * 0.6, w * shrink1 * 0.6
        d.polygon([(x0, y0), (w - x0, y0), (w - x1, y1), (x1, y1)], fill=(24, 44, 92))
        n = 10
        for k in range(1, n):
            xa = x0 + (w - 2 * x0) * k / n
            xb = x1 + (w - 2 * x1) * k / n
            d.line([(xa, y0), (xb, y1)], fill=(120, 150, 200), width=1)
        d.line([((x0 + x1) / 2, (y0 + y1) / 2), (w - (x0 + x1) / 2, (y0 + y1) / 2)], fill=(120, 150, 200), width=1)
    return save(im, name)


def corner_waves():
    w, h = 1100, 460
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(9):
        pts = [(x, h - 40 - k * 26 - 70 * math.sin(x / 260 + k * 0.35) * (x / w)) for x in range(0, w + 1, 6)]
        d.line(pts, fill=rgb(BLUE) + (40 + k * 10,), width=3)
    path = os.path.join(os.path.dirname(save(Image.new("RGB", (2, 2)), "_tmp.jpg")), "energy-waves.png")
    im.save(path)
    return path


def logo(white=False):
    w, h = 560, 160
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c1 = (255, 255, 255, 255) if white else rgb(BLUE) + (255,)
    c2 = (255, 255, 255, 255) if white else rgb(TEAL) + (255,)
    d.ellipse([10, 20, 130, 140], outline=c1, width=10)
    for k, col in enumerate((c1, c2, c1)):
        y = 58 + k * 22
        d.arc([30, y - 26, 110, y + 26], 200, 340, fill=col, width=8)
    d.text((150, 22), "岳川能源", font=K.cjk_font(64, bold=True), fill=c1)
    d.text((152, 100), "YUECHUAN ENERGY", font=K.cjk_font(30), fill=c2)
    path = os.path.join(os.path.dirname(save(Image.new("RGB", (2, 2)), "_tmp.jpg")),
                        f"energy-logo{'-w' if white else ''}.png")
    im.save(path)
    return path


# ---------- 母版和版式 ----------
def build_master(prs, art):
    m = prs.slide_master
    K.master_text_styles(prs, (22, "tx2", True), [(16, "tx1"), (14, "tx1"), (12, "accent4")])
    K.style_ph(K.ph_of(m, PP_PLACEHOLDER.TITLE), 0.5, 0.14, 7.6, 0.52, anchor="m", align="l")
    K.style_ph(K.ph_of(m, PP_PLACEHOLDER.BODY), 0.5, 0.95, 9.0, 4.1)
    K.style_ph(K.ph_of(m, PP_PLACEHOLDER.FOOTER), 0.5, 5.27, 4.0, 0.25, prompt="岳川能源 · 内部资料 注意保密",
               size=8, color="accent4", align="l")
    K.style_ph(K.ph_of(m, PP_PLACEHOLDER.SLIDE_NUMBER), 8.9, 5.27, 0.6, 0.25, size=8, color="accent4", align="r")
    K.drop_ph(m, PP_PLACEHOLDER.DATE)
    tmp = prs.slides.add_slide(prs.slide_layouts[6])
    deco = [K.picture(tmp.shapes, art["waves"], W - 4.1, H - 1.72, 4.1),
            K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 0.5, 0.72, 9.0, 0.02, theme="accent1"),
            K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 0.5, 0.7, 1.1, 0.06, theme="accent2"),
            K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 0.5, 5.22, 9.0, 0.01, color="C9D3DF"),
            K.picture(tmp.shapes, art["logo"], 8.25, 0.2, 1.25)]
    K.move_to(m, tmp, deco)
    drop_slide(prs, tmp)


def build_layouts(prs, art):
    L = K.keep_layouts(prs, {0: "封面", 1: "标题和内容", 2: "章节", 3: "两栏内容", 5: "仅标题", 6: "空白",
                             8: "图片与文字", 10: "目录"})
    # 封面：整页照片 + 左侧深色渐隐 + 白色占位符
    lay = L["封面"]
    lay._element.set("showMasterSp", "0")
    tmp = prs.slides.add_slide(L["空白"])
    ov = K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 0, 0, W * 0.72, H)
    K.gradient(ov, [(0, "081834", 0.92), (0.7, "081834", 0.55), (1, "081834", 0)], angle=0)
    K.move_to(lay, tmp, [K.picture(tmp.shapes, art["cover"], 0, 0, W, H), ov,
                         K.picture(tmp.shapes, art["logo_w"], 0.6, 0.45, 1.6),
                         K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 0.62, 2.95, 0.9, 0.05, theme="accent3")])
    drop_slide(prs, tmp)
    K.style_ph(K.ph_of(lay, PP_PLACEHOLDER.CENTER_TITLE), 0.6, 1.75, 6.4, 1.1, prompt="单击此处添加标题",
               size=32, color="bg1", bold=True, font="+mj", align="l", anchor="b")
    K.style_ph(K.ph_of(lay, PP_PLACEHOLDER.SUBTITLE), 0.6, 3.15, 6.0, 0.8, prompt="单击此处添加副标题",
               size=14, color="lt2", font="+mn", align="l", bullets=False)
    K.drop_ph(lay, PP_PLACEHOLDER.DATE, PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER)

    # 章节：主题色满底，序号是正文占位符
    lay = L["章节"]
    lay._element.set("showMasterSp", "0")
    K.layout_bg(lay, theme="accent1")
    tmp = prs.slides.add_slide(L["空白"])
    ring = K.shape(tmp.shapes, MSO_SHAPE.DONUT, 6.3, 0.6, 4.6, 4.6, color="FFFFFF", alpha=0.07, adj=0.12)
    K.move_to(lay, tmp, [ring, K.picture(tmp.shapes, art["logo_w"], 8.3, 0.3, 1.25),
                         K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 1.0, 3.25, 0.7, 0.05, theme="accent3")])
    drop_slide(prs, tmp)
    K.style_ph(K.ph_of(lay, PP_PLACEHOLDER.TITLE), 1.0, 2.35, 6.5, 0.85, prompt="单击此处添加章节标题",
               size=32, color="bg1", bold=True, font="+mj", anchor="b", align="l")
    K.style_ph(K.ph_of(lay, PP_PLACEHOLDER.BODY), 1.0, 1.15, 3.0, 1.1, prompt="01", size=60, color="accent3",
               bold=True, font="+mj", bullets=False)
    K.drop_ph(lay, PP_PLACEHOLDER.DATE, PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER)

    # 目录：左侧照片，标题占位符在右上
    lay = L["目录"]
    lay._element.set("showMasterSp", "0")
    tmp = prs.slides.add_slide(L["空白"])
    K.move_to(lay, tmp, [K.picture(tmp.shapes, art["solar"], 0, 0, 3.4, H, crop=(0.1, 0, 0.1, 0)),
                         K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 3.4, 0, 0.08, H, theme="accent2")])
    drop_slide(prs, tmp)
    K.drop_ph(lay, PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.VERTICAL_BODY, PP_PLACEHOLDER.DATE, PP_PLACEHOLDER.FOOTER,
              PP_PLACEHOLDER.SLIDE_NUMBER)
    t = K.style_ph(K.ph_of(lay, None, idx=0), 4.1, 0.55, 4.0, 0.7, prompt="目录", size=30, color="tx2", bold=True,
                   font="+mj", align="l")
    t._element.find(".//" + qn("p:ph")).attrib.pop("orient", None)  # 原版式是竖排标题，改回横排
    t.text_frame._txBody.find(qn("a:bodyPr")).set("vert", "horz")

    for name in ("标题和内容", "两栏内容", "仅标题", "图片与文字"):
        lay = L[name]
        K.style_ph(K.ph_of(lay, None, idx=0), 0.5, 0.14, 7.6, 0.52, prompt="单击此处添加标题", anchor="m", align="l")
    K.style_ph(K.ph_of(L["标题和内容"], None, idx=1), 0.5, 0.95, 9.0, 4.1, prompt="单击此处编辑正文")
    two = [p for p in L["两栏内容"].placeholders if p.placeholder_format.idx in (1, 2)]
    K.style_ph(two[0], 0.5, 0.95, 4.35, 4.1, prompt="单击此处编辑正文")
    K.style_ph(two[1], 5.15, 0.95, 4.35, 4.1, prompt="单击此处编辑正文")
    lay = L["图片与文字"]
    K.style_ph(K.ph_of(lay, PP_PLACEHOLDER.PICTURE), 0.5, 0.95, 4.3, 4.1, prompt="单击图标添加图片")
    K.style_ph(K.ph_of(lay, PP_PLACEHOLDER.BODY), 5.1, 0.95, 4.4, 4.1, prompt="单击此处编辑正文", size=14)
    return L


# ---------- 页面 ----------
def tracker(shapes, current, names):
    """左侧章节导航：当前章节主题色底 + 白字，其余灰字"""
    items = [K.shape(shapes, MSO_SHAPE.RECTANGLE, 0, 0.85, 1.15, 4.3, theme="bg2")]
    for i, n in enumerate(names):
        y = 1.0 + i * 0.62
        if i == current:
            items.append(K.shape(shapes, MSO_SHAPE.RECTANGLE, 0, y, 1.15, 0.5, theme="accent1"))
        items.append(K.text(shapes, 0.08, y, 1.0, 0.5, n, size=10, theme="bg1" if i == current else "accent4",
                            bold=i == current, align="c", anchor="m", name=f"导航 {i + 1}"))
    return items


def slides(prs, L, art):
    # 0 封面：占位符里是示例字
    s = prs.slides.add_slide(L["封面"])
    s.shapes.title.text = "岳川能源202X年度工作汇报"
    K.ph_of(s, PP_PLACEHOLDER.SUBTITLE).text = "汇报人：XXX　|　202X年XX月"
    K.text(s.shapes, 0.62, 1.42, 5, 0.3, "ANNUAL WORK REPORT", size=11, color="F5C77E", spc=3, font="+mj")

    # 1 目录：5 个条目，每条是「圆底序号 + 条目」组合
    s = prs.slides.add_slide(L["目录"])
    s.shapes.title.text = "目录"
    K.text(s.shapes, 4.15, 1.08, 2, 0.3, "CONTENTS", size=12, theme="accent2", spc=2, font="+mj")
    for i in range(5):
        y = 1.55 + i * 0.72
        c = K.shape(s.shapes, MSO_SHAPE.OVAL, 4.15, y, 0.46, 0.46, theme="accent1")
        n = K.text(s.shapes, 4.15, y, 0.46, 0.46, f"{i + 1:02d}", size=12, theme="bg1", bold=True, align="c",
                   anchor="m", insets=(0, 0, 0, 0))
        t = K.text(s.shapes, 4.8, y, 4.2, 0.46, "目录标题内容", size=16, theme="tx2", bold=True, anchor="m")
        ln = K.shape(s.shapes, MSO_SHAPE.RECTANGLE, 4.8, y + 0.52, 4.3, 0.01, color="D5DCE6")
        K.group(s.shapes, [c, n, t, ln])

    # 2 章节：序号和标题都是占位符
    s = prs.slides.add_slide(L["章节"])
    K.ph_of(s, None, idx=1).text = "01"
    s.shapes.title.text = "章节标题"
    K.text(s.shapes, 1.0, 3.45, 6, 0.4, "在此输入本章节的简要说明", size=13, color="D6E4F5")

    # 3 内容：多级要点示例（标题占位符留空，只有版式里的提示文字）
    s = prs.slides.add_slide(L["标题和内容"])
    body = K.ph_of(s, None, idx=1).text_frame
    body.text = "一级要点：在此输入工作内容"
    for lvl, t in ((1, "二级要点：补充说明文字"), (1, "二级要点：补充说明文字"), (0, "一级要点：在此输入工作内容"),
                   (1, "二级要点：补充说明文字"), (2, "三级要点：数据来源或备注")):
        p = body.add_paragraph()
        p.text, p.level = t, lvl

    # 4 内容 + 左侧章节导航（页面上把标题占位符挪到导航右边）
    s = prs.slides.add_slide(L["仅标题"])
    tracker(s.shapes, 0, ["第一部分", "第二部分", "第三部分", "第四部分"])
    t = s.shapes.title
    t.left, t.top, t.width, t.height = Inches(1.45), Inches(0.14), Inches(6.6), Inches(0.52)

    # 5 两栏示例
    s = prs.slides.add_slide(L["两栏内容"])
    s.shapes.title.text = "两栏内容示例"
    for p in s.placeholders:
        if p.placeholder_format.idx in (1, 2):
            p.text_frame.text = "在此输入对比内容"
            p.text_frame.add_paragraph().text = "在此输入对比内容"

    # 6 图文示例：图片占位符里插了图
    s = prs.slides.add_slide(L["图片与文字"])
    s.shapes.title.text = "图文排版示例"
    K.ph_of(s, PP_PLACEHOLDER.PICTURE).insert_picture(art["solar2"])
    K.ph_of(s, PP_PLACEHOLDER.BODY).text_frame.text = "在此输入图片说明文字，建议不超过 80 字。"

    # 7 表格示例（原生表格，表头用主题色）
    s = prs.slides.add_slide(L["仅标题"])
    s.shapes.title.text = "表格示例"
    K.table(s.shapes, 0.5, 1.05, 9.0, 2.6, [["指标", "202X年", "202Y年", "同比"]] +
            [[f"指标名称{i}", "XX", "XX", "XX%"] for i in range(1, 6)])

    # 8 图表示例（原生柱状图，主题色系列）
    s = prs.slides.add_slide(L["仅标题"])
    s.shapes.title.text = "图表示例"
    K.chart(s.shapes, XL_CHART_TYPE.COLUMN_CLUSTERED, 0.5, 0.95, 9.0, 4.1, ["2021", "2022", "2023", "2024", "2025"],
            [("系列一", (4.3, 2.5, 3.5, 4.5, 5.0)), ("系列二", (2.4, 4.4, 1.8, 2.8, 3.2))], ["accent1", "accent2"])

    # 9 KPI 卡片示例：4 个组合
    s = prs.slides.add_slide(L["仅标题"])
    s.shapes.title.text = "核心指标示例"
    for i in range(4):
        x = 0.5 + i * 2.3
        card = K.shape(s.shapes, MSO_SHAPE.RECTANGLE, x, 1.2, 2.05, 3.2, theme="bg2")
        bar = K.shape(s.shapes, MSO_SHAPE.RECTANGLE, x, 1.2, 2.05, 0.06, theme="accent1" if i % 2 == 0 else "accent2")
        ic = K.shape(s.shapes, MSO_SHAPE.OVAL, x + 0.75, 1.55, 0.55, 0.55, theme="accent1" if i % 2 == 0 else "accent2")
        v = K.text(s.shapes, x, 2.3, 2.05, 0.7, "XX%", size=30, theme="accent1", bold=True, align="c", font="+mj")
        n = K.text(s.shapes, x, 3.0, 2.05, 0.4, "指标名称", size=14, theme="tx2", bold=True, align="c")
        dsc = K.text(s.shapes, x + 0.15, 3.45, 1.75, 0.8, "在此输入指标说明", size=10, theme="accent4", align="c")
        K.group(s.shapes, [card, bar, ic, v, n, dsc])

    # 10 深色内容页：页面背景 + 配色映射
    s = prs.slides.add_slide(L["仅标题"])
    K.layout_bg(s, theme="dk2")  # dk2 不受配色映射影响
    K.dark_color_map(s)

    # 11 时间线示例
    s = prs.slides.add_slide(L["仅标题"])
    s.shapes.title.text = "发展历程示例"
    K.shape(s.shapes, MSO_SHAPE.RECTANGLE, 0.7, 2.9, 8.6, 0.04, theme="accent1")
    for i in range(5):
        x = 0.75 + i * 1.8
        K.shape(s.shapes, MSO_SHAPE.OVAL, x + 0.55, 2.79, 0.26, 0.26, theme="accent2", line="FFFFFF", line_w=2)
        K.text(s.shapes, x, 2.1, 1.4, 0.5, "202X", size=18, theme="accent1", bold=True, align="c", font="+mj")
        K.text(s.shapes, x - 0.1, 3.25, 1.6, 0.9, "在此输入事件描述", size=11, theme="tx1", align="c")

    # 12 结尾：空白版式 + 页面上的照片和文字
    s = prs.slides.add_slide(L["空白"])
    s._element.set("showMasterSp", "0")
    K.picture(s.shapes, art["cover"], 0, 0, W, H)  # 结尾页不要页脚
    ov = K.shape(s.shapes, MSO_SHAPE.RECTANGLE, 0, 0, W, H)
    K.gradient(ov, [(0, "081834", 0.85), (1, "081834", 0.35)], angle=0)
    K.picture(s.shapes, art["logo_w"], 0.6, 0.45, 1.6)
    K.text(s.shapes, 0.6, 2.0, 7, 0.9, "谢谢聆听", size=40, theme="bg1", bold=True, font="+mj")
    K.text(s.shapes, 0.6, 2.9, 7, 0.5, "敬请批评指正", size=16, color="F5C77E", font="+mn")


def add_footers(prs):
    for i, s in enumerate(prs.slides):
        if s.slide_layout.name in ("标题和内容", "两栏内容", "仅标题", "图片与文字"):
            K.footer_phs(s, prs.slide_master, i + 1)


def make():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    K.set_theme(prs, "岳川能源", COLORS, ("Arial", "微软雅黑"), ("Arial", "微软雅黑"))
    art = {"cover": cover_photo(), "solar": solar_photo(), "solar2": solar_photo((1200, 1080), "energy-solar2.jpg"),
           "waves": corner_waves(), "logo": logo(), "logo_w": logo(white=True)}
    build_master(prs, art)
    L = build_layouts(prs, art)
    slides(prs, L, art)
    add_footers(prs)
    path = os.path.join(OUT, "energy-yuechuan.pptx")
    prs.save(path)
    return path


if __name__ == "__main__":
    print(make())
