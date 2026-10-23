"""内容版式（recipe）。每个函数在内容安全区 area=(x,y,w,h) 里画一种版式，所有颜色字体来自 Theme。
排版规矩：一页一个重点；字号层级 标题 > 数字 > 小标题 > 正文 > 注释；主色只用在要被看见的地方；
内容少时按空间放大（最多 1.4 倍）并整体居中，不让版面上半截挤着、下半截空着。
"""
from common import count_lines, mix, text_em, text_height
from draw import WARN, box, chart as _chart, circle, hline, icon, label_in, picture_cover, table as _table, text, vline

GAP = 0.3
MAX_ZOOM = 1.4


def norm(item):
    if isinstance(item, str):
        return {"title": "", "text": item}
    return dict(item)


def zoom(avail, need):
    """内容自然高度 need 放进 avail 时的放大倍数"""
    if need <= 0:
        return 1.0
    return max(1.0, min(MAX_ZOOM, avail / need * 0.82))


def grid(n, max_cols=4):
    if n <= max_cols:
        return 1, n
    if n <= 6:
        return 2, 3
    return 2, (n + 1) // 2


def panel(slide, T, x, y, w, h, strong=False):
    """卡片底：浅底页用白卡+阴影，白底页用浅色卡+细边，深底页用亮一点的面"""
    return box(slide, T, x, y, w, h, fill=T.surface, shadow=T.shadow and not strong,
               line=(T.primary if strong else (None if T.shadow or T.dark_bg else T.line)),
               line_w=1.5 if strong else 0.75)


# ---------- 列表 ----------
def bullets(slide, T, a, d):
    items = [norm(i) for i in d["items"]]
    x, y, w, h = a
    cols = 2 if len(items) > 5 else 1
    per = (len(items) + cols - 1) // cols
    cw = (w - GAP * 2 * (cols - 1)) / cols
    base_row = max(max(text_height(i.get("text", ""), cw - 0.7, 14) + (0.5 if i.get("title") else 0.1) for i in items),
                   0.6)
    f = zoom(h, (base_row + 0.25) * per)
    rh = min(h / per, base_row * f + 0.3)
    top = y + max(0, (h - rh * per) / 2)
    for i, it in enumerate(items):
        c, r = divmod(i, per)
        cx, cy = x + c * (cw + GAP * 2), top + r * rh
        if it.get("icon"):
            d_ic = 0.5 * f
            icon(slide, T, it["icon"], cx, cy + 0.02, d_ic, "soft")
            tx = cx + d_ic + 0.25
        else:
            box(slide, T, cx, cy + 0.13 * f, 0.12, 0.12, fill=T.primary, radius=0)
            tx = cx + 0.35
        tw = cw - (tx - cx)
        if it.get("title"):
            th = 0.42 * f
            text(slide, T, tx, cy, tw, th, it["title"], size=round(18 * f), color=T.heading, bold=True, min_size=13)
            if it.get("text"):
                text(slide, T, tx, cy + th + 0.04, tw, rh - th - 0.2, it["text"], size=round(14 * f), color=T.body,
                     line=1.25, min_size=10)
        else:
            text(slide, T, tx, cy, tw, rh - 0.15, it["text"], size=round(17 * f), color=T.heading, line=1.25,
                 min_size=11)
        if r < per - 1 and i < len(items) - 1:
            hline(slide, T, cx, cy + rh - 0.1, cw, T.line, 0.75)


