"""绘图基础件：文字（自动缩字适配）、色块、卡片、图标、原生图表、表格。颜色字体一律取自模板令牌 Theme。"""
import os
import re
import tempfile

from lxml import etree
from PIL import Image
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Pt

from common import ICONS, contrast, emu, fit_size, luminance, mix, readable_on

ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}
ANCHOR = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}
WARN = []  # 构建过程中的提示（放不下、找不到图标等），build.py 汇总输出


class Theme:
    """一页的配色：模板令牌 + 这一页的底色（深色底自动反色）"""

    def __init__(self, tokens, bg="FFFFFF"):
        t = tokens
        self.bg = bg
        self.dark_bg = luminance(bg) < 0.22
        self.primary, self.secondary = t["primary"], t["secondary"]
        self.font, self.font_heading = t["font"], t.get("font_heading") or t["font"]
        self.radius = t.get("radius", 0.1)
        if self.dark_bg:
            self.heading = "FFFFFF"
            self.body = mix("FFFFFF", bg, 0.18)
            self.muted = mix("FFFFFF", bg, 0.42)
            self.surface = mix(bg, "FFFFFF", 0.08)
            self.line = mix(bg, "FFFFFF", 0.22)
            self.tint = mix(bg, t["primary"], 0.28)
        else:
            self.heading, self.body, self.muted = t["dark"], t["body"], t["muted"]
            white_bg = luminance(bg) > 0.92
            self.surface = mix("FFFFFF", t["primary"], 0.035) if white_bg else t.get("surface", "FFFFFF")
            self.line = mix(bg, t["dark"], 0.13)
            self.tint = mix(bg if not white_bg else "FFFFFF", t["primary"], 0.09)
        for _ in range(6):  # 注释、图表来源这类次要文字也要看得清
            if contrast(self.muted, bg) >= 3.2:
                break
            self.muted = mix(self.muted, "FFFFFF" if self.dark_bg else t["dark"], 0.25)
        self.shadow = not self.dark_bg and luminance(bg) <= 0.92
        # 深色页上主色和底色撞色（例如海军蓝主色 + 海军蓝底），这一页改用辅色当主色
        if contrast(self.primary, bg) < 1.8 and contrast(self.secondary, bg) > contrast(self.primary, bg):
            self.primary, self.secondary = self.secondary, self.primary
            if self.dark_bg:
                self.tint = mix(bg, self.primary, 0.22)
        # 主色当文字用时，保证在卡片底上看得清：先试主色、再试辅色，都不行就往深/浅混
        self.accent = next((c for c in (self.primary, self.secondary)
                            if contrast(c, self.surface) >= 3.0 and contrast(c, bg) >= 3.0),
                           mix(self.primary, "FFFFFF" if self.dark_bg else t["dark"], 0.45))
        self.on_primary = readable_on(self.primary, "FFFFFF", t["dark"])

    def series(self, n):
        base = [self.primary, self.secondary, mix(self.primary, self.bg, 0.5), mix(self.secondary, self.bg, 0.5),
                self.muted, mix(self.primary, self.heading, 0.5)]
        return [base[i % len(base)] for i in range(n)]


# ---------- 文字 ----------
def _style_run(run, size, color, bold, font):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = RGBColor.from_string(color)
    f.name = font
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", font)


def plain(paras):
    if isinstance(paras, str):
        return paras
    out = []
    for p in paras:
        out.append(p if isinstance(p, str) else "".join(t for t, _ in p))
    return "\n".join(out)


def fill_tf(tf, paras, size, color, bold, align, font, line=None, after=0, scale=1.0):
    tf.clear()
    if isinstance(paras, str):
        paras = paras.split("\n")
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ALIGN[align]
        if line:
            p.line_spacing = line
        if after and i < len(paras) - 1:
            p.space_after = Pt(after)
        runs = [(para, {})] if isinstance(para, str) else para
        for txt, o in runs:
            r = p.add_run()
            r.text = txt
            _style_run(r, round(o.get("size", size) * scale, 1), o.get("color", color), o.get("bold", bold),
                       o.get("font", font))


