"""复杂模板 3：咨询研究报告（虚构品牌「衡策咨询」）。
考验点：
- 第一页是隐藏的「模板使用说明」，不是封面
- 议程是「一个文本框里的多个段落」；章节页是「高亮当前议题的议程页」（同一结构出现两次）
- 内容页：两行行动标题（占位符，空）、右上角进度标签（当前章节加粗加下划线）、单位行、资料来源行、页脚和页码占位符
- 大量示例信息图页：执行摘要、2×2 矩阵、瀑布图（原生图表，隐藏底座系列）、哈维球表、甘特图、组织架构、箭头流程
- 带右侧要点栏的版式（栏在版式上）；封底是免责声明长段落，不含「谢谢」
"""
import os

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE, PP_PLACEHOLDER
from pptx.util import Inches, Pt

import tpl_kit as K
from make_templates import OUT, drop_slide, rgb, save

W, H = 13.333, 7.5
NAVY, TEAL, AMBER, GRAY = "0B2545", "1F8A70", "E09F3E", "8D99AE"
COLORS = {"dk1": "1F2937", "lt1": "FFFFFF", "dk2": NAVY, "lt2": "F2F4F7", "accent1": "13315C", "accent2": TEAL,
          "accent3": AMBER, "accent4": GRAY, "accent5": "5DA9E9", "accent6": "C0392B", "hlink": "13315C",
          "folHlink": GRAY}
TRACK = ["市场概览", "竞争格局", "能力评估", "实施建议"]


def skyline():
    w, h = 1300, 1080
    im = Image.new("RGB", (w, h), (247, 248, 250))
    d = ImageDraw.Draw(im)
    base = 820
    xs = [(60, 140, 420), (220, 90, 560), (330, 150, 360), (500, 110, 640), (630, 160, 300), (810, 90, 500),
          (920, 140, 410), (1080, 120, 580), (1200, 90, 330)]
    for x, bw, bh in xs:
        d.rectangle([x, base - bh, x + bw, base], outline=rgb(NAVY), width=3)
        for yy in range(base - bh + 30, base - 20, 40):
            for xx in range(x + 18, x + bw - 18, 28):
                d.rectangle([xx, yy, xx + 10, yy + 16], outline=rgb(GRAY), width=1)
    d.line([(0, base), (w, base)], fill=rgb(NAVY), width=4)
    for k in range(6):
        d.line([(0, base + 40 + k * 32), (w, base + 40 + k * 32)], fill=(220, 224, 230), width=2)
    return save(im, "consulting-skyline.jpg")


def logo_png(white=True):
    w, h = 620, 150
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (255, 255, 255, 255) if white else rgb(NAVY) + (255,)
    d.rectangle([10, 25, 110, 125], outline=c, width=9)
    d.line([(10, 75), (110, 75)], fill=c, width=9)
    d.line([(60, 25), (60, 125)], fill=rgb(TEAL) + (255,), width=9)
    d.text((140, 18), "衡策咨询", font=K.cjk_font(70, bold=True), fill=c)
    d.text((143, 100), "HENGCE CONSULTING", font=K.cjk_font(30), fill=c)
    path = os.path.join(os.path.dirname(save(Image.new("RGB", (2, 2)), "_tmp.jpg")),
                        f"consulting-logo{'-w' if white else ''}.png")
    im.save(path)
    return path