def cards(slide, T, a, d):
    items = [norm(i) for i in d["items"]]
    x, y, w, h = a
    rows, cols = grid(len(items), d.get("max_cols", 4))
    cw = (w - GAP * (cols - 1)) / cols
    any_icon = any(i.get("icon") for i in items)
    any_value = any(i.get("value") for i in items)

    def need(f):
        pad = (0.3 if cw > 2.2 else 0.22) * f
        iw = cw - 2 * pad
        head = (0.62 * f + 0.2 if any_icon else 0) + (0.8 * f if any_value else 0) + \
               (0.5 * f if not any_icon and not any_value else 0)
        th = max((text_height(i["title"], iw, 18 * f) + 0.06) if i.get("title") else 0 for i in items)
        bh = max((text_height(i["text"], iw, 14 * f, 1.25 * 1.2)) if i.get("text") else 0 for i in items)
        return pad * 2 + head + th + 0.12 + bh + 0.1, pad, iw, th

    avail = (h - GAP * (rows - 1)) / rows
    f = zoom(avail, need(1.0)[0])
    while f > 1.0 and need(f)[0] > avail:
        f -= 0.05
    nh, pad, iw, title_h = need(f)
    ch = min(avail, max(nh, avail * 0.62))
    oy = y + (h - (ch * rows + GAP * (rows - 1))) / 2
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        off = (cols - len(items) % cols) * (cw + GAP) / 2 if r == rows - 1 and len(items) % cols and rows > 1 else 0
        cx, cy = x + off + c * (cw + GAP), oy + r * (ch + GAP)
        panel(slide, T, cx, cy, cw, ch)
        if not T.radius:
            box(slide, T, cx, cy, cw, 0.07, fill=T.primary, radius=0)
        ty = cy + pad
        if any_icon:
            if it.get("icon"):
                icon(slide, T, it["icon"], cx + pad, ty, 0.62 * f, "solid")
            ty += 0.62 * f + 0.2
        elif not any_value:
            text(slide, T, cx + pad, ty, 1.2, 0.5 * f, f"{i + 1:02d}", size=round(22 * f), color=T.accent, bold=True,
                 fit=False)
            ty += 0.5 * f
        if any_value:
            if it.get("value"):
                text(slide, T, cx + pad, ty - 0.05, iw, 0.8 * f,
                     [[(str(it["value"]), {"size": round(34 * f), "bold": True, "color": T.accent}),
                       (" " + it.get("unit", ""), {"size": round(15 * f), "bold": True, "color": T.accent})]],
                     size=round(34 * f), fit=False)
            ty += 0.8 * f
        if it.get("title"):
            text(slide, T, cx + pad, ty, iw, title_h, it["title"], size=round(18 * f), color=T.heading, bold=True,
                 min_size=13)
        if it.get("text"):
            body_y = ty + title_h + 0.12
            text(slide, T, cx + pad, body_y, iw, cy + ch - body_y - pad * 0.7, it["text"], size=round(14 * f),
                 color=T.body, line=1.25, min_size=10)


def stats(slide, T, a, d):
    items = [norm(i) for i in d["items"]]
    x, y, w, h = a
    # 版面窄（小尺寸模板、带导航栏）：排成两行两列——前提是半高放得下最小字号的一整块（数字 + 标题 + 说明）
    half_need = 20 / 72 * 1.25 + 0.85 + max([text_height(i["text"], w / 2 - 0.45, 14, 1.2) + 0.1 if i.get("text")
                                             else 0 for i in items] + [0])
    if len(items) == 4 and w / 4 < 2.1 and h / 2 >= half_need:
        stats(slide, T, (x, y, w, h / 2), {**d, "items": items[:2], "note": None})
        stats(slide, T, (x, y + h / 2, w, h / 2), {**d, "items": items[2:]})
        return
    note = d.get("note")
    n = len(items)
    cw = w / n
    # 数字字号按列宽算：最长的那个数字 + 单位要放得下
    def width(i, vs):  # 数字 + 单位（单位字号是数字的 0.4 倍，最小 11pt）的宽度
        return (text_em(str(i.get("value", ""))) * vs + text_em(" " + i.get("unit", "")) * max(11, vs * 0.4)) / 72
    vsize = 88
    while vsize > 20 and max(width(i, vsize) for i in items) > (cw - 0.45) * 0.85:  # 窄栏（小尺寸模板）允许到 20pt
        vsize -= 2
    nh = 0.95 if note else 0

    def layout(vs):  # 这个字号下整块有多高
        vh = vs / 72 * 1.25
        f = min(1.3, max(1.0, vs / 56))
        th = max((text_height(i["text"], cw - 0.45, 14 * f, 1.2)) if i.get("text") else 0 for i in items)
        block = vh + 0.15 + 0.2 + 0.5 * f + (th + 0.1 if th else 0)
        return vh, f, th, block, block + (nh + 0.5 if note else 0)
    vh, f, th, block, total = layout(vsize)
    while total > h and vsize > 20:  # 高度也不够（两行排）就继续缩数字
        vsize -= 2
        vh, f, th, block, total = layout(vsize)
    if total > h:
        WARN.append("大数字页内容超出，删掉说明文字或拆页")
    top = y + max(0, (h - total) / 2)
    for i, it in enumerate(items):
        cx = x + i * cw
        pad = 0.3 if i else 0
        text(slide, T, cx + pad, top, cw - pad - 0.15, vh,
             [[(str(it.get("value", "")), {"size": vsize, "bold": True, "color": T.accent}),
               (" " + it.get("unit", ""), {"size": max(11, round(vsize * 0.4)), "bold": True, "color": T.accent})]],
             size=vsize, fit=False, anchor="b")
        ly = top + vh + 0.15
        hline(slide, T, cx + pad, ly, min(0.7, cw * 0.3), T.primary, 3)
        text(slide, T, cx + pad, ly + 0.2, cw - pad - 0.2, 0.5 * f, it.get("title") or it.get("label", ""),
             size=round(18 * f), color=T.heading, bold=True, min_size=12)
        if it.get("text"):
            text(slide, T, cx + pad, ly + 0.2 + 0.5 * f, cw - pad - 0.2, th + 0.1, it["text"], size=round(14 * f),
                 color=T.muted, min_size=10)
        if i:
            vline(slide, T, cx, top + 0.15, block - 0.15, T.line, 0.75)
    if note:
        b = box(slide, T, x, top + block + 0.5, w, nh, fill=T.tint)
        label_in(b, T, note, 18, T.accent if not T.dark_bg else T.heading, True, "l", margin=0.3)


