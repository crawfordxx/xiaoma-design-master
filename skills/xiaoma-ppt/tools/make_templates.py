"""生成 examples/templates/ 下的 5 套行业模板（虚构品牌）。用法：python3 tools/make_templates.py
这些模板故意用了不同的构造方式（装饰在母版/版式上或页面上、标题用占位符或文本框、目录条目是组合、
标题压在深色色带上、背景图里有画），用来检验 skill 对真实世界模板的适应能力。
"""
import math
import os
import random

from lxml import etree
from PIL import Image, ImageDraw, ImageFilter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "examples", "templates")
ART = os.path.join(ROOT, "tools", "_art")
W, H = 13.333, 7.5
PX = (1920, 1080)


# ---------- pptx 小工具 ----------
def new_prs():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    return prs


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def hexc(c):
    return RGBColor.from_string(c)


def rect(sh, x, y, w, h, fill=None, radius=0, line=None, line_w=1, kind=None, alpha=None, name=None):
    kind = kind or (MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE)
    s = sh.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = hexc(fill)
        if alpha is not None:
            clr = s.fill._xPr.find(".//" + qn("a:srgbClr"))
            etree.SubElement(clr, qn("a:alpha"), val=str(int(alpha * 100000)))
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = hexc(line)
        s.line.width = Pt(line_w)
    else:
        s.line.fill.background()
    if name:
        s.name = name
    return s


def tb(sh, x, y, w, h, paras, size=18, color="333333", bold=False, font="微软雅黑", align="l", wrap=True,
       anchor="t", spacing=None, name=None):
    """paras: str 或 [(文字, {size,color,bold,font})...] 的段落列表"""
    s = sh.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = s.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    if isinstance(paras, str):
        paras = [(p, {}) for p in paras.split("\n")]
    for i, (t, o) in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[o.get("align", align)]
        if spacing:
            p.line_spacing = spacing
        r = p.add_run()
        r.text = t
        f = r.font
        f.size = Pt(o.get("size", size))
        f.bold = o.get("bold", bold)
        f.color.rgb = hexc(o.get("color", color))
        fn = o.get("font", font)
        f.name = fn
        rPr = r._r.get_or_add_rPr()
        ea = etree.SubElement(rPr, qn("a:ea"))
        ea.set("typeface", fn)
    if name:
        s.name = name
    return s


def line(sh, x1, y1, x2, y2, color, w=1.0):
    c = sh.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = hexc(color)
    c.line.width = Pt(w)
    return c


def picture(sh, path, x=0, y=0, w=W, h=H):
    return sh.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))


def to_layout(layout, slide, shapes):
    """把页面上画好的形状搬到版式上（模拟「装饰做在母版/版式里」的模板）"""
    tree = layout.shapes._spTree
    for s in shapes:
        el = s._element
        for blip in el.iter(qn("a:blip")):
            rid = blip.get(qn("r:embed"))
            part = slide.part.related_part(rid)
            blip.set(qn("r:embed"), layout.part.relate_to(part, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"))
        tree.append(el)


def drop_slide(prs, slide):
    """删掉临时页（连同关系，避免文件里留下孤儿页）"""
    lst = prs.slides._sldIdLst
    for sid in list(lst):
        if prs.part.related_part(sid.get(qn("r:id"))) is slide.part:
            prs.part.drop_rel(sid.get(qn("r:id")))
            lst.remove(sid)


def ph_title(slide, x, y, w, h, text, size, color, font, bold=True):
    """用占位符做标题（模拟「标题是占位符」的模板）"""
    t = slide.shapes.title
    t.left, t.top, t.width, t.height = Inches(x), Inches(y), Inches(w), Inches(h)
    t.text_frame.text = text
    tf = t.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.runs[0]
    r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(size), bold, hexc(color), font
    etree.SubElement(r._r.get_or_add_rPr(), qn("a:ea")).set("typeface", font)
    return t


# ---------- PIL 美术 ----------
def rgb(c):
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def grad(c1, c2, size=PX, vertical=False):
    w, h = size
    im = Image.new("RGB", size)
    a, b = rgb(c1), rgb(c2)
    d = ImageDraw.Draw(im)
    n = h if vertical else w
    for i in range(n):
        t = i / (n - 1)
        c = tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3))
        if vertical:
            d.line([(0, i), (w, i)], fill=c)
        else:
            d.line([(i, 0), (i, h)], fill=c)
    return im


def save(im, name):
    os.makedirs(ART, exist_ok=True)
    p = os.path.join(ART, name)
    im.convert("RGB").save(p, quality=88)
    return p


def blobs(base, specs, blur=90):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for (cx, cy, r, c, a) in specs:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb(c) + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base.convert("RGBA"), layer)


