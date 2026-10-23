"""md + 模板画像 → 草稿 deck.json。用法：
    python3 plan.py content.md work/profile.json --out deck.json
内容也可以是 txt / docx / doc / rtf / odt / wps / html / pdf：先用 convert.py 转成 md（存到 profile 旁边的 <文件名>.converted.md）。

规则（详见 references/matching.md）：
  # 一级标题 → 封面；## 二级标题 → 章节页（≥3 个时生成目录）；### 三级标题 → 一页内容
  表格有数字列 → 图表（时间序列用折线/柱状，占比用环形，长类目用横条）；没数字 → 表格
  有序列表 → 流程；带年份/阶段开头 → 时间线；每项都带数字且 ≤4 项 → 大数字；「小标题：说明」→ 卡片；其余 → 要点
  引用 → 金句页；只有一两句话 → 观点页；段落 → 正文页；短段落放在版式上方做结论句
原文不改写：上屏的字直接取自 md，完整原文进演讲者备注。草稿生成后由模型逐页检查、删减、调整。
"""
import argparse
import os
import re

from common import load_json, profile_template, save_json
from convert import MD_EXT, convert, read_text

DATE = re.compile(r"(19|20)\d{2}\s*[年./\-]\s*\d{1,2}|日期[：:]")
UNITS = ("% ％ 亿千瓦时 万千瓦时 万亿 亿元 万元 万人次 万人 万户 万家 万次 万件 万台 万吨 万千瓦 千瓦时 千瓦 亿 万 千 倍 千克 克 毫秒 TOPS GB TB "
         "mAh GWh MWh kWh nm mm km GW MW x X k K + 元 起 家 个 人次 人 户 天 小时 分钟 秒 年 次 项 款 座 所 台 吨 公里 处 场").split()
# 长的单位放前面：「千克」「km」不能被「千」「k」先匹配走
NUM = re.compile(r"(?<![A-Za-z])([+\-]?\d[\d,]*(?:\.\d+)?)\s*("
                 + "|".join(re.escape(u) for u in sorted(UNITS, key=len, reverse=True)) + ")?")
TIME = re.compile(r"^\s*(\d{4}\s*年\s*\d{1,2}\s*月|\d{4}\s*(年|\.|/|-|$)|\d{4}\s*Q\d|Q\d|\d{1,2}\s*月|第.{1,3}(阶段|期|步|周|天)|Phase|阶段|\d{1,2}:\d{2}|Day\s*\d)",
                  re.I)
TITLED = re.compile(r"^\s*(?:\*\*(.+?)\*\*|__(.+?)__)\s*[：:—\-–]?\s*(.*)$|^\s*([^：:？?]{2,16}[：:？?])\s*(.+)$")
ICON_WORDS = [
    ("coins", "成本 价格 费用 钱 预算 收入 营收 利润 资金"), ("users", "客户 用户 会员 人群 观众 游客 患者 学员"),
    ("trending-up", "增长 提升 上涨 提高 翻倍 增速"), ("shield-check", "安全 合规 风控 保障 保护 隐私"),
    ("zap", "效率 速度 快 即时 秒级 实时"), ("database", "数据 数据库 指标 报表"), ("brain", "AI 智能 模型 算法 大模型"),
    ("hospital", "医院 门诊 科室"), ("heart-pulse", "健康 慢病 体检 心 血压"), ("stethoscope", "医生 诊疗 问诊 医疗"),
    ("graduation-cap", "学生 教育 学习 课程 培训 考试"), ("factory", "工厂 产线 车间 生产 制造"),
    ("badge-check", "质量 品质 良率 认证 标准"), ("clock", "时间 周期 时长 工期 等待"), ("triangle-alert", "风险 问题 痛点 隐患 故障"),
    ("target", "目标 定位 精准 KPI"), ("users-round", "团队 人才 组织 员工 人员"), ("workflow", "流程 协同 环节 链路"),
    ("handshake", "合作 服务 伙伴 生态 渠道"), ("package", "产品 交付 包装 库存"), ("truck", "物流 运输 配送 供应链"),
    ("map", "旅游 线路 地图 目的地"), ("hotel", "酒店 住宿 民宿"), ("mountain", "景区 山 自然 户外"),
    ("landmark", "文化 历史 古城 博物馆 政府"), ("store", "门店 零售 商户 店铺"), ("megaphone", "营销 宣传 推广 品牌 传播"),
    ("message-circle", "沟通 反馈 评价 咨询 客服"), ("cpu", "芯片 算力 设备 硬件"), ("leaf", "绿色 环保 低碳 节能"),
    ("gauge", "能耗 产能 OEE 稼动 性能"), ("wrench", "维修 运维 保养 检修"), ("search", "调研 分析 洞察 发现"),
    ("calendar", "活动 节庆 日程 季度"), ("utensils", "美食 餐饮 小吃"), ("award", "荣誉 奖 第一 领先"),
    ("lightbulb", "创新 想法 方案 思路"), ("smile", "满意 体验 口碑 好评"), ("wallet", "理财 财富 资产 存款"),
    ("landmark", "银行 金融 机构"), ("scale", "法律 法规 监管 政策"), ("book-open", "知识 教材 内容 案例"),
]