# ---------- 母版和版式 ----------
def setup(prs, art):
    m = prs.slide_master
    K.master_text_styles(prs, (22, "tx2", False), [(14, "tx1"), (12, "tx1"), (11, "accent4")])
    K.style_ph(K.ph_of(m, PP_PLACEHOLDER.TITLE), 0.55, 0.45, 9.6, 0.95, anchor="b", align="l")
    K.style_ph(K.ph_of(m, PP_PLACEHOLDER.BODY), 0.55, 1.75, 12.2, 4.9)
    K.style_ph(K.ph_of(m, PP_PLACEHOLDER.FOOTER), 0.55, 7.08, 5.0, 0.25, prompt="衡策咨询　|　严格保密，仅供客户内部使用",
               size=8, color="accent4", align="l")
    K.style_ph(K.ph_of(m, PP_PLACEHOLDER.SLIDE_NUMBER), 12.2, 7.08, 0.6, 0.25, size=8, color="accent4", align="r")
    K.drop_ph(m, PP_PLACEHOLDER.DATE)
    tmp = prs.slides.add_slide(prs.slide_layouts[6])
    K.move_to(m, tmp, [K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 0.55, 1.5, 12.23, 0.012, theme="tx2"),
                       K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 0.55, 7.0, 12.23, 0.008, color="C8CED8"),
                       K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 0, 0, 0.14, 0.62, theme="accent2")])
    drop_slide(prs, tmp)
    L = K.keep_layouts(prs, {0: "封面", 1: "标题和内容", 5: "仅标题", 6: "空白", 7: "议程", 3: "带要点栏"})
    # 封面：左侧深色面板在版式上
    lay = L["封面"]
    lay._element.set("showMasterSp", "0")
    tmp = prs.slides.add_slide(L["空白"])
    K.move_to(lay, tmp, [K.picture(tmp.shapes, art["skyline"], 5.6, 0, 7.733, H),
                         K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 0, 0, 5.6, H, theme="tx2"),
                         K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 0.7, 3.95, 0.8, 0.05, theme="accent2"),
                         K.picture(tmp.shapes, art["logo"], 0.7, 0.7, 2.0)])
    drop_slide(prs, tmp)
    K.style_ph(K.ph_of(lay, PP_PLACEHOLDER.CENTER_TITLE), 0.7, 1.9, 4.5, 1.9, prompt="单击此处添加报告标题",
               size=30, color="bg1", font="+mj", align="l", anchor="b")
    K.style_ph(K.ph_of(lay, PP_PLACEHOLDER.SUBTITLE), 0.7, 4.2, 4.5, 0.9, prompt="单击此处添加副标题",
               size=14, color="C9D4E3", align="l", bullets=False)
    K.drop_ph(lay, PP_PLACEHOLDER.DATE, PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER)
    # 议程
    lay = L["议程"]
    K.drop_ph(lay, PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.OBJECT, PP_PLACEHOLDER.DATE)
    K.style_ph(K.ph_of(lay, None, idx=0), 0.55, 0.45, 9.6, 0.95, prompt="议程", anchor="b", align="l")
    # 带要点栏：右侧灰栏在版式上
    lay = L["带要点栏"]
    tmp = prs.slides.add_slide(L["空白"])
    K.move_to(lay, tmp, [K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 9.35, 1.75, 3.43, 4.95, theme="bg2"),
                         K.shape(tmp.shapes, MSO_SHAPE.RECTANGLE, 9.35, 1.75, 3.43, 0.06, theme="accent2"),
                         K.text(tmp.shapes, 9.6, 1.95, 3.0, 0.4, "要点", size=14, bold=True, theme="tx2")])
    drop_slide(prs, tmp)
    phs = [p for p in lay.placeholders if p.placeholder_format.idx in (1, 2)]
    K.style_ph(phs[0], 0.55, 1.75, 8.5, 4.9, prompt="单击此处编辑正文")
    phs[1]._element.getparent().remove(phs[1]._element)
    for name in ("标题和内容", "仅标题", "带要点栏"):
        K.style_ph(K.ph_of(L[name], None, idx=0), 0.55, 0.45, 9.6, 0.95,
                   prompt="行动标题：用一句完整的话写出本页结论，不超过两行", anchor="b", align="l")
    return L


# ---------- 页面部件 ----------
def tracker(s, cur):
    for i, t in enumerate(TRACK):
        x = 10.35 + i * 0.62
        K.text(s.shapes, x, 0.22, 0.62, 0.25, t, size=7, bold=i == cur, theme="tx2" if i == cur else "accent4",
               align="c", insets=(0, 0, 0, 0), name=f"进度 {t}")
        if i == cur:
            K.shape(s.shapes, MSO_SHAPE.RECTANGLE, x + 0.06, 0.48, 0.5, 0.03, theme="accent2")


def source(s, txt="资料来源：XXX；衡策咨询分析"):
    K.text(s.shapes, 0.55, 6.72, 9, 0.25, txt, size=8, theme="accent4")