def process(slide, T, a, d):
    steps = [norm(s) for s in d["steps"]]
    x, y, w, h = a
    n = len(steps)
    cw = (w - GAP * (n - 1)) / n

    def need(f):
        pad = 0.22 * f
        t = max(text_height(s.get("title", ""), cw - 2 * pad, 18 * f) for s in steps)
        b = max((text_height(s["text"], cw - 2 * pad, 14 * f, 1.5)) if s.get("text") else 0 for s in steps)
        return 0.7 * f + 0.35 + pad * 2 + t + 0.12 + b + 0.1, t

    f = zoom(h, need(1.0)[0])
    while f > 1.0 and need(f)[0] > h:
        f -= 0.05
    total, th = need(f)
    dia = 0.7 * f
    card_h = min(h - dia - 0.35, max(total - dia - 0.35, (h - dia - 0.35) * 0.55))
    total = dia + 0.35 + card_h
    cy = y + max(0, (h - total) / 2)
    hline(slide, T, x + cw / 2, cy + dia / 2, w - cw, T.line if T.dark_bg else mix(T.primary, T.bg, 0.6), 3)
    for i, s in enumerate(steps):
        cx = x + i * (cw + GAP)
        if s.get("icon"):
            icon(slide, T, s["icon"], cx + cw / 2 - dia / 2, cy, dia, "solid")
        else:
            c = circle(slide, T, cx + cw / 2 - dia / 2, cy, dia, T.primary)
            label_in(c, T, str(i + 1), round(20 * f), T.on_primary, True, margin=0)
        by = cy + dia + 0.35
        panel(slide, T, cx, by, cw, card_h)
        pad = 0.22 * f
        text(slide, T, cx + pad, by + pad, cw - 2 * pad, th + 0.05, s.get("title", ""), size=round(18 * f),
             color=T.heading, bold=True, align="c", min_size=12)
        if s.get("text"):
            text(slide, T, cx + pad, by + pad + th + 0.12, cw - 2 * pad, card_h - th - 2 * pad - 0.1, s["text"],
                 size=round(14 * f), color=T.body, align="c", line=1.25, min_size=10)