def mountains(size, layers, seed=3):
    """水墨远山：多层正弦叠加的山脊线，越远越淡越模糊"""
    random.seed(seed)
    w, h = size
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    for (base_y, amp, color, alpha, blur) in layers:
        ph = [random.uniform(0, 6.28) for _ in range(4)]
        fr = [random.uniform(0.8, 1.6), random.uniform(2.5, 4), random.uniform(6, 9), random.uniform(13, 18)]
        am = [1, 0.45, 0.2, 0.08]
        pts = [(0, h)]
        for x in range(0, w + 1, 4):
            t = x / w
            yy = base_y - amp * sum(am[i] * math.sin(t * fr[i] * 3.14 + ph[i]) for i in range(4))
            pts.append((x, yy))
        pts.append((w, h))
        lay = Image.new("RGBA", size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon(pts, fill=rgb(color) + (alpha,))
        # 山体下半部分渐隐，像雾
        fade = Image.new("L", size, 0)
        fd = ImageDraw.Draw(fade)
        for y in range(h):
            fd.line([(0, y), (w, y)], fill=int(255 * max(0, min(1, 1 - (y - base_y) / (h - base_y + 1) * 0.9))))
        lay.putalpha(Image.composite(lay.split()[3], Image.new("L", size, 0), fade))
        out = Image.alpha_composite(out, lay.filter(ImageFilter.GaussianBlur(blur)))
    return out


def paper(size, c="F6F1E7", seed=1):
    random.seed(seed)
    im = Image.new("RGB", size, rgb(c))
    noise = Image.effect_noise(size, 10).convert("L")
    tex = Image.merge("RGB", [noise] * 3)
    return Image.blend(im, tex.point(lambda v: v), 0.035)


# ======================================================================
# 1. 金融：睿信资本 —— 深海军蓝 + 金色，衬线标题，直角。装饰放在版式上，标题用文本框。
# ======================================================================
def finance():
    NAVY, NAVY2, GOLD, INK, GRAY = "0B1F3A", "15325C", "C9A45C", "1B2433", "8A94A6"
    SERIF = "思源宋体"
    prs = new_prs()
    # 封面/章节/结尾共用的深色背景：渐变 + 金色几何线
    im = grad(NAVY, NAVY2)
    d = ImageDraw.Draw(im)
    for i in range(14):
        x0 = 1150 + i * 58
        d.line([(x0, 1080), (x0 + 520, 0)], fill=rgb("B89650") + (0,), width=1)
    for i in range(7):
        r = 240 + i * 70
        d.arc([1500 - r, 820 - r, 1500 + r, 820 + r], 180, 300, fill=rgb("8C7542"), width=1)
    dark_bg = save(im, "fin-dark.jpg")
    light = Image.new("RGB", PX, (255, 255, 255))
    dl = ImageDraw.Draw(light)
    for i in range(6):
        dl.line([(1700 + i * 40, 1080), (1920, 1080 - (220 - i * 40) * 2)], fill=rgb("EFE6D2"), width=2)
    light_bg = save(light, "fin-light.jpg")

    def logo(sh, x, y, dark=True):
        rect(sh, x, y + 0.04, 0.26, 0.26, fill=GOLD)
        tb(sh, x + 0.34, y - 0.04, 2.6, 0.5, [("睿信资本", {"size": 14, "bold": True, "color": "FFFFFF" if dark else NAVY,
                                                         "font": SERIF})], wrap=False, name="logo")

    # 版式：深色页（背景 + logo 放进版式）
    lay_dark, lay_light = prs.slide_layouts[6], prs.slide_layouts[5]
    tmp = blank(prs)
    to_layout(lay_dark, tmp, [picture(tmp.shapes, dark_bg)])
    # 内容版式：白底 + 页脚线 + 页脚文字 + 右下角金色装饰
    tmp2 = blank(prs)
    shapes = [picture(tmp2.shapes, light_bg), rect(tmp2.shapes, 0.6, 6.92, W - 1.2, 0.012, fill="D9DEE7"),
              tb(tmp2.shapes, 0.6, 6.98, 6, 0.3, [("睿信资本 · 内部资料 · 请勿外传", {"size": 9, "color": GRAY})])]
    to_layout(lay_light, tmp2, shapes)
    for sp in list(lay_light.placeholders):
        sp._element.getparent().remove(sp._element)
    for s in (tmp, tmp2):
        drop_slide(prs, s)
    # 1 封面
    s = prs.slides.add_slide(lay_dark)
    logo(s.shapes, 0.8, 0.6)
    rect(s.shapes, 0.8, 2.55, 0.9, 0.05, fill=GOLD)
    tb(s.shapes, 0.8, 2.8, 8.5, 1.2, [("报告主标题", {"size": 44, "bold": True, "color": "FFFFFF", "font": SERIF})])
    tb(s.shapes, 0.8, 4.0, 8.5, 0.6, [("副标题：请输入副标题内容", {"size": 20, "color": GOLD})])
    tb(s.shapes, 0.8, 6.3, 6, 0.4, [("汇报人：XXX　|　2026.10", {"size": 13, "color": "AEB8CA"})])
    # 2 目录：左侧深蓝面板
    s = prs.slides.add_slide(lay_light)
    rect(s.shapes, 0, 0, 4.3, H, fill=NAVY)
    tb(s.shapes, 0.8, 2.6, 3, 0.9, [("目录", {"size": 40, "bold": True, "color": "FFFFFF", "font": SERIF})])
    tb(s.shapes, 0.8, 3.45, 3, 0.5, [("CONTENTS", {"size": 16, "color": GOLD})], wrap=False)
    for i in range(5):
        y = 1.15 + i * 1.08
        tb(s.shapes, 5.2, y, 1.0, 0.7, [(f"{i + 1:02d}", {"size": 30, "bold": True, "color": GOLD, "font": SERIF})])
        tb(s.shapes, 6.3, y + 0.12, 6, 0.6, [("目录标题", {"size": 22, "bold": True, "color": INK})])
        line(s.shapes, 5.2, y + 0.88, 12.4, y + 0.88, "E3E7EE", 0.75)
    # 3 章节
    s = prs.slides.add_slide(lay_dark)
    logo(s.shapes, 0.8, 0.6)
    tb(s.shapes, 0.8, 2.0, 3, 1.6, [("01", {"size": 96, "bold": True, "color": GOLD, "font": SERIF})], wrap=False)
    rect(s.shapes, 0.85, 3.75, 0.6, 0.04, fill=GOLD)
    tb(s.shapes, 0.8, 3.95, 8, 0.9, [("章节标题", {"size": 36, "bold": True, "color": "FFFFFF", "font": SERIF})])
    tb(s.shapes, 0.8, 4.85, 8, 0.5, [("章节副标题", {"size": 16, "color": "AEB8CA"})])
    # 4 内容页：标题 + 金色短线 + 右上编号
    s = prs.slides.add_slide(lay_light)
    tb(s.shapes, 0.6, 0.45, 1, 0.4, [("01", {"size": 14, "bold": True, "color": GOLD})], wrap=False)
    tb(s.shapes, 0.6, 0.75, 10.5, 0.7, [("页面标题", {"size": 26, "bold": True, "color": NAVY, "font": SERIF})])
    rect(s.shapes, 0.62, 1.48, 0.55, 0.045, fill=GOLD)
    tb(s.shapes, 11.2, 0.5, 1.6, 0.35, [("RUIXIN CAPITAL", {"size": 9, "color": GRAY})], align="r", wrap=False)
    for i in range(3):
        x = 0.6 + i * 4.1
        rect(s.shapes, x, 2.1, 3.8, 3.9, fill="F5F6F8")
        tb(s.shapes, x + 0.3, 2.4, 3.2, 0.5, [("标题文字", {"size": 18, "bold": True, "color": NAVY})])
        tb(s.shapes, x + 0.3, 3.0, 3.2, 2.5, [("请在此处输入具体内容，建议精炼概括。", {"size": 13, "color": GRAY})])
    # 5 内容页（深色版，用于观点/金句）
    s = prs.slides.add_slide(lay_dark)
    tb(s.shapes, 0.6, 0.45, 1, 0.4, [("01", {"size": 14, "bold": True, "color": GOLD})], wrap=False)
    tb(s.shapes, 0.6, 0.75, 10.5, 0.7, [("页面标题", {"size": 26, "bold": True, "color": "FFFFFF", "font": SERIF})])
    rect(s.shapes, 0.62, 1.48, 0.55, 0.045, fill=GOLD)
    # 6 结尾
    s = prs.slides.add_slide(lay_dark)
    logo(s.shapes, 0.8, 0.6)
    tb(s.shapes, 0.8, 2.8, 8, 1.2, [("感谢聆听", {"size": 48, "bold": True, "color": "FFFFFF", "font": SERIF})])
    tb(s.shapes, 0.8, 4.0, 8, 0.5, [("THANK YOU", {"size": 18, "color": GOLD})], wrap=False)
    tb(s.shapes, 0.8, 6.3, 8, 0.4, [("睿信资本 · 让每一份资产都被认真对待", {"size": 13, "color": "AEB8CA"})])
    prs.save(os.path.join(OUT, "finance-ruixin.pptx"))


# ======================================================================
# 2. 医疗：康宁医疗 —— 白 + 青绿，圆角。内容页标题是占位符；目录条目是「组合」。
# ======================================================================
def medical():
    TEAL, TEAL_D, MINT, INK, GRAY = "0E9AA7", "0B5563", "3CC6B0", "17323A", "7C8F94"
    prs = new_prs()
    base = Image.new("RGB", PX, (255, 255, 255))
    cover = blobs(base, [(1650, 300, 420, TEAL, 140), (1400, 900, 360, MINT, 120), (1850, 950, 300, "8FE3D6", 160)],
                  110)
    cover_bg = save(cover, "med-cover.jpg")
    sec = blobs(grad("0E9AA7", "0B6F7C"), [(1600, 200, 380, "3CC6B0", 120), (300, 1000, 300, "13B5C2", 120)], 120)
    d = ImageDraw.Draw(sec)
    for i in range(5):
        r = 120 + i * 90
        d.ellipse([1560 - r, 540 - r, 1560 + r, 540 + r], outline=(255, 255, 255, 40), width=2)
    sec_bg = save(sec, "med-section.jpg")
    corner = blobs(Image.new("RGB", PX, (255, 255, 255)), [(1980, 1150, 260, MINT, 110)], 80)
    content_bg = save(corner, "med-content.jpg")

    def cross(sh, x, y, s=0.3, c=TEAL):
        rect(sh, x + s / 3, y, s / 3, s, fill=c, radius=0.2)
        rect(sh, x, y + s / 3, s, s / 3, fill=c, radius=0.2)

    def logo(sh, x, y, c=TEAL_D):
        cross(sh, x, y + 0.05)
        tb(sh, x + 0.42, y - 0.02, 2.5, 0.45, [("康宁医疗集团", {"size": 13, "bold": True, "color": c})], wrap=False)

    lay_title = prs.slide_layouts[5]  # Title Only：内容页用它的标题占位符
    # 1 封面
    s = blank(prs)
    picture(s.shapes, cover_bg)
    logo(s.shapes, 0.8, 0.6)
    tb(s.shapes, 0.8, 2.4, 7.5, 1.6, [("在此输入标题", {"size": 42, "bold": True, "color": TEAL_D})], spacing=1.1)
    tb(s.shapes, 0.8, 4.1, 7.5, 0.6, [("请输入副标题", {"size": 20, "color": TEAL})])
    rect(s.shapes, 0.8, 5.2, 2.6, 0.5, fill=TEAL, radius=0.5)
    tb(s.shapes, 0.8, 5.24, 2.6, 0.45, [("2026年10月", {"size": 14, "color": "FFFFFF", "bold": True})], align="c")
    # 2 目录：2×3 圆角卡片，每张卡片是一个组合
    s = blank(prs)
    rect(s.shapes, 0, 0, W, H, fill="F2FAF9")
    tb(s.shapes, 0.8, 0.7, 4, 0.8, [("目录", {"size": 34, "bold": True, "color": TEAL_D})])
    tb(s.shapes, 0.8, 1.4, 4, 0.4, [("CONTENTS", {"size": 14, "color": TEAL})], wrap=False)
    for i in range(6):
        r, c = divmod(i, 3)
        x, y = 0.8 + c * 4.0, 2.35 + r * 2.15
        g = s.shapes.add_group_shape()
        rect(g.shapes, x, y, 3.7, 1.85, fill="FFFFFF", radius=0.12)
        rect(g.shapes, x + 0.3, y + 0.3, 0.7, 0.7, fill=TEAL, kind=MSO_SHAPE.OVAL)
        tb(g.shapes, x + 0.3, y + 0.42, 0.7, 0.45, [(f"{i + 1:02d}", {"size": 16, "bold": True, "color": "FFFFFF"})],
           align="c")
        tb(g.shapes, x + 1.2, y + 0.38, 2.4, 0.55, [("目录标题", {"size": 18, "bold": True, "color": INK})])
        tb(g.shapes, x + 1.2, y + 0.95, 2.4, 0.6, [("简要说明", {"size": 12, "color": GRAY})])
    # 3 章节
    s = blank(prs)
    picture(s.shapes, sec_bg)
    rect(s.shapes, 1.0, 2.35, 1.5, 1.5, fill="FFFFFF", kind=MSO_SHAPE.OVAL)
    tb(s.shapes, 1.0, 2.68, 1.5, 0.9, [("01", {"size": 40, "bold": True, "color": TEAL})], align="c")
    tb(s.shapes, 2.9, 2.45, 8, 0.9, [("章节标题", {"size": 38, "bold": True, "color": "FFFFFF"})])
    tb(s.shapes, 2.9, 3.35, 8, 0.5, [("章节副标题", {"size": 16, "color": "D5F3EF"})])
    # 4 内容页（标题占位符 + 左侧竖条 + 右上 logo）
    s = prs.slides.add_slide(lay_title)
    pic = picture(s.shapes, content_bg)  # 背景图放到最底层
    s.shapes._spTree.remove(pic._element)
    s.shapes._spTree.insert(2, pic._element)
    rect(s.shapes, 0.6, 0.62, 0.09, 0.55, fill=TEAL, radius=0.5)
    ph_title(s, 0.85, 0.5, 9.5, 0.8, "单击此处添加标题", 26, INK, "微软雅黑")
    logo(s.shapes, 10.5, 0.62)
    rect(s.shapes, 0.85, 1.95, 5.6, 4.6, fill="F2FAF9", radius=0.06)
    tb(s.shapes, 1.15, 2.2, 5, 0.5, [("小标题", {"size": 18, "bold": True, "color": TEAL_D})])
    tb(s.shapes, 1.15, 2.8, 5, 3, [("此处输入正文内容。", {"size": 14, "color": GRAY})])
    # 5 结尾
    s = blank(prs)
    picture(s.shapes, sec_bg)
    logo(s.shapes, 0.8, 0.6, "FFFFFF")
    tb(s.shapes, 0.8, 2.7, 8, 1.1, [("感谢聆听", {"size": 46, "bold": True, "color": "FFFFFF"})])
    tb(s.shapes, 0.8, 3.8, 8, 0.5, [("守护每一份健康", {"size": 18, "color": "D5F3EF"})])
    prs.save(os.path.join(OUT, "medical-kangning.pptx"))


# ======================================================================
# 3. 教育：启明教育 —— 暖色（奶油底 + 橙 + 棕），大圆角，点阵涂鸦。
# ======================================================================
def education():
    CREAM, ORANGE, BROWN, YELLOW, GRAY = "FFF6EC", "F2762E", "4A2C1D", "FFC24B", "9A7B67"
    prs = new_prs()

    def dots(im, x0, y0, cols, rows, gap, r, c):
        d = ImageDraw.Draw(im)
        for i in range(cols):
            for j in range(rows):
                d.ellipse([x0 + i * gap - r, y0 + j * gap - r, x0 + i * gap + r, y0 + j * gap + r], fill=rgb(c))

    im = Image.new("RGB", PX, rgb(CREAM))
    d = ImageDraw.Draw(im)
    d.ellipse([1240, 200, 2200, 1160], fill=rgb(ORANGE))
    d.ellipse([1420, 380, 2020, 980], fill=rgb("F59A5C"))
    d.ellipse([1180, 120, 1300, 240], fill=rgb(YELLOW))
    dots(im, 120, 880, 8, 3, 34, 5, "F4C9A6")
    d.arc([1050, 820, 1350, 1000], 200, 340, fill=rgb(BROWN), width=6)
    cover_bg = save(im, "edu-cover.jpg")
    im = Image.new("RGB", PX, rgb(CREAM))
    dots(im, 1700, 60, 6, 4, 30, 4, "F6D3B5")
    content_bg = save(im, "edu-content.jpg")
    im = Image.new("RGB", PX, rgb(ORANGE))
    d = ImageDraw.Draw(im)
    d.ellipse([-300, 500, 700, 1500], fill=rgb("F48A48"))
    dots(im, 1500, 820, 9, 5, 34, 5, "F9B58A")
    sec_bg = save(im, "edu-section.jpg")

    def brand(sh, x, y, c=BROWN):
        rect(sh, x, y + 0.04, 0.3, 0.3, fill=ORANGE, kind=MSO_SHAPE.OVAL)
        tb(sh, x + 0.4, y - 0.02, 2.2, 0.45, [("启明教育", {"size": 14, "bold": True, "color": c})], wrap=False)

    # 1 封面
    s = blank(prs)
    picture(s.shapes, cover_bg)
    brand(s.shapes, 0.8, 0.6)
    tb(s.shapes, 0.8, 2.3, 7.4, 1.8, [("课程标题", {"size": 46, "bold": True, "color": BROWN})], spacing=1.05)
    rect(s.shapes, 0.8, 4.25, 4.2, 0.6, fill=ORANGE, radius=0.5)
    tb(s.shapes, 0.8, 4.3, 4.2, 0.5, [("副标题 / 课程模块", {"size": 18, "bold": True, "color": "FFFFFF"})], align="c")
    tb(s.shapes, 0.8, 5.3, 6, 0.4, [("主讲人：XXX　　2026 年秋季", {"size": 14, "color": GRAY})])
    # 2 目录：左列表 + 右侧大圆
    s = blank(prs)
    picture(s.shapes, content_bg)
    tb(s.shapes, 0.8, 0.7, 4, 0.9, [("目录", {"size": 36, "bold": True, "color": BROWN})])
    tb(s.shapes, 2.3, 0.92, 3, 0.5, [("CONTENTS", {"size": 14, "bold": True, "color": ORANGE})], wrap=False)
    for i in range(5):
        y = 1.85 + i * 1.0
        rect(s.shapes, 0.8, y, 0.62, 0.62, fill=ORANGE if i % 2 == 0 else YELLOW, kind=MSO_SHAPE.OVAL)
        tb(s.shapes, 0.8, y + 0.1, 0.62, 0.45, [(f"{i + 1:02d}", {"size": 15, "bold": True, "color": "FFFFFF"})],
           align="c")
        tb(s.shapes, 1.65, y + 0.06, 6.5, 0.55, [("目录标题", {"size": 21, "bold": True, "color": BROWN})])
    rect(s.shapes, 8.9, 1.5, 4.8, 4.8, fill="FBD9BD", kind=MSO_SHAPE.OVAL)
    rect(s.shapes, 9.7, 2.3, 3.2, 3.2, fill=ORANGE, kind=MSO_SHAPE.OVAL)
    # 3 章节
    s = blank(prs)
    picture(s.shapes, sec_bg)
    tb(s.shapes, 0.9, 1.6, 3, 1.5, [("01", {"size": 88, "bold": True, "color": "FFFFFF"})], wrap=False)
    tb(s.shapes, 0.9, 3.25, 9, 1.0, [("章节标题", {"size": 40, "bold": True, "color": "FFFFFF"})])
    tb(s.shapes, 0.9, 4.25, 9, 0.5, [("这一章你会学到什么", {"size": 18, "color": "FFE6D3"})])
    # 4 内容页
    s = blank(prs)
    picture(s.shapes, content_bg)
    tb(s.shapes, 0.8, 0.55, 10, 0.75, [("页面标题", {"size": 28, "bold": True, "color": BROWN})])
    rect(s.shapes, 0.82, 1.32, 0.9, 0.08, fill=ORANGE, radius=0.5)
    brand(s.shapes, 11.0, 0.62)
    for i in range(2):
        rect(s.shapes, 0.8 + i * 6.0, 1.9, 5.7, 4.6, fill="FFFFFF", radius=0.08)
        tb(s.shapes, 1.1 + i * 6.0, 2.2, 5, 0.5, [("小标题", {"size": 18, "bold": True, "color": ORANGE})])
        tb(s.shapes, 1.1 + i * 6.0, 2.8, 5, 3, [("在此输入正文内容", {"size": 14, "color": GRAY})])
    tb(s.shapes, 12.2, 6.9, 0.8, 0.35, [("‹ 启明 ›", {"size": 9, "color": GRAY})], align="r", wrap=False)
    # 5 结尾
    s = blank(prs)
    picture(s.shapes, cover_bg)
    brand(s.shapes, 0.8, 0.6)
    tb(s.shapes, 0.8, 2.6, 7, 1.1, [("下课啦，谢谢大家", {"size": 44, "bold": True, "color": BROWN})])
    tb(s.shapes, 0.8, 3.75, 7, 0.5, [("课后作业见学习群", {"size": 18, "color": ORANGE})])
    prs.save(os.path.join(OUT, "education-qiming.pptx"))


# ======================================================================
# 4. 制造：华铸智造 —— 石墨 + 安全橙，直角，蓝图网格。内容页标题压在深色页眉带上。
# ======================================================================
def manufacturing():
    GRAPH, GRAPH2, ORANGE, STEEL, LIGHT = "1E252B", "2A333B", "FF6B1A", "9AA5B1", "F3F4F6"
    prs = new_prs()
    im = grad(GRAPH, GRAPH2)
    d = ImageDraw.Draw(im)
    for x in range(0, 1920, 48):
        d.line([(x, 0), (x, 1080)], fill=(52, 62, 70), width=1)
    for y in range(0, 1080, 48):
        d.line([(0, y), (1920, y)], fill=(52, 62, 70), width=1)
    for i in range(6):  # 右下角安全斜纹
        x0 = 1500 + i * 70
        d.polygon([(x0, 1080), (x0 + 35, 1080), (x0 + 35 + 220, 860), (x0 + 220, 860)], fill=rgb(ORANGE))
    d.ellipse([1300, 180, 1800, 680], outline=(90, 104, 115), width=3)
    d.ellipse([1420, 300, 1680, 560], outline=(90, 104, 115), width=3)
    for k in range(12):
        a = k * math.pi / 6
        d.line([(1550 + 250 * math.cos(a), 430 + 250 * math.sin(a)), (1550 + 290 * math.cos(a), 430 + 290 * math.sin(a))],
               fill=(90, 104, 115), width=10)
    dark_bg = save(im, "mfg-dark.jpg")
    lay_content = prs.slide_layouts[6]
    # 内容页的页眉带 + 橙色小方块 + 页脚线放在「母版」上（所有用空白版式的页都会显示）——这里只放在专用版式上
    lay = prs.slide_layouts[5]
    tmp = blank(prs)
    deco = [rect(tmp.shapes, 0, 0, W, H, fill=LIGHT), rect(tmp.shapes, 0, 0, W, 1.15, fill=GRAPH),
            rect(tmp.shapes, 0, 1.15, W, 0.06, fill=ORANGE), rect(tmp.shapes, 0.6, 7.05, 1.2, 0.05, fill=ORANGE),
            tb(tmp.shapes, 9.8, 6.95, 2.9, 0.3, [("HUAZHU SMART MANUFACTURING", {"size": 8, "color": STEEL})],
               align="r", wrap=False)]
    to_layout(lay, tmp, deco)
    for sp in list(lay.placeholders):
        sp._element.getparent().remove(sp._element)
    drop_slide(prs, tmp)

    def brand(sh, x, y):
        rect(sh, x, y + 0.06, 0.24, 0.24, fill=ORANGE)
        tb(sh, x + 0.34, y - 0.02, 2.4, 0.45, [("华铸智造", {"size": 14, "bold": True, "color": "FFFFFF"})], wrap=False)

    # 1 封面
    s = prs.slides.add_slide(lay_content)
    picture(s.shapes, dark_bg)
    brand(s.shapes, 0.8, 0.6)
    tb(s.shapes, 0.8, 2.5, 8, 1.4, [("标题", {"size": 48, "bold": True, "color": "FFFFFF"})])
    tb(s.shapes, 0.8, 3.9, 8, 0.5, [("SUBTITLE / 副标题", {"size": 18, "color": STEEL})])
    rect(s.shapes, 0.8, 4.65, 1.6, 0.08, fill=ORANGE)
    tb(s.shapes, 0.8, 6.4, 6, 0.4, [("2026 年度经营汇报", {"size": 13, "color": STEEL})])
    # 2 目录
    s = prs.slides.add_slide(lay_content)
    rect(s.shapes, 0, 0, W, H, fill=LIGHT)
    rect(s.shapes, 0, 0, 4.0, H, fill=GRAPH)
    tb(s.shapes, 0.7, 2.7, 3, 0.6, [("CONTENTS", {"size": 30, "bold": True, "color": "FFFFFF"})], wrap=False)
    tb(s.shapes, 0.7, 3.35, 3, 0.5, [("目录", {"size": 18, "color": ORANGE})])
    for i in range(6):
        y = 0.95 + i * 0.98
        rect(s.shapes, 4.8, y, 0.08, 0.6, fill=ORANGE)
        tb(s.shapes, 5.1, y + 0.02, 0.9, 0.55, [(f"{i + 1:02d}", {"size": 22, "bold": True, "color": GRAPH})],
           wrap=False)
        tb(s.shapes, 6.1, y + 0.07, 6.4, 0.5, [("目录标题", {"size": 19, "color": GRAPH})])
    # 3 章节
    s = prs.slides.add_slide(lay_content)
    picture(s.shapes, dark_bg)
    tb(s.shapes, 0.8, 1.7, 4, 1.8, [("01", {"size": 110, "bold": True, "color": ORANGE})], wrap=False)
    tb(s.shapes, 0.8, 3.6, 9, 0.9, [("章节标题", {"size": 38, "bold": True, "color": "FFFFFF"})])
    tb(s.shapes, 0.8, 4.5, 9, 0.5, [("SECTION SUBTITLE", {"size": 15, "color": STEEL})])
    # 4 内容页：标题白字压在深色页眉带上
    s = prs.slides.add_slide(lay)
    tb(s.shapes, 0.6, 0.3, 0.9, 0.6, [("01", {"size": 24, "bold": True, "color": ORANGE})], wrap=False)
    tb(s.shapes, 1.45, 0.32, 9.5, 0.6, [("页面标题", {"size": 24, "bold": True, "color": "FFFFFF"})])
    tb(s.shapes, 11.0, 0.42, 1.8, 0.35, [("华铸智造", {"size": 11, "bold": True, "color": STEEL})], align="r",
       wrap=False)
    for i in range(4):
        rect(s.shapes, 0.6 + i * 3.05, 1.8, 2.85, 4.6, fill="FFFFFF")
        tb(s.shapes, 0.85 + i * 3.05, 2.05, 2.4, 0.5, [("XXXXXX", {"size": 16, "bold": True, "color": GRAPH})])
    # 5 内容页（深色版）
    s = prs.slides.add_slide(lay_content)
    picture(s.shapes, dark_bg)
    tb(s.shapes, 0.6, 0.3, 0.9, 0.6, [("01", {"size": 24, "bold": True, "color": ORANGE})], wrap=False)
    tb(s.shapes, 1.45, 0.32, 9.5, 0.6, [("页面标题", {"size": 24, "bold": True, "color": "FFFFFF"})])
    rect(s.shapes, 0, 1.15, W, 0.04, fill=ORANGE)
    # 6 结尾
    s = prs.slides.add_slide(lay_content)
    picture(s.shapes, dark_bg)
    brand(s.shapes, 0.8, 0.6)
    tb(s.shapes, 0.8, 2.8, 8, 1.2, [("THANKS", {"size": 60, "bold": True, "color": "FFFFFF"})], wrap=False)
    tb(s.shapes, 0.8, 4.1, 8, 0.5, [("精益求精 · 智造未来", {"size": 18, "color": ORANGE})])
    prs.save(os.path.join(OUT, "manufacturing-huazhu.pptx"))


# ======================================================================
# 5. 文旅：云栖文旅 —— 宣纸 + 水墨远山 + 青绿 + 朱砂印章，衬线标题。内容页背景图右下角有山（考验安全区避让）。
# ======================================================================
def tourism():
    PAPER, INK, CELADON, CINNABAR, GRAY = "F6F1E7", "2B2B2B", "2F7D6D", "C2412D", "8C8577"
    SERIF = "思源宋体"
    prs = new_prs()
    base = paper(PX, PAPER)
    m = mountains(PX, [(640, 90, "A9C4BB", 150, 6), (760, 120, "6E9C8F", 190, 3), (880, 110, "2F5D53", 230, 1)])
    cover = Image.alpha_composite(base.convert("RGBA"), m)
    d = ImageDraw.Draw(cover)
    d.ellipse([1500, 140, 1660, 300], fill=rgb("E9B8A0") + (255,))
    cover_bg = save(cover, "tour-cover.jpg")
    m2 = mountains((900, 520), [(300, 70, "B9CFC7", 140, 4), (380, 80, "7EA89B", 180, 2)], seed=8)
    content = paper(PX, PAPER).convert("RGBA")
    content.alpha_composite(m2, (1020, 560))
    content_bg = save(content, "tour-content.jpg")
    sec = Image.alpha_composite(grad("24584D", "2F7D6D").convert("RGBA"),
                                mountains(PX, [(760, 120, "3E8C7B", 160, 4), (880, 100, "1D4A41", 220, 1)], seed=5))
    sec_bg = save(sec, "tour-section.jpg")

    def seal(sh, x, y, s=0.62, txt="云栖"):
        rect(sh, x, y, s, s, fill=CINNABAR, radius=0.08)
        tb(sh, x, y + s * 0.18, s, s * 0.6, [(txt, {"size": 13, "bold": True, "color": "FFFFFF", "font": SERIF})],
           align="c")

    # 1 封面
    s = blank(prs)
    picture(s.shapes, cover_bg)
    seal(s.shapes, 0.8, 0.7)
    tb(s.shapes, 0.8, 1.9, 9, 1.4, [("主标题", {"size": 54, "bold": True, "color": INK, "font": SERIF})])
    tb(s.shapes, 0.8, 3.3, 9, 0.6, [("副标题", {"size": 20, "color": CELADON, "font": SERIF})])
    tb(s.shapes, 0.8, 4.0, 6, 0.4, [("云栖文旅集团　·　20XX", {"size": 13, "color": GRAY})])
    # 2 目录：横排，竖线分隔
    s = blank(prs)
    picture(s.shapes, content_bg)
    tb(s.shapes, 0.8, 0.7, 5, 1.0, [("目　录", {"size": 36, "bold": True, "color": INK, "font": SERIF})])
    seal(s.shapes, 3.2, 0.82, 0.5, "录")
    for i in range(5):
        x = 0.9 + i * 2.45
        line(s.shapes, x, 2.4, x, 4.9, "C9BFAE", 1)
        rect(s.shapes, x - 0.03, 2.4, 0.06, 0.7, fill=CELADON)
        tb(s.shapes, x + 0.25, 2.4, 1.6, 0.8, [(f"{i + 1:02d}", {"size": 30, "bold": True, "color": CELADON,
                                                                "font": SERIF})], wrap=False)
        tb(s.shapes, x + 0.25, 3.3, 2.0, 1.4, [("目录标题", {"size": 19, "bold": True, "color": INK, "font": SERIF})])
    # 3 章节
    s = blank(prs)
    picture(s.shapes, sec_bg)
    tb(s.shapes, 0.9, 1.5, 3, 1.6, [("01", {"size": 80, "bold": True, "color": "F3E3C3", "font": SERIF})],
       wrap=False)
    tb(s.shapes, 0.9, 3.1, 9, 1.0, [("章节标题", {"size": 40, "bold": True, "color": "FFFFFF", "font": SERIF})])
    tb(s.shapes, 0.9, 4.1, 9, 0.5, [("章节副标题", {"size": 17, "color": "D7E6DF"})])
    # 4 内容页：右下角远山
    s = blank(prs)
    picture(s.shapes, content_bg)
    seal(s.shapes, 0.8, 0.62, 0.42, "栖")
    tb(s.shapes, 1.4, 0.5, 10, 0.8, [("页面标题", {"size": 28, "bold": True, "color": INK, "font": SERIF})])
    line(s.shapes, 0.8, 1.42, 12.5, 1.42, "D8CFBF", 0.75)
    rect(s.shapes, 0.8, 1.38, 1.4, 0.08, fill=CELADON)
    tb(s.shapes, 0.8, 1.9, 6, 4, [("在此输入正文内容", {"size": 15, "color": GRAY})])
    tb(s.shapes, 10.6, 7.0, 2.2, 0.3, [("云栖文旅 · YUNQI", {"size": 9, "color": GRAY})], align="r", wrap=False)
    # 5 结尾
    s = blank(prs)
    picture(s.shapes, cover_bg)
    seal(s.shapes, 0.8, 0.7)
    tb(s.shapes, 0.8, 2.2, 9, 1.2, [("山水相逢　后会有期", {"size": 46, "bold": True, "color": INK, "font": SERIF})])
    tb(s.shapes, 0.8, 3.4, 9, 0.5, [("欢迎来云栖", {"size": 20, "color": CELADON, "font": SERIF})])
    prs.save(os.path.join(OUT, "tourism-yunqi.pptx"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn in (finance, medical, education, manufacturing, tourism):
        fn()
        print("ok", fn.__name__)