# ---------- 解析 md ----------
def parse(md):
    blocks, i = [], 0
    lines = md.splitlines()
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip() or re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", ln):
            i += 1
            continue
        if ln.startswith("```"):
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                i += 1
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            blocks.append({"t": "h", "level": len(m.group(1)), "text": clean(m.group(2))})
            i += 1
            continue
        if ln.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [clean(c) for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells if c):
                    rows.append(cells)
                i += 1
            if rows:
                blocks.append({"t": "table", "header": rows[0], "rows": rows[1:]})
            continue
        if ln.lstrip().startswith(">"):
            q = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                q.append(lines[i].lstrip()[1:].strip())
                i += 1
            blocks.append({"t": "quote", "text": clean(" ".join(x for x in q if x))})
            continue
        m = re.match(r'^\s*!\[(.*?)\]\(\s*(\S+?)(?:\s+"[^"]*")?\s*\)', ln)
        if m:
            if re.match(r"https?://", m.group(2)):
                print(f"  （跳过网络图片 {m.group(2)}：先下载到本地再写进 md）")
            else:
                blocks.append({"t": "image", "alt": m.group(1), "path": m.group(2)})
            i += 1
            continue
        if re.match(r"^\s*([-*+]|\d+[.)、])\s+", ln):
            items, ordered = [], bool(re.match(r"^\s*\d+[.)、]", ln))
            base = len(ln) - len(ln.lstrip())
            item_re = r"^\s*([-*+]|\d+[.)、])\s+(.*)$"
            while i < len(lines):
                cur = lines[i]
                if not cur.strip():  # 松散列表：空行后面还是同级列表项就继续
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    nxt = lines[j] if j < len(lines) else ""
                    if re.match(item_re, nxt) and len(nxt) - len(nxt.lstrip()) <= base + 1:
                        i = j
                        continue
                    break
                if re.match(r"^\s*(#{1,6}\s|\||>|```|!\[)", cur):  # 标题、表格、引用不是续行
                    break
                ind = len(cur) - len(cur.lstrip())
                mm = re.match(item_re, cur)
                if mm and ind <= base + 1:
                    items.append(mm.group(2).strip())
                elif items:  # 子项和续行并入上一项
                    sub = re.sub(r"^\s*([-*+]|\d+[.)、])\s+", "", cur).strip()
                    items[-1] += ("；" if mm else "") + sub
                i += 1
            blocks.append({"t": "list", "ordered": ordered, "items": items})
            continue
        para = [ln.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^\s*(#|\||>|[-*+]\s|\d+[.)、]\s|!\[|```)",
                                                                     lines[i]):
            para.append(lines[i].strip())
            i += 1
        blocks.append({"t": "para", "text": clean(" ".join(para)), "raw": " ".join(para)})
    return blocks


def clean(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    return s.strip()


def unbold(s):
    return re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m.group(1) or m.group(2), s).strip()


def outline(blocks, fallback_title):
    doc = {"title": fallback_title, "subtitle": [], "meta": [], "sections": []}
    sec, unit = None, None
    seen_h1 = False
    for b in blocks:
        if b["t"] == "h" and b["level"] == 1 and not seen_h1:
            doc["title"], seen_h1 = unbold(b["text"]), True
            mm = re.match(r"^(.+?)\s*(——|--|\s-\s|\s\|\s)\s*(.+)$", doc["title"])
            if mm:
                doc["title"], doc["subtitle"] = mm.group(1), [mm.group(3)]
            continue
        if b["t"] == "h" and b["level"] <= 2:
            t = re.sub(r"^\s*([一二三四五六七八九十]+[、.]|\d+[.、]|第.{1,3}[章部分节][：:、\s]?|PART\s*\d+)\s*", "",
                       unbold(b["text"]))
            kick, sub = "", ""
            mm = re.match(r"^(开场|引言|前言|序言?|结语|总结|尾声|背景|附录?|补充|案例|结论)[：:](.+)$", t)
            if mm:
                kick, t = mm.group(1), mm.group(2).strip()
            mm = re.match(r"^(.+?)[：:—–]+\s*(.+)$", t)
            if mm and len(t) > 12:
                t, sub = mm.group(1).strip(), mm.group(2).strip()
            sec = {"title": t, "kicker": kick, "sub": sub, "units": []}
            doc["sections"].append(sec)
            unit = None
            continue
        if sec is None and (b["t"] == "h" or b["t"] not in ("para", "quote")):
            sec = {"title": doc["title"], "kicker": "", "sub": "", "units": [], "implicit": True}  # 没有 ## 的文档
            doc["sections"].append(sec)
        if sec is None:  # 封面下面的导语、日期
            if b["t"] in ("para", "quote"):
                for part in re.split(r"\s{2,}|(?<=[^\d])\s(?=\S{1,6}[：:])", unbold(b["text"])):
                    part = part.strip()
                    if DATE.search(part):
                        doc["meta"].append(re.sub(r"^(日期|时间)[：:]\s*", "", part))
                    elif len(part) <= 60 and len(doc["subtitle"]) < 2 and not re.match(r"^(场景|受众|对象)[：:]", part):
                        doc["subtitle"].append(part)
            continue
        if b["t"] == "h" and b["level"] == 3:  # 「（一）」「1.1」这类小节编号不上屏
            unit = {"title": re.sub(r"^\s*([（(][一二三四五六七八九十]+[）)]|\d{1,2}(\.\d{1,2})+(?=\s|[\u4e00-\u9fff])"
                                    r"(?!\s*[%％倍万亿千元个分吨])|[一二三四五六七八九十]+[、.])\s*", "",
                                    unbold(b["text"])), "blocks": []}  # 「2.5 倍增长」这种数字开头的不动
            sec["units"].append(unit)
            continue
        if unit is None:
            unit = {"title": sec["title"], "blocks": [], "intro": True}
            sec["units"].append(unit)
        unit["blocks"].append(b)
    return doc


# ---------- 内容形态 → 版式 ----------
def split_item(s):
    m = TITLED.match(s)
    if m:
        if m.group(1) or m.group(2):
            return unbold(m.group(1) or m.group(2)), unbold(m.group(3) or "")
        return unbold(m.group(4)).rstrip("：:"), unbold(m.group(5))
    return "", unbold(s)


def guess_icon(text):
    for name, words in ICON_WORDS:
        if any(w in text for w in words.split()):
            return name
    return None


def num_of(s):
    m = NUM.search(s)
    if not m:
        return None
    return m.group(1), m.group(2) or ""


def to_float(s):
    try:
        return float(re.sub(r"[,%％\s]", "", s))
    except ValueError:
        return None


def list_body(b):
    raw = b["items"]
    pairs = [split_item(x) for x in raw]
    n = len(raw)
    if n >= 2 and sum(bool(TIME.match(unbold(x))) for x in raw) >= n * 0.7 and n <= 6:
        items = []
        for x, (bt, bd) in zip(raw, pairs):
            if bt and TIME.match(bt):  # 「**第一天上午**：……」整个加粗部分都是时间
                time, rest = bt, bd
            else:
                xx = unbold(x)
                m = TIME.match(xx)
                time = m.group(0).strip().rstrip(".:/-") if m else ""
                rest = xx[m.end():].lstrip("：:—-– ").strip() if m else xx
            t, d = split_item(rest)
            if not t:
                head, _, tail = rest.partition("，")
                t, d = (head, tail) if tail and len(head) <= 14 else (rest, "")
            items.append({"time": time, "title": t, "text": d})
        return {"type": "timeline", "items": items}, "列表每项以时间/阶段开头 → 时间线"
    if not b["ordered"] and n <= 4 and all(num_of(unbold(x)) for x in raw) and all(len(unbold(x)) <= 40 for x in raw):
        items = []
        for (t, d), x in zip(pairs, raw):
            plain = unbold(x)
            bolds = re.findall(r"\*\*(.+?)\*\*", x)
            mb = next((NUM.search(b) for b in bolds if NUM.search(b)), None)
            m = NUM.search(plain, plain.find(mb.group(0))) if mb and plain.find(mb.group(0)) >= 0 else NUM.search(plain)
            v, u = m.group(1), m.group(2) or ""
            before = plain[:m.start()].strip(" ：:，,")
            after = plain[m.end():].strip(" ：:，,。")
            label = t or before or after
            text = d if t and v not in d else (after if before else "")
            items.append({"value": v, "unit": u, "title": label[:18], "text": text})
        return {"type": "stats", "items": items}, "每项都有关键数字 → 大数字"
    if b["ordered"] and 2 <= n <= 6:
        steps = [{"title": t or d[:14], "text": d if t else ""} for t, d in pairs]
        return {"type": "process", "steps": steps}, "有序列表 → 流程"
    titled = sum(bool(t) for t, _ in pairs)
    if 2 <= n <= 6 and titled >= n * 0.7:
        items = [{"title": t, "text": d} for t, d in pairs]
        icons = [guess_icon(t + d) for t, d in pairs]
        if sum(bool(i) for i in icons) >= n * 0.6:
            for it, ic in zip(items, icons):
                it["icon"] = ic or "circle-check"
        return {"type": "cards", "items": items}, "「小标题：说明」列表 → 卡片"
    items = [{"title": t, "text": d} if t else d for t, d in pairs]
    return {"type": "bullets", "items": items}, "普通列表 → 要点"


def table_body(b):
    header, rows = b["header"], [r + [""] * (len(b["header"]) - len(r)) for r in b["rows"]]
    numeric = []
    for c in range(1, len(header)):
        vals = [to_float(r[c]) for r in rows]
        if rows and all(v is not None for v in vals):
            numeric.append(c)
    if numeric and 2 <= len(rows) <= 12 and len(numeric) <= 4:
        cats = [r[0] for r in rows]
        series = [{"name": header[c], "values": [to_float(r[c]) for r in rows]} for c in numeric]
        pct = any("%" in r[c] or "％" in r[c] for r in rows for c in numeric)
        timey = sum(bool(TIME.match(x)) for x in cats) >= len(cats) * 0.7
        share = len(numeric) == 1 and (re.search(r"占比|比例|份额|构成|分布", "".join(header)) or
                                       (pct and 95 <= sum(series[0]["values"]) <= 105)) and len(rows) <= 6
        if share:
            kind = "doughnut"
        elif timey:
            kind = "line" if len(rows) >= 6 else "column"
        elif max(len(x) for x in cats) > 6 or len(rows) > 7:
            kind = "bar"
        else:
            kind = "column"
        decimals = any(isinstance(v, float) and v != int(v) for s in series for v in s["values"])
        fmt = '0.0"%"' if pct and decimals else ('0"%"' if pct else ("#,##0.0" if decimals else "#,##0"))
        if kind == "doughnut":
            fmt = '0"%"' if pct else "General"
        body = {"type": "chart", "kind": kind, "categories": cats, "series": series, "format": fmt}
        tops = [max(abs(v) for v in s_["values"]) or 1 for s_ in series]
        if len(series) == 2 and max(tops) / min(tops) > 8:  # 量级差太多，画在一张图里小的那列看不见
            mk = lambda s_: {"type": "chart", "kind": kind, "categories": cats, "series": [s_],  # noqa: E731
                             "format": fmt, "title": s_["name"]}
            return {"type": "split", "left": mk(series[0]), "right": mk(series[1])}, "两列数字量级差太多 → 两张图并排"
        return body, f"表格有数字列 → {kind} 图表"
    if len(rows) > 8:  # 长表格分页，每页重复表头
        return [({"type": "table", "header": header, "rows": rows[k:k + 8]}, "长表格 → 分页表格")
                for k in range(0, len(rows), 8)]
    return {"type": "table", "header": header, "rows": rows}, "表格没有数字列 → 表格"


def is_bold(b):
    return b["t"] == "para" and bool(re.fullmatch(r"\s*(\*\*.+\*\*|__.+__)\s*", b.get("raw", "")))


def chunks_of(blocks):
    """把一个单元切成若干「铺垫段落 → 主体（列表/表格/引用/图） → 紧跟的加粗结论」"""
    out, cur = [], {"pre": [], "major": None, "post": []}
    for b in blocks:
        if b["t"] in ("list", "table", "quote", "image"):
            if cur["major"] is not None:
                out.append(cur)
                cur = {"pre": [], "major": None, "post": []}
            cur["major"] = b
        elif b["t"] in ("para", "h"):
            if cur["major"] is not None and is_bold(b) and not cur["post"] or \
                    cur["major"] is not None and cur["post"] and is_bold(b) and len(cur["post"]) < 2:
                cur["post"].append(b)
            elif cur["major"] is not None:
                out.append(cur)
                cur = {"pre": [b], "major": None, "post": []}
            else:
                cur["pre"].append(b)
    if cur["major"] is not None or cur["pre"]:
        out.append(cur)
    return out


def table_cards(b):
    """没有数字、说明很长的表格 → 卡片（太长就分页）"""
    header, rows = b["header"], b["rows"]
    if len(header) < 2 or not 2 <= len(rows) <= 8:
        return None
    last = [r[-1] if r else "" for r in rows]
    if sum(len(x) for x in last) / len(rows) < 22:
        return None
    items = []
    for r in rows:
        t = unbold(r[0])
        tag = unbold(r[1]) if len(r) > 2 and len(unbold(r[1])) <= 8 else ""
        items.append({"title": f"{t} · {tag}" if tag else t, "text": unbold(r[-1])})
    avg = sum(len(i["text"]) for i in items) / len(items)
    per = 4 if avg <= 50 else (3 if avg <= 90 else 2)
    pages = [items[i:i + per] for i in range(0, len(items), per)]
    return [({"type": "cards", "items": p}, f"长文字表格 → 卡片（每页 {per} 张）") for p in pages]


def compare_of(blocks):
    """两段列表、各自前面有一个短标签（过去/现在、传统/我们）→ 对比"""
    for i in range(len(blocks) - 3):
        a, la, b, lb = blocks[i:i + 4]
        if a["t"] == "para" and la["t"] == "list" and b["t"] == "para" and lb["t"] == "list" and \
                len(unbold(a["text"])) <= 14 and len(unbold(b["text"])) <= 14:
            return i, {"type": "compare", "left": {"title": unbold(a["text"]).rstrip("：:"),
                                                   "items": [unbold(x) for x in la["items"]]},
                       "right": {"title": unbold(b["text"]).rstrip("：:"), "items": [unbold(x) for x in lb["items"]]}}
    return None


def block_text(b):
    """一个块的原文（进演讲者备注）"""
    if b["t"] in ("para", "h", "quote"):
        return unbold(b["text"])
    if b["t"] == "list":
        return "\n".join(f"{k + 1}. {unbold(x)}" if b["ordered"] else f"· {unbold(x)}" for k, x in enumerate(b["items"]))
    if b["t"] == "table":
        return "\n".join("｜".join(unbold(c) for c in r) for r in [b["header"]] + b["rows"])
    return ""


def unit_slides(unit):
    """一个内容单元 → 一页或多页，返回 [(body, lead, conclusion, why, notes)]"""
    out = []
    cmp = compare_of(unit["blocks"])
    if cmp:
        i, body = cmp
        blocks = unit["blocks"]
        pre = [unbold(b["text"]) for b in blocks[:i] if b["t"] == "para"]
        nxt = blocks[i + 4] if len(blocks) > i + 4 else None
        rest = blocks[i + 4:]
        if nxt is not None and nxt["t"] == "para" and len(unbold(nxt["text"])) <= 50:  # 紧跟的一句短话当结论
            body["verdict"] = unbold(nxt["text"])
            rest = blocks[i + 5:]
        out.append((body, pre[-1] if pre and len(pre[-1]) <= 60 else None, None, "两组带标签的列表 → 对比",
                    "\n".join(pre + ([body["verdict"]] if body.get("verdict") else []))))
        unit = {**unit, "blocks": rest}
    for ch in chunks_of(unit["blocks"]):
        pre = [b for b in ch["pre"] if b["t"] == "para"]
        parts = ch["pre"] + ([ch["major"]] if ch["major"] else []) + ch["post"]
        notes = "\n".join(block_text(b) for b in parts if block_text(b))  # 这一页对应的完整原文
        conclusion = unbold(ch["post"][0]["text"]) if ch["post"] else None
        if len(ch["post"]) > 1:
            conclusion += " " + unbold(ch["post"][1]["text"])
        m = ch["major"]
        if m is None:
            txt = [unbold(b["text"]) for b in pre]
            bold = [unbold(b["text"]) for b in pre if is_bold(b)]
            if not txt:
                continue
            if bold and sum(len(t) for t in txt) <= 160:
                rest = [t for t in txt if t not in bold]
                out.append(({"type": "statement", "text": bold[0], "sub": "\n".join(rest)}, None, None,
                            "段落里有加粗金句 → 观点页", notes))
            elif sum(len(t) for t in txt) <= 70 and len(txt) <= 2:
                out.append(({"type": "statement", "text": txt[0], "sub": txt[1] if len(txt) > 1 else ""}, None,
                            None, "只有一两句话 → 观点页", notes))
            else:
                for k in range(0, len(txt), 4):
                    out.append(({"type": "text", "paras": txt[k:k + 4]}, None, None, "纯段落 → 正文页（建议精简）",
                                notes))
            continue
        cand = [b for b in pre if len(b["text"]) <= 64]
        lead_b = next((b for b in reversed(cand) if is_bold(b)), cand[-1] if cand else None)
        lead_txt = unbold(lead_b["text"]).rstrip("：:") if lead_b else None
        if m["t"] == "list":
            bodies = [list_body(m)]
            if bodies[0][0]["type"] == "stats" and conclusion:
                bodies[0][0]["note"], conclusion = conclusion, None
        elif m["t"] == "table":
            tb = table_body(m)
            bodies = table_cards(m) or (tb if isinstance(tb, list) else [tb])
        elif m["t"] == "quote":
            bodies = [({"type": "quote", "text": unbold(m["text"]).strip("“”\"「」『』")}, "引用 → 金句页")]  # 版式自带引号
        else:
            bodies = [({"type": "image", "path": m["path"], "title": unit["title"],
                        "text": "\n".join(unbold(b["text"]) for b in pre)[:200]}, "图片 → 图文页")]
        for k, (body, why) in enumerate(bodies):
            last = k == len(bodies) - 1
            out.append((body, lead_txt if k == 0 else None, conclusion if last else None, why,
                        notes if k == 0 else ""))
    return out


# ---------- 选模板页 ----------
def pick_pages(prof):
    roles = {}
    for s in prof["slides"]:
        roles.setdefault(s["role"], []).append(s)

    def area(s):
        return s["area"][2] * s["area"][3] if s.get("area") else 0
    content = sorted(roles.get("content", []), key=lambda s: -area(s))
    if any(s.get("tracker") for s in content):  # 有进度标签的版式：每页都用它，导航保持一致（先于面积筛选）
        content = [s for s in content if s.get("tracker")]
    if content and area(content[0]):  # 带侧栏、带样机这类窄版式不参与轮换（需要时在 deck.json 里用 from 指定）
        content = [s for s in content if area(s) >= 0.75 * area(content[0])]
    light = [s for s in content if not s["dark"]]
    dark = [s for s in content if s["dark"]]
    main = dark if len(dark) > len(light) else (light or content)  # 深色为主的模板（发布会）就用深色页
    sections = roles.get("section", [])
    if any(not s.get("agenda") for s in sections):  # 普通章节页和议程式章节页都有：只用一种，别交替
        sections = [s for s in sections if not s.get("agenda")]
    return {"cover": roles.get("cover", content[:1]), "toc": roles.get("toc", []), "section": sections,
            "content": main, "content_dark": dark, "quote": roles.get("quote", []), "ending": roles.get("ending", [])}


def plan(src_path, prof_path, out):
    name = os.path.splitext(os.path.basename(src_path))[0]
    md_path = src_path
    if not src_path.lower().endswith(MD_EXT):  # txt / docx / pdf ……先转成 md
        md_path = convert(src_path, os.path.join(os.path.dirname(os.path.abspath(prof_path)), name + ".converted.md"))
        print(f"  {os.path.basename(src_path)} 已转成 {md_path}：按它出草稿，结构认错了就改这份 md 再跑")
    md = read_text(md_path)
    prof = load_json(prof_path)
    doc = outline(parse(md), name)
    pages = pick_pages(prof)
    if not pages["content"]:
        raise SystemExit("模板里没识别出内容页，无法自动规划：先看 profile.md，手写 deck.json")
    base = os.path.dirname(os.path.abspath(out))
    slides = []
    cover = pages["cover"][0]
    sp = {"from": cover["index"], "title": doc["title"], "_why": "封面"}
    if doc["subtitle"]:
        sp["subtitle"] = doc["subtitle"][0] if len(cover["slots"].get("subtitle", [])) <= 1 else doc["subtitle"]
    if doc["meta"]:
        if cover["slots"].get("meta"):
            sp["meta"] = doc["meta"][0]
        elif len(cover["slots"].get("subtitle", [])) >= 2 and isinstance(sp.get("subtitle"), str):
            sp["subtitle"] = [sp["subtitle"], doc["meta"][0]]
    slides.append(sp)
    secs = doc["sections"]
    toc_secs = [s for s in secs if not re.match(r"^(附|附录|Appendix)", s["title"])]
    if pages["toc"] and len(toc_secs) >= 3:
        toc = pages["toc"][0]
        paras = toc.get("toc_mode") == "paragraphs"  # 一个文本框一段一个议题：条数不受形状个数限制
        cap = 8 if paras else len(toc["slots"].get("items", []))
        multi = not paras and toc["texts"] and any("\n" in t["text"] for t in toc["texts"]
                                                   if t["key"] in toc["slots"].get("items", []))
        items = [[s["title"], s["sub"] or s["kicker"]] if multi else s["title"] for s in toc_secs]
        if len(items) > cap:
            print(f"  （{len(items)} 个章节超过模板目录的 {cap} 个位置，没生成目录页：合并章节后手动加）")
        else:
            slides.append({"from": toc["index"], "items": items,
                           "_why": f"目录：{len(items)} 个章节，模板有 {cap} 个位置"})
    for si, sec in enumerate(secs):
        num = f"{si + 1:02d}"
        if pages["section"] and len(secs) >= 2 and not sec.get("implicit"):
            sx = pages["section"][si % len(pages["section"])]
            intro = next((b for u in sec["units"] if u.get("intro") for b in u["blocks"] if b["t"] == "para"), None)
            if sx.get("agenda"):  # 议程式章节页：整张议程，高亮当前这一章
                slides.append({"from": sx["index"], "items": [x["title"] for x in toc_secs],
                               "current": toc_secs.index(sec) if sec in toc_secs else None,
                               "_why": "章节页（模板用高亮当前议题的议程页做章节分隔）"})
            else:
                s = {"from": sx["index"], "number": num, "title": sec["title"], "_why": "章节页"}
                sub = sec["sub"] or sec["kicker"] or (unbold(intro["text"]) if intro and len(intro["text"]) <= 40
                                                      else "")
                if sub:
                    s["subtitle"] = sub
                slides.append(s)
        for unit in sec["units"]:
            for k, (body, lead, conclusion, why, notes) in enumerate(unit_slides(unit)):
                pool = pages["content_dark"] if body["type"] in ("quote", "statement") and pages["content_dark"] \
                    else pages["content"]
                tp = pool[(len(slides)) % len(pool)] if body["type"] not in ("chart", "table", "cards") else pool[0]
                if body["type"] == "quote" and pages["quote"]:  # 模板自带金句页：直接用它
                    q = pages["quote"][len(slides) % len(pages["quote"])]
                    # 署名在最后一个破折号后面，而且要短（「增长——不是目标」里的破折号是正文）
                    mm = re.match(r"^(.+?)\s*(——|—|--)\s*([^，。,.!！?？—-]{1,20})$", body["text"])
                    if not (mm and q["slots"].get("subtitle")):
                        mm = None  # 模板没有署名位：整句放标题，不丢字
                    s = {"from": q["index"], "title": mm.group(1).strip() if mm else body["text"],
                         "_why": "引用 → 模板的金句页"}
                    if mm:
                        s["subtitle"] = "—— " + mm.group(3)
                    if notes:
                        s["notes"] = notes
                    slides.append(s)
                    continue
                s = {"from": tp["index"], "title": unit["title"], "body": body, "_why": why}
                if tp.get("tracker"):  # 进度标签：写章节名，高亮当前章
                    s["tracker"] = {"items": [x["title"] for x in toc_secs],
                                    "current": toc_secs.index(sec) if sec in toc_secs else None} \
                        if len(toc_secs) >= 2 and not sec.get("implicit") else None
                if tp["slots"].get("number"):
                    s["number"] = num
                if body["type"] == "quote":  # 金句通常是一章的收尾：页面标题用章节名
                    s["title"] = sec["title"]
                if lead:
                    s["lead"] = lead
                if conclusion:
                    s["conclusion"] = conclusion
                if notes:
                    s["notes"] = notes
                if body["type"] == "image" and not os.path.isabs(body["path"]):
                    body["path"] = os.path.relpath(os.path.join(os.path.dirname(os.path.abspath(md_path)),
                                                                body["path"]), base)
                slides.append(s)
    trk = next((s.get("tracker") for s in slides if s.get("tracker")), None)
    tp_trk = next((p.get("tracker") for p in pages["content"] if p.get("tracker")), None)
    if trk and tp_trk:
        cell = next((t for p in pages["content"] for t in p["texts"] if t["key"] == tp_trk["items"][0]), None)
        cap = int((cell["box"][2] - 0.2) * 72 / max(6, cell["size"])) if cell else 6
        long = [x for x in trk["items"] if len(x) > cap]
        if long:
            print(f"  （进度标签一格约放 {cap} 个字，这些章节名太长会被缩小：{long}。在 deck.json 的 tracker.items 里换成短名）")
    if pages["ending"]:
        slides.append({"from": pages["ending"][0]["index"], "_why": "结尾页（保留模板原文；要改就写 title）"})
    deck = {"template": os.path.relpath(profile_template(prof, prof_path), base), "profile": os.path.relpath(prof_path, base),
            "output": "out/deck.pptx", "slides": slides}
    save_json(out, deck)
    print(f"草稿 {out}：{len(slides)} 页")
    for i, s in enumerate(slides):
        t = s.get("title") or ("目录" if "items" in s else ("（无标题）" if "title" in s else "（模板原文）"))
        print(f"  {i + 1:>2}. [模板第 {s['from']} 页] {t[:22]:<22} {s.get('_why', '')}")
    return deck


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("md", help="内容文件：md，或 txt / docx / pdf 等（自动转成 md）")
    ap.add_argument("profile")
    ap.add_argument("--out", default="deck.json")
    a = ap.parse_args()
    plan(a.md, a.profile, a.out)


if __name__ == "__main__":
    main()