def timeline(slide, T, a, d):
    items = [norm(i) for i in d["items"]]
    x, y, w, h = a
    n = len(items)
    cw = w / n

    def need(f):
        b = max((text_height(i["text"], cw - 0.3, 14 * f, 1.5)) if i.get("text") else 0 for i in items)
        t = max((text_height(i["title"], cw - 0.3, 18 * f)) if i.get("title") else 0 for i in items)
        return 0.75 * f + 0.5 + t + 0.1 + b, t

    f = zoom(h, need(1.0)[0])
    while f > 1.0 and need(f)[0] > h:
        f -= 0.05
    total, th = need(f)
    top = y + max(0, (h - total) / 2)
    ly = top + 0.75 * f + 0.15
    hline(slide, T, x, ly, w, T.line if T.dark_bg else mix(T.primary, T.bg, 0.6), 3)
    for i, it in enumerate(items):
        cx = x + i * cw
        hi = d.get("highlight", n - 1) == i
        circle(slide, T, cx, ly - 0.15, 0.3, T.primary if hi else T.bg, line=T.primary)
        tsize = min(round(24 * f), int((cw - 0.25) * 72 / max(1.0, text_em(it.get("time", "")) * 1.12)))
        text(slide, T, cx, top, cw - 0.2, 0.75 * f, it.get("time", ""), size=max(12, tsize), color=T.accent,
             bold=True, anchor="b", fit=False)
        ty = ly + 0.4
        if it.get("title"):
            text(slide, T, cx, ty, cw - 0.3, th + 0.05, it["title"], size=round(18 * f), color=T.heading, bold=True,
                 min_size=12)
            ty += th + 0.1
        if it.get("text"):
            text(slide, T, cx, ty, cw - 0.3, max(0.4, top + total - ty + 0.1), it["text"], size=round(14 * f),
                 color=T.body, line=1.25, min_size=10)


def compare(slide, T, a, d):
    x, y, w, h = a
    verdict = d.get("verdict")
    vh = 0.85 if verdict else 0
    avail = h - (vh + 0.35 if verdict else 0)
    gap = 0.9
    cw = (w - gap) / 2
    n = max(len(d["left"].get("items", [])), len(d["right"].get("items", [])), 1)
    def row_h(k):  # 字号缩放 k 时，最长一项折行后的行高
        tw = cw - 0.75 - 0.34 * k
        longest = max([text_height(t, tw, 16 * k, 1.2) for s in (d["left"], d["right"]) for t in s.get("items", [])]
                      + [0.3 * k])
        return max(0.62 * k, longest + 0.2 * k)
    rh0 = row_h(1)
    if 0.8 + n * rh0 + 0.35 <= avail:
        f = zoom(avail, 0.8 + n * rh0 + 0.3)
        rh = rh0 * f
    else:  # 放不下（版面矮的模板）：缩小字号、按缩小后的折行重算
        f = 1.0
        while f > 0.7 and 0.8 * f + n * row_h(f) + 0.35 > avail:
            f -= 0.05
        rh = row_h(f)
        if 0.8 * f + n * rh + 0.35 > avail:
            WARN.append("对比页内容超出，删减条目或拆页")
    ph = min(avail, 0.8 * f + n * rh + 0.35)
    top = y + max(0, (avail - ph) / 2)
    for k, (side, good) in enumerate(((d["left"], False), (d["right"], True))):
        cx = x + k * (cw + gap)
        panel(slide, T, cx, top, cw, ph, strong=good)
        hb = box(slide, T, cx, top, cw, 0.8 * f, fill=T.primary if good else mix(T.surface, T.muted, 0.16),
                 radius=T.radius)
        label_in(hb, T, side.get("title", ""), round(20 * f), T.on_primary if good else T.heading, True,
                 margin=0.15)
        for i, it in enumerate(side.get("items", [])):
            iy = top + 0.8 * f + 0.2 + i * rh
            icon(slide, T, "circle-check" if good else "circle-x", cx + 0.3, iy + 0.06, 0.34 * f, "bare")
            text(slide, T, cx + 0.45 + 0.34 * f, iy, cw - 0.75 - 0.34 * f, rh - 0.05, it, size=max(11, round(16 * f)),
                 color=T.heading if good else T.muted, bold=good, line=1.2, min_size=11)
    vs = circle(slide, T, x + cw + gap / 2 - 0.38, top + ph / 2 - 0.38, 0.76, T.heading)
    label_in(vs, T, d.get("vs", "VS"), 15, T.bg, True, margin=0)
    if verdict:
        b = box(slide, T, x, top + ph + 0.35, w, vh, grad=(T.primary, T.secondary), angle=0)
        label_in(b, T, verdict, 19, T.on_primary, True, margin=0.3)


