"""各种文本格式 → md（plan.py 只认 md，转成 md 也方便检查和手改）。用法：
    python3 convert.py 内容.docx --out work/content.md

支持：
  .md .markdown          原样
  .txt                   自动识别编码（UTF-8 / GBK / UTF-16）；按「第一章」「一、」「（一）」「1.1」「1.」「•」这类编号认出标题和列表
  .docx                  标题样式（含大纲级别）、列表、表格、加粗、引用样式、图片；没用标题样式的文档按编号和整段加粗猜标题
  .doc .rtf .odt .wps .html 等   先用 LibreOffice 转成 docx 再处理
  .pdf                   用 pdftotext 抽文字后按 txt 处理，只能尽力（表格和分栏会乱）
转出来的 md 一定要读一遍：哪句是标题、哪些是列表猜错了，直接改 md 再跑 plan.py。
"""
import argparse
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import zipfile

MD_EXT = (".md", ".markdown")
LO_EXT = (".doc", ".rtf", ".odt", ".wps", ".wpt", ".dot", ".dotx", ".docm", ".html", ".htm", ".fodt")
IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".bmp")

CN = "一二三四五六七八九十百"
H2 = re.compile(rf"^\s*(第[{CN}\d]+[章部篇]|[{CN}]+\s*[、.．]|PART\s*\d+|Part\s*\d+)")
H3 = re.compile(rf"^\s*(第[{CN}\d]+节|[（(][{CN}]+[）)]|\d+\.\d+(\.\d+)?(?:\s+|(?=[\u4e00-\u9fff]))(?![%％万亿千元倍]))")
ORDERED = re.compile(r"^\s*(?:\d{1,2}\s*[.、．)）](?!\d)|[①②③④⑤⑥⑦⑧⑨⑩])\s*(.+)$")
BULLET_CHARS = "•·●○■□◆◇▪▸►✓✔\uf0a7\uf0b7\uf06c\uf076\uf0d8\uf0fc"  # 后几个是 Word 符号字体的项目符号
BULLET = re.compile(rf"^\s*(?:[{BULLET_CHARS}]\s*|[-*–]\s+)(.+)$")
UNIT_ONLY = re.compile(r"\d+\.\d+(\.\d+)?\s*(%|％|个?百分点|个点|万元|亿元|万人|万户|分|万|亿|千|元|倍|吨|小时|天|年|次|项|人|户|家|台|"
                       r"公里|米|秒|周|月|个|件|km|kg|t)?\s*")  # 「4.8 分」「3.5个百分点」是数字，不是 1.1 式小节号
KV = re.compile(r"^[^：:，。]{1,12}[：:]\s*\S")
END_PUNCT = "。；，、！.;,!：:"


def is_short_heading(t, limit=30):
    t = t.strip()
    return 0 < len(t) <= limit and t[-1] not in END_PUNCT and not re.fullmatch(r"[\d\s.,%％]+", t)