def unit(s, txt="单位：XX"):
    K.text(s.shapes, 0.55, 1.58, 4, 0.25, txt, size=9, theme="accent4")


def content(prs, L, cur, title=None, layout="仅标题"):
    s = prs.slides.add_slide(L[layout])
    if title:
        s.shapes.title.text = title
    tracker(s, cur)
    return s


def agenda(s, cur=None):
    tb = s.shapes.add_textbox(Inches(1.6), Inches(1.95), Inches(8.5), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    for i in range(5):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(18)
        r = p.add_run()
        r.text = f"{i + 1}　　议题{'一二三四五'[i]}：在此输入议题名称"
        on = cur is None or i == cur
        K.style_run(r, size=20, bold=(i == cur), theme="tx2" if on else "accent4", font="+mn")
    tb.name = "议程列表"
    if cur is not None:
        K.shape(s.shapes, MSO_SHAPE.RECTANGLE, 1.3, 1.98 + cur * 0.78, 0.08, 0.42, theme="accent2")


def make():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    K.set_theme(prs, "衡策咨询", COLORS, ("Georgia", "华文中宋"), ("Arial", "微软雅黑"))
    art = {"skyline": skyline(), "logo": logo_png()}
    L = setup(prs, art)

    # 0 隐藏的使用说明页
    s = prs.slides.add_slide(L["仅标题"])
    s.shapes.title.text = "模板使用说明（本页隐藏，不会放映）"
    K.text(s.shapes, 0.55, 1.8, 12, 4.5, "\n".join([
        "1. 标题用「行动标题」：一句完整的话写出本页结论，不超过两行。",
        "2. 右上角进度标签标出当前所在章节，其余章节为灰色。",
        "3. 每页左下角注明资料来源；单位写在标题下方。",
        "4. 图表颜色只用主题色：深蓝为主，青绿表示重点，琥珀色表示风险。",
        "5. 正文字号不小于 11pt；一页只讲一个结论。",
        "6. 交付前删除本页，并把封面的「讨论稿」改为「终稿」。"]), size=14, theme="tx1", spacing=1.5)
    K.hide(s)

    # 1 封面
    s = prs.slides.add_slide(L["封面"])
    s.shapes.title.text = "项目名称：报告主标题"
    K.ph_of(s, PP_PLACEHOLDER.SUBTITLE).text = "为XX客户准备的讨论文件"
    K.text(s.shapes, 0.7, 6.3, 4.5, 0.35, "202X年X月　|　北京", size=11, color="C9D4E3")
    K.text(s.shapes, 0.7, 6.65, 4.5, 0.3, "讨论稿 · 严格保密", size=9, color="8DA2BF")

    # 2 议程：一个文本框、5 个段落
    s = prs.slides.add_slide(L["议程"])
    s.shapes.title.text = "议程"
    agenda(s)

    # 3 章节分隔：高亮第 2 个议题的议程页
    s = prs.slides.add_slide(L["议程"])
    s.shapes.title.text = "议程"
    agenda(s, cur=1)

    # 4 执行摘要
    s = content(prs, L, 0, "执行摘要")
    for i in range(4):
        y = 1.85 + i * 1.18
        b = K.shape(s.shapes, MSO_SHAPE.RECTANGLE, 0.55, y, 0.5, 0.5, theme="tx2")
        n = K.text(s.shapes, 0.55, y, 0.5, 0.5, str(i + 1), size=16, bold=True, theme="bg1", align="c", anchor="m")
        lead = K.text(s.shapes, 1.25, y - 0.04, 11.3, 0.4, f"核心结论{'一二三四'[i]}：在此输入一句话结论", size=15,
                      bold=True, theme="tx2")
        sub = K.text(s.shapes, 1.25, y + 0.38, 11.3, 0.55, "支撑论据：在此输入数据或事实，说明为什么得出这个结论",
                     size=11, theme="tx1")
        K.group(s.shapes, [b, n, lead, sub])
    source(s)

    # 5 标准内容页（标题占位符留空）
    s = content(prs, L, 1, layout="标题和内容")
    unit(s)
    source(s)

    # 6 2×2 矩阵
    s = content(prs, L, 1, "2×2 矩阵示例")
    K.shape(s.shapes, MSO_SHAPE.RECTANGLE, 2.0, 1.95, 8.6, 0.015, theme="accent4").top = Inches(4.2)
    K.shape(s.shapes, MSO_SHAPE.RECTANGLE, 6.3, 1.9, 0.015, 4.6, theme="accent4")
    for (x, y, t) in ((2.2, 2.0, "象限一"), (6.5, 2.0, "象限二"), (2.2, 4.35, "象限三"), (6.5, 4.35, "象限四")):
        K.text(s.shapes, x, y, 2.5, 0.35, t, size=12, bold=True, theme="tx2")
    for (x, y, r, c) in ((7.8, 2.6, 0.8, "accent2"), (3.6, 3.0, 0.55, "accent1"), (8.6, 5.0, 0.45, "accent3"),
                         (4.4, 5.3, 0.6, "accent4")):
        K.shape(s.shapes, MSO_SHAPE.OVAL, x, y, r, r, theme=c)
    K.text(s.shapes, 10.7, 4.05, 1.8, 0.3, "维度一 →", size=10, theme="accent4")
    K.text(s.shapes, 5.5, 1.62, 1.8, 0.3, "↑ 维度二", size=10, theme="accent4")
    source(s)

    # 7 瀑布图（原生图表：底座系列透明）
    s = content(prs, L, 1, "瀑布图示例")
    unit(s)
    g = K.chart(s.shapes, XL_CHART_TYPE.COLUMN_STACKED, 0.55, 1.9, 12.2, 4.7,
                ["起点", "因素一", "因素二", "因素三", "因素四", "终点"],
                [("底座", (0, 100, 130, 110, 125, 0)), ("数值", (100, 30, -20, 15, 20, 145))],
                ["FFFFFF", "accent1"], legend=False, gap=60)
    base = g.chart.series[0]
    base.format.fill.background()
    g.chart.plots[0].data_labels.font.size = Pt(10)
    source(s)

    # 8 哈维球评分表
    s = content(prs, L, 2, "能力评估示例")
    K.table(s.shapes, 0.55, 1.9, 12.2, 3.9, [["评估维度", "公司 A", "公司 B", "公司 C", "公司 D"]] +
            [[f"维度{'一二三四五'[i]}", "", "", "", ""] for i in range(5)], header_theme="tx2", font_size=12)
    import random
    random.seed(4)
    for r in range(5):
        for c in range(4):
            x, y = 4.0 + c * 2.44 + 0.75, 2.62 + r * 0.645
            K.shape(s.shapes, MSO_SHAPE.OVAL, x, y, 0.32, 0.32, color="FFFFFF", line="13315C", line_w=1)
            k = random.choice((0.25, 0.5, 0.75, 1.0))
            if k < 1:
                K.shape(s.shapes, MSO_SHAPE.PIE, x, y, 0.32, 0.32, theme="accent1", adj=[-90, -90 + 360 * k])
            else:
                K.shape(s.shapes, MSO_SHAPE.OVAL, x, y, 0.32, 0.32, theme="accent1")
    source(s)

    # 9 甘特图
    s = content(prs, L, 3, "实施路线图示例")
    for q in range(8):
        K.text(s.shapes, 3.2 + q * 1.19, 1.85, 1.19, 0.3, f"Q{q % 4 + 1}", size=10, bold=True, theme="tx2", align="c")
    for r in range(6):
        y = 2.3 + r * 0.68
        K.text(s.shapes, 0.55, y, 2.6, 0.45, f"工作模块{'一二三四五六'[r]}", size=12, theme="tx1", anchor="m")
        K.shape(s.shapes, MSO_SHAPE.RECTANGLE, 0.55, y + 0.56, 12.2, 0.008, color="E3E7ED")
        K.shape(s.shapes, MSO_SHAPE.RECTANGLE, 3.25 + r * 0.9, y + 0.08, 2.4 + (r % 3) * 0.8, 0.32,
                theme="accent1" if r % 2 == 0 else "accent2")
    K.shape(s.shapes, MSO_SHAPE.DIAMOND, 10.3, 6.35, 0.25, 0.25, theme="accent3")
    K.text(s.shapes, 10.6, 6.3, 2, 0.3, "里程碑", size=10, theme="accent4")

    # 10 组织架构
    s = content(prs, L, 3, "组织架构示例")
    top = K.shape(s.shapes, MSO_SHAPE.RECTANGLE, 5.4, 1.95, 2.5, 0.7, theme="tx2")
    K.text(s.shapes, 5.4, 1.95, 2.5, 0.7, "项目指导委员会", size=12, bold=True, theme="bg1", align="c", anchor="m")
    for i in range(4):
        x = 0.9 + i * 3.1
        b = K.shape(s.shapes, MSO_SHAPE.RECTANGLE, x, 3.6, 2.4, 0.65, theme="bg2", line="13315C")
        K.text(s.shapes, x, 3.6, 2.4, 0.65, f"工作组{'一二三四'[i]}", size=12, bold=True, theme="tx2", align="c",
               anchor="m")
        c = s.shapes.add_connector(MSO_CONNECTOR.ELBOW, Inches(6.65), Inches(2.65), Inches(x + 1.2), Inches(3.6))
        c.line.color.rgb = K.RGBColor.from_string("8D99AE")
        c.begin_connect(top, 2)
        c.end_connect(b, 0)
        for k in range(2):
            K.text(s.shapes, x + 0.1, 4.45 + k * 0.42, 2.2, 0.35, "职责描述", size=10, theme="tx1", align="c")

    # 11 箭头流程（组合）
    s = content(prs, L, 3, "推进步骤示例")
    for i in range(5):
        x = 0.55 + i * 2.45
        ch = K.shape(s.shapes, MSO_SHAPE.CHEVRON if i else MSO_SHAPE.PENTAGON, x, 2.0, 2.55, 0.8,
                     theme="tx2" if i % 2 == 0 else "accent1")
        t = K.text(s.shapes, x + 0.3, 2.0, 2.0, 0.8, f"阶段{'一二三四五'[i]}", size=13, bold=True, theme="bg1",
                   align="c", anchor="m")
        d = K.text(s.shapes, x + 0.1, 3.05, 2.2, 2.4, "• 关键动作\n• 关键动作\n• 交付成果", size=11, theme="tx1",
                   spacing=1.4)
        K.group(s.shapes, [ch, t, d])
    source(s)

    # 12 带右侧要点栏
    s = content(prs, L, 2, layout="带要点栏")
    K.ph_of(s, None, idx=1).text_frame.text = "在此输入正文或插入图表"
    K.text(s.shapes, 9.6, 2.45, 3.0, 3.8, "• 在此输入要点一\n• 在此输入要点二\n• 在此输入要点三", size=12, theme="tx1",
           spacing=1.5)

    # 13 封底：免责声明
    s = prs.slides.add_slide(L["空白"])
    s._element.set("showMasterSp", "0")
    K.layout_bg(s, theme="dk2")
    K.picture(s.shapes, art["logo"], 0.8, 0.8, 2.6)
    K.text(s.shapes, 0.8, 3.0, 11, 0.4, "北京　|　上海　|　深圳　|　香港　|　新加坡", size=13, color="C9D4E3")
    K.text(s.shapes, 0.8, 5.3, 11.7, 1.4,
           "本报告仅供委托方内部参考使用，未经衡策咨询书面许可，不得向任何第三方披露、引用或转载。报告中的分析与结论基于"
           "委托方提供的资料及公开信息，衡策咨询不对其完整性与准确性作出保证，亦不承担因使用本报告而产生的任何责任。",
           size=9, color="8DA2BF", spacing=1.4)

    for i, sl in enumerate(prs.slides):
        if sl.slide_layout.name in ("标题和内容", "仅标题", "带要点栏", "议程"):
            K.footer_phs(sl, prs.slide_master, i + 1)
    path = os.path.join(OUT, "consulting-hengce.pptx")
    prs.save(path)
    return path


if __name__ == "__main__":
    print(make())