def chart(slide, T, a, d):
    x, y, w, h = a
    if d.get("title"):
        text(slide, T, x, y, w, 0.45, d["title"], size=16, color=T.heading, bold=True)
        y, h = y + 0.55, h - 0.55
    tk = d.get("takeaway")
    cw = w * 0.66 if tk else w
    if d.get("kind") in ("pie", "doughnut") and not tk and cw > h * 1.9:  # 饼图别拉太宽，居中
        x, cw = x + (cw - h * 1.9) / 2, h * 1.9
    series = d.get("series") or [{"name": d.get("name", ""), "values": d["values"]}]
    _chart(slide, T, x, y, cw, h, d.get("kind", "column"), d["categories"], series, d.get("format", "General"),
           d.get("highlight"), size=14 if h > 3.5 else 12)
    if tk:
        tx = x + cw + 0.4
        tw = w - cw - 0.4
        box(slide, T, tx, y, tw, h, fill=T.tint)
        pad = 0.35
        ty = y + pad
        if tk.get("value"):
            em = text_em(str(tk["value"])) + 0.38 * text_em(" " + tk.get("unit", ""))
            vs = int(min(48, (tw - 2 * pad) * 72 / max(1.0, em * 1.12)))
            text(slide, T, tx + pad, ty, tw - 2 * pad, vs / 72 * 1.35,
                 [[(str(tk["value"]), {"size": vs, "bold": True, "color": T.accent}),
                   (" " + tk.get("unit", ""), {"size": round(vs * 0.38), "bold": True, "color": T.accent})]],
                 size=vs, fit=False)
            ty += vs / 72 * 1.35 + 0.15
        if tk.get("title"):
            text(slide, T, tx + pad, ty, tw - 2 * pad, 0.8, tk["title"], size=18, color=T.heading, bold=True)
            ty += 0.85
        if tk.get("text"):
            text(slide, T, tx + pad, ty, tw - 2 * pad, y + h - ty - pad, tk["text"], size=15, color=T.body,
                 line=1.3, min_size=10)


def table(slide, T, a, d):
    x, y, w, h = a
    rows = d["rows"]
    n = len(rows) + 1
    size = 16 if len(d["header"]) <= 4 and n <= 6 else (14 if len(d["header"]) <= 5 else 12)
    rh = min(0.85 if size == 16 else 0.62, h / n)
    th = rh * n
    _table(slide, T, x, y + max(0, (h - th) / 2 * 0.6), w, th, d["header"], rows, d.get("highlight_col"), size,
           d.get("col_widths"))


def quote(slide, T, a, d):
    x, y, w, h = a
    mw = min(w, 10.0)
    mx = x + (w - mw) / 2
    th = min(h - 1.4, max(1.2, text_height(d["text"], mw - 0.4, 32, 1.3) + 0.3))
    top = y + max(0, (h - th - 1.4) / 2)
    text(slide, T, mx, top - 0.25, 1.2, 1.15, "“", size=80, color=T.accent, bold=True, fit=False, heading=True)
    text(slide, T, mx + 0.2, top + 0.9, mw - 0.4, th, d["text"], size=32, color=T.heading, bold=True, line=1.3,
         align="c", anchor="m", heading=True, min_size=18)
    if d.get("by"):
        hline(slide, T, mx + mw / 2 - 0.3, top + th + 1.0, 0.6, T.accent, 2.5)
        text(slide, T, mx, top + th + 1.15, mw, 0.4, d["by"], size=15, color=T.muted, align="c")


def statement(slide, T, a, d):
    x, y, w, h = a
    al = d.get("align", "l")
    mw = min(w, 10.5)
    mx = x if al == "l" else x + (w - mw) / 2
    th = min(h * 0.6, max(0.9, text_height(d["text"], mw, 40, 1.2) + 0.2))
    sh = text_height(d.get("sub", ""), mw, 18, 1.4) + 0.2 if d.get("sub") else 0
    total = th + (0.55 + sh if sh else 0)
    top = y + max(0, (h - total) / 2)
    text(slide, T, mx, top, mw, th, d["text"], size=40, color=T.heading, bold=True, line=1.2, align=al, anchor="b",
         heading=True, min_size=22)
    if d.get("sub"):
        hline(slide, T, mx if al == "l" else mx + mw / 2 - 0.4, top + th + 0.25, 0.8, T.accent, 3)
        text(slide, T, mx, top + th + 0.5, mw, min(sh, y + h - top - th - 0.5), d["sub"], size=18, color=T.muted,
             line=1.35, align=al, min_size=12)