# ---------- 纯文本 ----------
def read_text(path):
    raw = open(path, "rb").read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    for enc in ("utf-8-sig", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def unwrap(lines):
    """PDF 的硬换行：上一行接近满行、又没以句末标点结尾，就和下一行接成一段。"""
    lens = [len(x) for x in lines if len(x.strip()) > 10]
    full = max(statistics.median(lens) * 0.85, 20) if lens else 10 ** 9
    out = []
    for ln in lines:
        s = ln.strip()
        if (out and out[-1] and s and len(out[-1]) >= full and out[-1][-1] not in "。！？；：.!?;:”」"
                and not (H2.match(s) or H3.match(s) or ORDERED.match(s) or BULLET.match(s))):
            if out[-1].endswith("-") and s[:1].isascii() and s[:1].isalpha():
                out[-1] = out[-1][:-1] + s  # 英文断词的连字符
            elif out[-1][-1].isascii() and out[-1][-1].isalnum() and s[0].isascii() and s[0].isalnum():
                out[-1] += " " + s
            else:
                out[-1] += s
        else:
            out.append(s)
    return out


def text_blocks(text, hard_wrapped=False):
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    joined = []
    for ln in lines:  # 单独一行的项目符号（PDF 里常见）接到下一行文字前面
        if joined and re.fullmatch(rf"\s*[{BULLET_CHARS}]\s*", joined[-1]) and ln.strip():
            joined[-1] = "• " + ln.strip()
        elif not (joined and re.fullmatch(rf"\s*[{BULLET_CHARS}]\s*", joined[-1])):
            joined.append(ln)
    # Word 另存的 txt：自动编号是「1.<Tab>文字」「•<Tab>文字」，别当成表格
    lines = [re.sub(rf"^(\s*(?:\d{{1,2}}[.、．)）]|[{BULLET_CHARS}\-*–]))\t+", r"\1 ", ln) for ln in joined]
    if hard_wrapped:
        lines = [ln for ln in lines if not re.fullmatch(r"\s*(第\s*\d+\s*页.*|[-—]\s*\d+\s*[-—]|\d+\s*/\s*\d+|Page\s*\d+.*)\s*", ln)]
        lines = unwrap(lines)
    blocks = []
    i, grp = 0, 0  # grp：中间没有空行的连续几行算一组
    while i < len(lines):
        ln = lines[i].strip()
        if not ln:
            i, grp = i + 1, grp + 1
            continue
        if "\t" in ln:  # 制表符分隔的连续行 → 表格（行首的 Tab 是空的左上角格子，不能去掉）
            j = i
            while j < len(lines) and "\t" in lines[j].strip():
                j += 1
            if j - i >= 2:
                blocks.append({"t": "table", "rows": [[c.strip() for c in lines[k].split("\t")]
                                                      for k in range(i, j)]})
                i = j
                continue
        nxt = next((x.strip() for x in lines[i + 1:] if x.strip()), "")
        lone = (is_short_heading(ln, 20) and len(nxt) > len(ln) and not KV.match(ln)
                and (len(nxt) >= 12 or ORDERED.match(nxt) or BULLET.match(nxt))  # 下面跟的是正文或列表才像标题
                and not (H2.match(nxt) or H3.match(nxt)))
        blocks.append({"t": "line", "text": ln, "lone": lone, "grp": grp})
        i += 1
    return blocks


# ---------- docx ----------
def numbering_formats(doc):
    """numId → {层级: 编号格式}，用来区分有序列表、无序列表和「一、」式的章节编号。"""
    from docx.oxml.ns import qn
    try:
        root = doc.part.numbering_part.element
    except (KeyError, NotImplementedError, AttributeError):
        return {}
    absf = {}
    for a in root.findall(qn("w:abstractNum")):
        absf[a.get(qn("w:abstractNumId"))] = {
            int(lv.get(qn("w:ilvl"))): (lv.find(qn("w:numFmt")).get(qn("w:val")) if lv.find(qn("w:numFmt")) is not None
                                        else "decimal") for lv in a.findall(qn("w:lvl"))}
    out = {}
    for n in root.findall(qn("w:num")):
        ref = n.find(qn("w:abstractNumId"))
        if ref is not None:
            out[n.get(qn("w:numId"))] = absf.get(ref.get(qn("w:val")), {})
    return out


def para_info(p, styles_outline):
    """段落的标题级别（1 起，None 表示不是标题）、编号 (numId, 层级)。"""
    from docx.oxml.ns import qn
    name = (p.style.name if p.style is not None else "") or ""
    level = None
    if name.lower() == "title" or name == "标题":
        level = 0
    else:
        m = re.match(r"^(heading|标题)\s*(\d)$", name, re.I)
        if m:
            level = int(m.group(2))
    ppr = p._p.pPr
    ol = ppr.find(qn("w:outlineLvl")) if ppr is not None else None
    if level is None and ol is not None and ol.get(qn("w:val")) not in (None, "9"):
        level = int(ol.get(qn("w:val"))) + 1
    if level is None and p.style is not None:
        level = styles_outline.get(p.style.style_id)
    num = None
    numpr = ppr.find(qn("w:numPr")) if ppr is not None else None
    if numpr is None and p.style is not None and p.style.element.pPr is not None:
        numpr = p.style.element.pPr.find(qn("w:numPr"))
    if numpr is not None and numpr.find(qn("w:numId")) is not None \
            and numpr.find(qn("w:numId")).get(qn("w:val")) != "0":  # numId=0 是「取消编号」
        ilvl = numpr.find(qn("w:ilvl"))
        num = (numpr.find(qn("w:numId")).get(qn("w:val")), int(ilvl.get(qn("w:val"))) if ilvl is not None else 0)
    return level, num, name


def run_bold(run, p):
    if run.bold is not None:
        return run.bold
    for st in (run.style, p.style):
        while st is not None:
            if st.font.bold is not None:
                return st.font.bold
            st = st.base_style
    return False


def para_text(p, save_image):
    """段落 → (带 **加粗** 的文字, 是否整段加粗, 图片路径列表)。"""
    from docx.oxml.ns import qn
    from docx.text.run import Run
    parts, imgs, bold_chars, all_chars = [], [], 0, 0
    skip = (qn("w:txbxContent"), "{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback")  # 文本框里的字不混进正文；兼容内容只取一份
    for r in p._p.iter(qn("w:r")):
        if any(a.tag in skip for a in r.iterancestors()):
            continue
        run = Run(r, p)
        for blip in r.iter(qn("a:blip")):
            rid = blip.get(qn("r:embed"))
            if rid and rid in p.part.related_parts:
                path = save_image(p.part.related_parts[rid])
                if path:
                    imgs.append(path)
        t = run.text.replace("\t", " ")
        if not t:
            continue
        b = run_bold(run, p) and t.strip()
        all_chars += len(t.strip())
        bold_chars += len(t.strip()) if b else 0
        if parts and parts[-1][1] == bool(b):
            parts[-1][0] += t
        else:
            parts.append([t, bool(b)])
    text = "".join(t[:len(t) - len(t.lstrip())] + f"**{t.strip()}**" + t[len(t.rstrip()):] if b else t
                   for t, b in parts)
    text = re.sub(r"\*\*\s*\*\*", "", text).strip()
    return text, all_chars > 0 and bold_chars == all_chars, imgs


def cell_text(tc):
    """单元格文字，嵌套表格里的字一起摊平。"""
    from docx.oxml.ns import qn
    paras = ("".join(t.text or "" for t in p.iter(qn("w:t"))).strip() for p in tc.iter(qn("w:p")))
    return " ".join(x for x in paras if x)


def docx_blocks(path, media_dir, md_dir):
    import docx
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    doc = docx.Document(path)
    fmts = numbering_formats(doc)
    styles_outline = {}
    for st in doc.styles:
        el = getattr(st, "element", None)
        ol = el.find(qn("w:pPr") + "/" + qn("w:outlineLvl")) if el is not None else None
        if ol is not None and ol.get(qn("w:val")) not in (None, "9"):
            styles_outline[st.style_id] = int(ol.get(qn("w:val"))) + 1
    count = [0]

    def save_image(part):
        ext = os.path.splitext(part.partname)[1].lower()
        if ext not in IMG_EXT:
            print(f"  （跳过 {ext} 格式的图片：PPT 里放不了，需要的话另存成 png 写进 md）")
            return None
        os.makedirs(media_dir, exist_ok=True)
        count[0] += 1
        dst = os.path.join(media_dir, f"img{count[0]:02d}{ext}")
        with open(dst, "wb") as f:
            f.write(part.blob)
        return os.path.relpath(dst, md_dir)

    def walk(parent):
        for el in parent.iterchildren():
            if el.tag == qn("w:sdt"):  # 内容控件（Word 自动目录等）
                content = el.find(qn("w:sdtContent"))
                if content is not None:
                    yield from walk(content)
            elif el.tag == qn("w:p"):
                yield Paragraph(el, doc.part)
            elif el.tag == qn("w:tbl"):
                yield Table(el, doc.part)

    blocks = []
    for item in walk(doc.element.body):
        if isinstance(item, Table):
            rows, above = [], []
            for row in item.rows:
                cells = []
                for c in row.cells:
                    if not cells or c._tc is not cells[-1][0]:  # 横向合并的格子只取一次
                        merged_down = any(c._tc is x for x in above)  # 纵向合并：只在第一行写字
                        cells.append((c._tc, "" if merged_down else cell_text(c._tc)))
                above = [tc for tc, _ in cells]
                rows.append([t for _, t in cells])
            if rows:
                blocks.append({"t": "table", "rows": rows})
            continue
        level, num, style = para_info(item, styles_outline)
        if re.match(r"^(toc|目录)\s*(\d|heading|标题)", style, re.I):  # Word 自动目录的标题和条目
            continue
        text, all_bold, imgs = para_text(item, save_image)
        for line in (text.split("\n") if level is None and num is None else [text.replace("\n", " ")]):
            line = line.strip()
            if not line:
                continue
            b = {"t": "line", "text": line, "lone": all_bold and is_short_heading(re.sub(r"\*", "", line))}
            if level is not None:
                b = {"t": "styled_h", "level": level, "text": re.sub(r"\*\*(.+?)\*\*", r"\1", line)}
            elif re.search(r"quote|引用", style, re.I):
                b = {"t": "quote", "text": line}
            elif num is not None:
                fmt = fmts.get(num[0], {}).get(num[1], "none")  # 找不到编号定义就当普通段落
                if fmt == "none":
                    pass
                elif re.match(r"chinese|ideograph|japanese|taiwanese", fmt) and is_short_heading(line):
                    b = {"t": "line", "text": line, "mark": "h2" if num[1] == 0 else "h3"}
                else:
                    b = {"t": "item", "ordered": fmt != "bullet", "depth": num[1], "text": line}
            blocks.append(b)
        blocks.extend({"t": "image", "path": p} for p in imgs)
    return blocks


# ---------- 统一出 md ----------
def classify(b):
    """纯文本行 → 标题标记 / 列表项 / 段落。"""
    if b["t"] != "line":
        return b
    if b.get("mark"):
        return {"t": "cand", "kind": b["mark"], "text": b["text"]}
    raw = re.sub(r"\*\*", "", b["text"])
    if is_short_heading(raw) and H2.match(raw):
        return {"t": "cand", "kind": "h2", "text": raw}
    if is_short_heading(raw) and H3.match(raw) and not UNIT_ONLY.fullmatch(raw.strip()):
        return {"t": "cand", "kind": "h3", "text": raw}
    m = ORDERED.match(b["text"])
    if m:
        return {"t": "item", "ordered": True, "depth": 0, "text": m.group(1).strip()}
    m = BULLET.match(b["text"])
    if m and not b["text"].lstrip().startswith("**"):
        return {"t": "item", "ordered": False, "depth": 0, "text": m.group(1).strip()}
    if b.get("lone"):
        return {"t": "cand", "kind": "hx", "text": raw}
    if re.fullmatch(r"[“「].{4,80}[”」]", raw):
        return {"t": "quote", "text": raw[1:-1]}  # 金句版式自带引号
    return {"t": "para", "text": b["text"], "grp": b.get("grp")}


def resolve_headings(blocks):
    """把各种标题线索统一成 # / ## / ###。"""
    styled = [b["level"] for b in blocks if b["t"] == "styled_h"]
    if len(styled) >= 2 or 0 in styled:
        levels = sorted(set(styled))
        first = next((b for b in blocks if b["t"] != "image"), None)
        title_lv = 0 if 0 in levels else (levels[0] if first and first["t"] == "styled_h" and styled.count(levels[0]) == 1
                                          else None)
        if title_lv is None and first and first["t"] == "line" and is_short_heading(re.sub(r"\*", "", first["text"]), 40):
            i = blocks.index(first)  # 没用标题样式、写在最前面的一行短句是封面标题
            blocks = blocks[:i] + [dict(first, t="styled_h", level=-1)] + blocks[i + 1:]
            levels, title_lv = [-1] + levels, -1
        rest = [lv for lv in levels if lv != title_lv]
        rank = {lv: i + 2 for i, lv in enumerate(rest)}
        rank[title_lv] = 1
        out = []
        for b in blocks:
            if b["t"] == "styled_h":
                out.append({"t": "h", "level": min(rank[b["level"]], 4), "text": re.sub(r"\*\*", "", b["text"])})
                continue
            c = classify(dict(b, lone=False, mark=None))  # 有标题样式时只认样式，其余行只分列表和段落
            out.append({"t": "para", "text": b["text"]} if c["t"] == "cand" else c)
        return out
    blocks = [{"t": "line", "text": b["text"]} if b["t"] == "styled_h" else b for b in blocks]
    blocks = [classify(b) for b in blocks]
    kinds = {b["kind"] for b in blocks if b["t"] == "cand"}
    if "h2" in kinds:
        lv = {"h2": 2, "h3": 3, "hx": 3}
    elif "h3" in kinds:
        lv = {"h3": 2, "hx": 3}
    else:
        lv = {"hx": 3}
    out = []
    first = next((b for b in blocks if b["t"] != "image"), None)
    if first and (first["t"] == "para" or first.get("kind") == "hx") \
            and is_short_heading(re.sub(r"\*", "", first["text"]), 40):
        out.append({"t": "h", "level": 1, "text": re.sub(r"\*\*", "", first["text"])})
        blocks = blocks[blocks.index(first) + 1:]
    for b in blocks:
        out.append({"t": "h", "level": lv[b["kind"]], "text": b["text"]} if b["t"] == "cand" else b)
    return out


def listish(b, first):
    """能和前面的段落连成列表：「小标题：说明」，或 txt 里没隔空行、都很短的几行。"""
    if b["t"] != "para":
        return False
    t = re.sub(r"\*\*", "", b["text"])
    if KV.match(t) and len(t) <= 80:
        return True
    return b.get("grp") is not None and b["grp"] == first.get("grp") and is_short_heading(t, 40)


def kv_lists(blocks):
    """标题之后连续 ≥2 行「小标题：说明」或连续短行 → 列表（plan.py 会做成卡片 / 要点 / 大数字）。
    封面下面的「日期：」「汇报人：」不动。"""
    out = list(blocks)
    i = 0
    while i < len(out):
        j = i
        while j < len(out) and listish(out[j], out[i]):
            j += 1
        before_h = not any(x["t"] == "h" and x["level"] >= 2 for x in out[:i])
        if j - i >= 2 and not before_h:
            for k in range(i, j):
                out[k] = {"t": "item", "ordered": False, "depth": 0, "text": out[k]["text"]}
        i = max(j, i + 1)
    return out


def esc_cell(s):
    return s.replace("|", "｜").strip()


def to_md(blocks):
    out, prev = [], None
    for b in blocks:
        t = b["t"]
        if t == "h":
            s = "#" * b["level"] + " " + b["text"]
        elif t == "item":
            s = "  " * b["depth"] + ("1. " if b["ordered"] else "- ") + b["text"]
        elif t == "quote":
            s = "> " + b["text"]
        elif t == "image":
            s = f"![]({b['path']})"
        elif t == "table":
            w = max(len(r) for r in b["rows"])
            rows = [r + [""] * (w - len(r)) for r in b["rows"]]
            s = "\n".join(["| " + " | ".join(esc_cell(c) for c in rows[0]) + " |", "|" + "---|" * w] +
                          ["| " + " | ".join(esc_cell(c) for c in r) + " |" for r in rows[1:]])
        else:
            s = b["text"]
        same_list = t == "item" and prev == ("item", b["ordered"])
        out.append(("\n" if same_list else "\n\n") + s if out else s)
        prev = (t, b.get("ordered"))
    return "".join(out) + "\n"


# ---------- 入口 ----------
def libreoffice_to_docx(path, workdir):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from render import soffice_bin
    profile = tempfile.mkdtemp(prefix="lo-")
    try:
        r = subprocess.run([soffice_bin(), f"-env:UserInstallation=file://{profile}", "--headless",
                            "--convert-to", "docx:MS Word 2007 XML", "--outdir", workdir, path],  # html 要显式指定过滤器
                           capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        sys.exit("LibreOffice 转换超过 5 分钟，已放弃")
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    out = os.path.join(workdir, os.path.splitext(os.path.basename(path))[0] + ".docx")
    if not os.path.exists(out):
        detail = " ".join((r.stderr or r.stdout or "").strip().splitlines()[-2:])
        sys.exit(f"LibreOffice 没能把 {os.path.basename(path)} 转成 docx（{detail}）：用 Word/WPS 另存为 .docx 再试")
    return out


def convert(src, out):
    """src（任意支持的格式）→ out（md 文件），返回 out。"""
    ext = os.path.splitext(src)[1].lower()
    if not os.path.exists(src):
        sys.exit(f"找不到 {src}")
    md_dir = os.path.dirname(os.path.abspath(out))
    os.makedirs(md_dir, exist_ok=True)
    # 目录名只留安全字符：md 的图片语法里不能有空格和括号
    media = os.path.join(md_dir, re.sub(r"[^\w.-]", "_", os.path.splitext(os.path.basename(out))[0]) + "-media")
    if ext in MD_EXT:
        md = read_text(src)
    elif ext == ".txt" or ext == "":
        text = read_text(src)
        md = text if re.search(r"^#{1,3}\s+\S", text, re.M) else to_md(kv_lists(resolve_headings(text_blocks(text))))
    elif ext == ".pdf":
        if not shutil.which("pdftotext"):
            sys.exit("找不到 pdftotext（poppler）。macOS: brew install poppler；Ubuntu: apt install poppler-utils")
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", "-nopgbrk", src, "-"], capture_output=True)
        if r.returncode:
            sys.exit(f"pdftotext 读不了这个 PDF（{r.stderr.decode('utf-8', 'replace').strip()[:200]}）：可能损坏或加密")
        text = r.stdout.decode("utf-8", errors="replace")
        if not text.strip():
            sys.exit("这个 PDF 里抽不出文字（可能是扫描件）：先 OCR，或者直接给 Word / txt")
        md = to_md(kv_lists(resolve_headings(text_blocks(text, hard_wrapped=True))))
    elif ext == ".docx" or ext in LO_EXT:
        with tempfile.TemporaryDirectory() as tmp:
            # 扩展名是 .docx 但其实是 rtf / 老 doc 的，也交给 LibreOffice
            path = src if ext == ".docx" and zipfile.is_zipfile(src) else libreoffice_to_docx(os.path.abspath(src), tmp)
            md = to_md(kv_lists(resolve_headings(docx_blocks(path, media, md_dir))))
    elif ext == ".pages":
        sys.exit("Pages 文档请先在 Pages 里「导出为 → Word」再试")
    else:
        sys.exit(f"不支持 {ext}：支持 md / txt / docx / doc / rtf / odt / wps / html / pdf")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--out", help="输出的 md，默认 work/<文件名>.md")
    a = ap.parse_args()
    out = a.out or os.path.join("work", os.path.splitext(os.path.basename(a.src))[0] + ".md")
    convert(a.src, out)
    print(f"已转成 {out}：读一遍，标题和列表认错了就直接改 md，再跑 plan.py")


if __name__ == "__main__":
    main()