def text(slide, T, x, y, w, h, paras, size=14, color=None, bold=False, align="l", anchor="t", line=1.15,
         after=0, heading=False, fit=True, min_size=None, wrap=True):
    """放一个文本框。fit=True 时放不下会整体缩小字号（不低于 min_size），返回实际倍率"""
    if w < 0.05 or h < 0.05:
        WARN.append(f"空间不够（{w:.2f}×{h:.2f} 英寸），内容太多：{plain(paras)[:20]}…")
        w, h = max(w, 0.05), max(h, 0.05)
    tb = slide.shapes.add_textbox(emu(x), emu(y), emu(w), emu(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.auto_size = None
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = ANCHOR[anchor]
    scale = 1.0
    if fit and wrap:
        min_size = min_size or max(10, round(size * 0.7))
        spacing = (line or 1.0) * 1.2 + (after / max(size, 1) if after else 0)
        s = fit_size(plain(paras), w, h, size, min_size, spacing)
        if s is None:
            s = min_size
            WARN.append(f"文字放不下（已缩到 {min_size}pt）：{plain(paras)[:24]}…")
        scale = s / size
        if scale < 0.8 and s >= min_size and fit_size(plain(paras), w, h, size, min_size, spacing) is not None:
            WARN.append(f"字号从 {size} 缩到 {s}pt，内容偏多：{plain(paras)[:20]}…")
    fill_tf(tf, paras, size, color or T.body, bold, align, T.font_heading if heading else T.font, line, after, scale)
    return tb


# ---------- 形状 ----------
def _shadow(shape, color):
    spPr = shape._element.spPr
    eff = etree.SubElement(spPr, qn("a:effectLst"))
    sh = etree.SubElement(eff, qn("a:outerShdw"), blurRad=str(16 * 12700), dist=str(3 * 12700), dir="5400000",
                          algn="t", rotWithShape="0")
    clr = etree.SubElement(sh, qn("a:srgbClr"), val=color)
    etree.SubElement(clr, qn("a:alpha"), val="16000")


def box(slide, T, x, y, w, h, fill=None, line=None, line_w=1.0, radius=None, shadow=False, grad=None, angle=0,
        kind=None, alpha=None):
    radius = T.radius if radius is None else radius
    w, h = max(w, 0.02), max(h, 0.02)
    if kind is None:
        kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(kind, emu(x), emu(y), emu(w), emu(h))
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE and radius:
        s.adjustments[0] = min(0.5, radius / max(0.01, min(w, h)))
    if grad:
        s.fill.gradient()
        s.fill.gradient_angle = angle
        st = s.fill.gradient_stops
        st[0].position, st[1].position = 0.0, 1.0
        st[0].color.rgb = RGBColor.from_string(grad[0])
        st[1].color.rgb = RGBColor.from_string(grad[1])
    elif fill:
        s.fill.solid()
        s.fill.fore_color.rgb = RGBColor.from_string(fill)
        if alpha is not None:
            clr = s.fill._xPr.find(".//" + qn("a:srgbClr"))
            etree.SubElement(clr, qn("a:alpha"), val=str(int(alpha * 100000)))
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = RGBColor.from_string(line)
        s.line.width = Pt(line_w)
    else:
        s.line.fill.background()
    if shadow:
        _shadow(s, mix(T.primary, "000000", 0.5))
    s.text_frame.text = ""
    return s


def circle(slide, T, x, y, d, fill, line=None):
    return box(slide, T, x, y, d, d, fill=fill, line=line, kind=MSO_SHAPE.OVAL, radius=0)


def hline(slide, T, x, y, w, color, weight=1.0):
    ln = slide.shapes.add_connector(1, emu(x), emu(y), emu(x + w), emu(y))
    ln.line.color.rgb = RGBColor.from_string(color)
    ln.line.width = Pt(weight)
    return ln


def vline(slide, T, x, y, h, color, weight=1.0):
    ln = slide.shapes.add_connector(1, emu(x), emu(y), emu(x), emu(y + h))
    ln.line.color.rgb = RGBColor.from_string(color)
    ln.line.width = Pt(weight)
    return ln


def label_in(shape, T, paras, size, color, bold=True, align="c", anchor="m", margin=0.06):
    tf = shape.text_frame
    tf.word_wrap = True
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", emu(margin))
    tf.vertical_anchor = ANCHOR[anchor]
    fill_tf(tf, paras, size, color, bold, align, T.font)
    return shape


_ICON_CACHE = tempfile.mkdtemp(prefix="xiaoma-ppt-icons-")  # 每次运行独立目录，不和别的用户共享


def icon_path(name, color):
    src = os.path.join(ICONS, f"{name}.png")
    if not re.fullmatch(r"[\w-]+", name or "") or not os.path.exists(src):
        WARN.append(f"没有图标 {name}（可用图标见 engine/icons/）")
        return None
    os.makedirs(_ICON_CACHE, exist_ok=True)
    dst = os.path.join(_ICON_CACHE, f"{name}-{color}.png")
    if not os.path.exists(dst):
        a = Image.open(src).convert("RGBA").split()[3]
        im = Image.new("RGBA", a.size, tuple(int(color[i:i + 2], 16) for i in (0, 2, 4)) + (0,))
        im.putalpha(a)
        im.save(dst)
    return dst


def icon(slide, T, name, x, y, d, style="solid"):
    """圆底图标。solid：主色底+反白图标；soft：浅主色底+主色图标；bare：只有图标"""
    if style == "solid":
        circle(slide, T, x, y, d, T.primary)
        p = icon_path(name, T.on_primary)
    elif style == "soft":
        circle(slide, T, x, y, d, T.tint)
        p = icon_path(name, T.accent)
    else:
        p = icon_path(name, T.accent)
        if p:
            slide.shapes.add_picture(p, emu(x), emu(y), emu(d), emu(d))
        return
    if p:
        k = d * 0.52
        slide.shapes.add_picture(p, emu(x + (d - k) / 2), emu(y + (d - k) / 2), emu(k), emu(k))


def picture_cover(slide, path, x, y, w, h):
    """等比铺满 w×h，多出来的部分裁掉"""
    with Image.open(path) as im:
        iw, ih = im.size
    pic = slide.shapes.add_picture(path, emu(x), emu(y), emu(w), emu(h))
    r_box, r_img = w / h, iw / ih
    if r_img > r_box:
        c = (1 - r_box / r_img) / 2
        pic.crop_left = pic.crop_right = c
    else:
        c = (1 - r_img / r_box) / 2
        pic.crop_top = pic.crop_bottom = c
    return pic


# ---------- 图表 ----------
KINDS = {"column": XL_CHART_TYPE.COLUMN_CLUSTERED, "bar": XL_CHART_TYPE.BAR_CLUSTERED,
         "stacked": XL_CHART_TYPE.COLUMN_STACKED, "line": XL_CHART_TYPE.LINE_MARKERS,
         "pie": XL_CHART_TYPE.PIE, "doughnut": XL_CHART_TYPE.DOUGHNUT, "area": XL_CHART_TYPE.AREA}


def _chart_font(ch, T, size):
    ch.font.name = T.font
    ch.font.size = Pt(size)
    ch.font.color.rgb = RGBColor.from_string(T.body)
    txPr = ch._chartSpace.find(qn("c:txPr"))
    if txPr is not None:
        for r in txPr.iter(qn("a:defRPr")):
            ea = r.find(qn("a:ea"))
            if ea is None:
                ea = etree.SubElement(r, qn("a:ea"))
            ea.set("typeface", T.font)


def chart(slide, T, x, y, w, h, kind, categories, series, fmt="General", highlight=None, size=12):
    cd = CategoryChartData()
    cd.categories = categories
    for s in series:
        cd.add_series(s.get("name", ""), s["values"])
    gf = slide.shapes.add_chart(KINDS[kind], emu(x), emu(y), emu(w), emu(h), cd)
    ch = gf.chart
    _chart_font(ch, T, size)
    ch.has_title = False
    plot = ch.plots[0]
    colors = T.series(len(series))
    pie = kind in ("pie", "doughnut")
    if pie:
        pc = T.series(len(categories))
        for i, pt in enumerate(plot.series[0].points):
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = RGBColor.from_string(pc[i])
            pt.format.line.color.rgb = RGBColor.from_string(T.bg)
        ch.has_legend = True
        ch.legend.position = XL_LEGEND_POSITION.RIGHT
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(size + 2)
        ch.legend.font.color.rgb = RGBColor.from_string(T.body)
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.number_format, dl.number_format_is_linked = fmt if fmt != "General" else "0%", False
        dl.show_percentage = fmt == "General"
        dl.show_value = fmt != "General"
        dl.font.size = Pt(size + 1)
        dl.font.bold = True
        dl.font.color.rgb = RGBColor.from_string(readable_on(T.primary))
        return ch
    ch.has_legend = len(series) > 1
    if ch.has_legend:
        ch.legend.position = XL_LEGEND_POSITION.TOP
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(size)
        ch.legend.font.color.rgb = RGBColor.from_string(T.body)
    if kind in ("column", "bar", "stacked"):
        plot.gap_width = 60 if len(categories) <= 6 else 40
        if kind != "stacked":
            plot.overlap = -10 if len(series) > 1 else 0
    for si, s in enumerate(plot.series):
        c = colors[si]
        if kind in ("line",):
            s.format.line.color.rgb = RGBColor.from_string(c)
            s.format.line.width = Pt(2.75)
            s.smooth = False
            s.marker.format.fill.solid()
            s.marker.format.fill.fore_color.rgb = RGBColor.from_string(c)
            s.marker.format.line.color.rgb = RGBColor.from_string(T.bg)
        else:
            s.format.fill.solid()
            s.format.fill.fore_color.rgb = RGBColor.from_string(c)
            s.format.line.fill.background()
            if highlight is not None and len(series) == 1:
                for i, pt in enumerate(s.points):
                    pt.format.fill.solid()
                    pt.format.fill.fore_color.rgb = RGBColor.from_string(
                        c if i == highlight else mix(c, T.bg, 0.55))
    if len(series) <= 2 and len(categories) <= 12:
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.number_format, dl.number_format_is_linked = fmt, False
        dl.font.size = Pt(size + 1)
        dl.font.bold = True
        dl.font.color.rgb = RGBColor.from_string(T.heading)
        if kind != "stacked":
            dl.position = XL_LABEL_POSITION.OUTSIDE_END if kind != "line" else XL_LABEL_POSITION.ABOVE
    va = ch.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor.from_string(T.line)
    va.major_gridlines.format.line.width = Pt(0.75)
    va.format.line.fill.background()
    va.tick_labels.font.color.rgb = RGBColor.from_string(T.muted)
    va.tick_labels.font.size = Pt(size - 1)
    va.tick_labels.number_format, va.tick_labels.number_format_is_linked = fmt, False
    if plot.has_data_labels:
        va.visible = False
        va.has_major_gridlines = False
    if kind == "line":  # 折线图纵轴围绕数据取范围，线条落在图中间而不是贴顶
        vals = [v for s in series for v in s["values"] if v is not None]
        lo, hi = min(vals), max(vals)
        span = (hi - lo) or abs(hi) or 1
        va.minimum_scale = lo - span * 1.2 if lo - span * 1.2 > 0 or lo < 0 else 0
        va.maximum_scale = hi + span * 0.35
    ca = ch.category_axis
    ca.format.line.color.rgb = RGBColor.from_string(T.line)
    ca.tick_labels.font.color.rgb = RGBColor.from_string(T.body)
    ca.tick_labels.font.size = Pt(size)
    ca.has_major_gridlines = False
    return ch


def table(slide, T, x, y, w, h, header, rows, highlight_col=None, size=13, col_widths=None):
    nr, nc = len(rows) + 1, len(header)
    gf = slide.shapes.add_table(nr, nc, emu(x), emu(y), emu(w), emu(h))
    tbl = gf.table
    tblPr = gf._element.graphic.graphicData.tbl.tblPr
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is not None:
        sid.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"  # 无样式、无网格，全部自己上色
    widths = col_widths or [1] * nc
    tot = sum(widths)
    for i, cw in enumerate(widths):
        tbl.columns[i].width = emu(w * cw / tot)
    for r in range(nr):
        tbl.rows[r].height = emu(h / nr)
        for c in range(nc):
            cell = tbl.cell(r, c)
            val = header[c] if r == 0 else rows[r - 1][c]
            hl = highlight_col is not None and c == highlight_col
            if r == 0:
                fill, color, bold = (T.primary if not hl else mix(T.primary, T.heading, 0.25)), T.on_primary, True
            else:
                fill = T.tint if hl else (T.surface if r % 2 else mix(T.surface, T.line, 0.35))
                color, bold = (T.accent if hl else T.body), (c == 0 or hl)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor.from_string(fill)
            cell.margin_left = cell.margin_right = emu(0.12)
            cell.margin_top = cell.margin_bottom = emu(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            fill_tf(cell.text_frame, str(val), size, color, bold, "l" if c == 0 else "c", T.font)
    return tbl