def paragraphs(slide, T, a, d):
    x, y, w, h = a
    paras = d["paras"] if isinstance(d.get("paras"), list) else [d.get("paras") or d.get("text", "")]
    mw = min(w, 10.0)
    need = text_height("\n".join(paras), mw, 18, 1.45 * 1.2) + 0.15 * len(paras)
    top = y + max(0, (h - need) / 2 * 0.6)
    text(slide, T, x, top, mw, h - (top - y), paras, size=18, color=T.body, line=1.45, after=12, min_size=12)


def image(slide, T, a, d):
    x, y, w, h = a
    iw = w * d.get("ratio", 0.5)
    left = d.get("side", "left") == "left"
    ix = x if left else x + w - iw
    picture_cover(slide, d["path"], ix, y, iw, h - (0.35 if d.get("caption") else 0))
    tx = x + iw + 0.5 if left else x
    tw = w - iw - 0.5
    ty = y
    if d.get("title"):
        text(slide, T, tx, ty, tw, 1.0, d["title"], size=24, color=T.heading, bold=True, heading=True)
        ty += 1.1
    if d.get("items"):
        bullets(slide, T, (tx, ty, tw, y + h - ty), {"items": d["items"]})
    elif d.get("text"):
        text(slide, T, tx, ty, tw, y + h - ty, d["text"], size=16, color=T.body, line=1.4)
    if d.get("caption"):
        text(slide, T, ix, y + h - 0.3, iw, 0.3, d["caption"], size=10, color=T.muted)


def split(slide, T, a, d):
    x, y, w, h = a
    r = d.get("ratio", 0.5)
    gap = 0.5
    lw = (w - gap) * r
    draw(slide, T, (x, y, lw, h), d["left"])
    draw(slide, T, (x + lw + gap, y, w - lw - gap, h), d["right"])


RECIPES = {"bullets": bullets, "cards": cards, "stats": stats, "process": process, "timeline": timeline,
           "compare": compare, "chart": chart, "table": table, "quote": quote, "statement": statement,
           "text": paragraphs, "image": image, "split": split}

REQUIRED = {"bullets": ["items"], "cards": ["items"], "stats": ["items"], "process": ["steps"],
            "timeline": ["items"], "compare": ["left", "right"], "chart": ["categories"],
            "table": ["header", "rows"], "quote": ["text"], "statement": ["text"], "text": [],
            "image": ["path"], "split": ["left", "right"]}

LIMITS = {"cards": 8, "stats": 4, "process": 6, "timeline": 6, "bullets": 10}


def draw(slide, T, area, d):
    kind = d.get("type")
    if kind not in RECIPES:
        raise ValueError(f"未知版式 {kind}，可用：{', '.join(RECIPES)}")
    for k in REQUIRED[kind]:
        if k not in d:
            raise ValueError(f"版式 {kind} 缺少字段 {k}")
    key = {"process": "steps"}.get(kind, "items")
    if kind in LIMITS and len(d[key]) > LIMITS[kind]:
        WARN.append(f"{kind} 放了 {len(d[key])} 项，超过上限 {LIMITS[kind]}，应拆成两页")
    RECIPES[kind](slide, T, area, d)


def lead(slide, T, area, s):
    """页面的一句话结论，放在内容区顶部，返回剩余区域"""
    x, y, w, h = area
    lh = max(0.5, count_lines(s, w, 20) * 20 * 1.3 / 72)
    text(slide, T, x, y, w, lh, s, size=20, color=T.heading, bold=True, line=1.15, min_size=15)
    return (x, y + lh + 0.3, w, h - lh - 0.3)


def conclusion(slide, T, area, s):
    """页面底部的结论条，返回剩余区域"""
    x, y, w, h = area
    ch = max(0.75, count_lines(s, w - 0.6, 18) * 18 * 1.3 / 72 + 0.3)
    b = box(slide, T, x, y + h - ch, w, ch, grad=(T.primary, T.secondary), angle=0)
    label_in(b, T, s, 18, T.on_primary, True, "l", margin=0.3)
    return (x, y, w, h - ch - 0.3)


def source(slide, T, area, s):
    x, y, w, h = area
    text(slide, T, x, y + h - 0.28, w, 0.28, s, size=10, color=T.muted, fit=False)
    return (x, y, w, h - 0.4)
