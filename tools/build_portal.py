#!/usr/bin/env python3
"""生成创作知识总览门户(纯知识口径:无平台名、无逆向字样、无协议细节)。

只读本仓库内的 markdown(shared/ 与各技能 references/),统一清洗后汇编为
单文件 HTML:docs/knowledge/index.html。用法: python3 tools/build_portal.py
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOW = ROOT / "docs" / "knowledge"
OUT = KNOW / "index.html"

SHARED = ROOT / "shared"
SKILLS = ROOT / "skills"
DRAMA = SKILLS / "xiaoma-short-drama" / "references"
DIRECTOR = SKILLS / "xiaoma-director"
STUDIO = SKILLS / "xiaoma-studio" / "references"
EDITOR = SKILLS / "xiaoma-editor" / "references"
DESIGNER = SKILLS / "xiaoma-designer" / "references"
OPUS3D = SKILLS / "xiaoma-opus3d" / "references"
PPT = SKILLS / "xiaoma-ppt" / "references"

DIRECTOR_GENRES = [
    ("tvc", "TVC 广告"), ("brand-film", "品牌形象宣传片"), ("product-promo", "产品宣传片"),
    ("creator-ad", "达人口播 / 带货种草"), ("city-tourism", "文旅 / 城市宣传片"),
    ("short-drama", "竖屏短剧"), ("micro-film", "微电影 / 剧情短片"), ("animation", "动画短片"),
    ("explainer", "知识科普 / 解说"), ("motion-graphics", "MG 动画 / 数据可视化"),
    ("tutorial", "教程 / 操作演示"), ("documentary", "纪录片 / 人物纪实"), ("mv", "MV / 音乐短片"),
    ("vlog", "Vlog"), ("trailer-pv", "预告片 / 游戏 PV"), ("opening-title", "片头 / 活动开场片"),
    ("event-recap", "发布会 / 活动纪实"),
]

# ---------------------------------------------------------------------------
# 内容清单:(分组, [(条目 id, 显示标题, 文件路径, 是否剥离链接)])
# ---------------------------------------------------------------------------
GROUPS = [
    ("总览", [
        ("overview", "知识地图与阅读路径", KNOW / "overview.md", False),
    ]),
    ("短剧创作 · 通用卡", [
        ("hooks", "开场钩子", DRAMA / "hooks.md", False),
        ("structure", "单集结构与多集连续性", DRAMA / "structure.md", False),
        ("series-arc", "全剧结构:情绪契约、单元链、付费点", DRAMA / "series-arc.md", False),
        ("ledger", "跨集台账", DRAMA / "continuity-ledger.md", False),
        ("shot-language", "镜头语言", DRAMA / "shot-language.md", False),
        ("editing-rhythm", "剪辑节奏", DRAMA / "editing-rhythm.md", False),
        ("director-lenses", "大导演思维工具箱", DRAMA / "director-lenses.md", False),
        ("dialogue", "短剧台词", DRAMA / "dialogue.md", False),
        ("sound", "声音", DRAMA / "sound.md", False),
        ("ai-production", "AI 短剧制作手法", DRAMA / "ai-production.md", False),
        ("rubric", "评分标准与三评委", DRAMA / "scoring-rubric.md", False),
    ]),
    ("短剧创作 · 片种卡", [
        ("g-suspense", "悬疑刑侦", DRAMA / "genres" / "suspense.md", False),
        ("g-underdog", "爽文逆袭", DRAMA / "genres" / "underdog-payoff.md", False),
        ("g-timetravel", "穿越重生", DRAMA / "genres" / "time-travel-rebirth.md", False),
        ("g-sweet", "甜宠霸总", DRAMA / "genres" / "sweet-romance.md", False),
        ("g-revenge", "复仇虐恋", DRAMA / "genres" / "revenge-angst.md", False),
        ("g-darkfantasy", "奇幻西幻", DRAMA / "genres" / "dark-fantasy.md", False),
        ("g-guofeng", "古风志怪", DRAMA / "genres" / "guofeng-supernatural.md", False),
        ("g-family", "都市家庭", DRAMA / "genres" / "family-drama.md", False),
    ]),
    ("编导分镜 · 17 片种卡", [
        (f"dg-{gid}", title, DIRECTOR / "genres" / f"{gid}.md", False) for gid, title in DIRECTOR_GENRES
    ]),
    ("编导与分镜", [
        ("d-shot", "镜头语言速查", DIRECTOR / "references" / "shot-language.md", False),
        ("d-frame", "分镜图提示词", DIRECTOR / "references" / "frame-prompts.md", False),
        ("d-review", "导演审片标准", DIRECTOR / "references" / "director-review.md", False),
        ("d-checklist", "交付前自检清单", DIRECTOR / "references" / "review-checklist.md", False),
        ("d-route", "视频制作路线:按片种筛选", DIRECTOR / "references" / "video-pipeline.md", False),
        ("bench", "拉片节奏基准", DIRECTOR / "references" / "benchmarks.md", True),
    ]),
    ("代码动效视频(30 条高赞样本)", [
        ("s-research", "研究底稿:30 条样本表", STUDIO / "research.md", True),
        ("s-aesthetics", "审美规则", STUDIO / "aesthetics.md", False),
        ("s-artdir", "配图与视频的审美逻辑", STUDIO / "art-direction.md", False),
        ("s-motion", "动效语法", STUDIO / "motion.md", False),
        ("s-storyboard", "分镜与节奏", STUDIO / "storyboard.md", False),
        ("s-audio", "声音:配乐、音效、旁白", STUDIO / "audio.md", False),
        ("s-aiassets", "搭配生成模型出素材", STUDIO / "ai-assets.md", False),
        ("s-prompts", "可直接抄的提示词", STUDIO / "prompts.md", False),
        ("s-slides", "HTML 幻灯片", STUDIO / "slides.md", False),
        ("s-web", "网页:官网、落地页、展厅大屏", STUDIO / "web.md", False),
    ]),
    ("剪辑与成片", [
        ("e-cut", "剪辑节奏:入出点、内部切镜、闪帧", EDITOR / "cut-rhythm.md", False),
        ("e-sound", "声音三层:底噪、音效、BGM", EDITOR / "sound.md", False),
        ("e-cards", "字幕与字卡", EDITOR / "cards.md", False),
        ("e-qa", "成片体检:查什么、门槛、怎么修", EDITOR / "qa-report.md", False),
    ]),
    ("复刻与产线", [
        ("clone", "复刻与变体方法论", SHARED / "clone-method.md", False),
        ("viral", "爆款拆解与带货测试", SHARED / "viral-breakdown.md", False),
        ("pipeline", "AI 视频产线工作流", SHARED / "production-pipeline.md", False),
        ("runtime", "运行时纪律:成本、长任务、素材边界", SHARED / "runtime-rules.md", False),
    ]),
    ("写作与内容方法论", [
        ("w-writing", "写作指南(原子洞察/So What/情绪形状)", SHARED / "writing-guide.md", False),
        ("w-frameworks", "六大文章框架", SHARED / "frameworks.md", False),
        ("w-topic", "选题五维评分", SHARED / "topic-selection.md", False),
        ("w-deai", "去 AI 味四级流程", SHARED / "de-ai-protocol.md", False),
        ("w-visual", "视觉提示词五要素", SHARED / "visual-prompts.md", False),
        ("w-videoprompt", "视频提示词(3×3 时间结构/四维控制)", SHARED / "video-prompt-guide.md", False),
        ("w-character", "人物设计逻辑", SHARED / "character-design.md", False),
        ("w-library", "提示词库(按用途重组)", SHARED / "prompt-library.md", True),
        ("w-dna-wechat", "平台 DNA:公众号", SHARED / "platform-dna" / "wechat.md", False),
        ("w-dna-x", "平台 DNA:海外短帖", SHARED / "platform-dna" / "x.md", False),
        ("w-dna-xhs", "平台 DNA:图文社区", SHARED / "platform-dna" / "xhs.md", False),
    ]),
    ("设计 · 3D · PPT", [
        ("v-strategy", "海报/KV 策略层", DESIGNER / "strategy.md", False),
        ("v-rules", "规范层:五元素决策表", DESIGNER / "design-rules.md", False),
        ("v-style", "表现层:风格词典", DESIGNER / "style-dictionary.md", False),
        ("v-rubric", "设计评审:三层评分", DESIGNER / "review-rubric.md", False),
        ("v-ui", "UI 设计参考", SHARED / "ui-design.md", False),
        ("v-3d-camera", "3D 镜头语法", OPUS3D / "camera-grammar.md", False),
        ("v-3d-pitfalls", "3D 场景踩坑记录", OPUS3D / "pitfalls.md", False),
        ("v-ppt-aes", "PPT 审美标准", PPT / "aesthetics.md", False),
        ("v-ppt-match", "PPT 内容怎么匹配模板", PPT / "matching.md", False),
    ]),
]

# ---------------------------------------------------------------------------
# 清洗规则:纯知识口径(顺序敏感:长词在前)
# ---------------------------------------------------------------------------
TEXT_RULES = [
    # 组合词先处理
    (r"即梦系半写实\s*3D", "半写实 3D 漫剧"),
    (r"即梦系", "半写实 3D 漫剧系"),
    (r"即梦", "AI 漫剧工具"),
    (r"小云雀", "AI 短剧工作台"),
    (r"Seedance", "文生视频模型"),
    (r"Seedream", "图像模型"),
    (r"Nano Banana", "图像模型"),
    (r"Kling", "视频模型"),
    (r"豆包", "中文配音模型"),
    (r"剪映", "剪辑工具"),
    (r"[Ll]ib[TV]V?", "AI 视频工具"),
    (r"斗罗风?\s*CG", "国漫 CG"),
    (r"斗罗", "国漫"),
    (r"皮克斯萌系", "欧美萌系"),
    (r"皮克斯", "欧美动画"),
    # 平台名 → 泛称
    (r"全抖音", "全网"),
    (r"均来自抖音", "均采集自公开短视频平台"),
    (r"来自抖音", "采集自公开短视频平台"),
    (r"抖音", "短视频平台"),
    (r"红果", "短剧平台"),
    (r"B\s*站", "视频平台"),
    (r"快手", "短视频平台"),
    (r"小红书", "图文社区"),
    (r"知乎", "问答社区"),
    (r"TikTok", "海外短视频平台"),
    (r"YouTube", "视频平台"),
    (r"Instagram", "图片社区"),
    # 逆向/协议字样
    (r"逆向工程", "技术分析"),
    (r"逆向", "还原分析"),
    (r"去 AI 味协议", "去 AI 味四级流程"),
    (r"四级协议", "四级流程"),
    (r"de-ai-protocol", "de-ai 流程"),
    # 提示词库:按模型分组 → 按用途
    (r"## Claude Fable 5", "## 代码生成:网页复刻与落地页"),
    (r"## Claude Opus 5\.5(（代码动画/网页）)?", "## 代码生成:动画与网页动效"),
    (r"## Gemini 3 Pro", "## 代码生成:高端网页设计"),
    (r"## GPT 6 Astra", "## 代码生成:3D 游戏与互动"),
    (r"## GPT Image 1\.5", "## 图像生成:风格化变形(基础)"),
    (r"## GPT Image 2(?!\.5)", "## 图像生成:海报与编辑排版"),
    (r"## GPT Image 2\.5", "## 图像生成:风格化变形(进阶)"),
    (r"## Grok Imagine", "## 视频生成:变形与奇观"),
    (r"## Seedance 2\.0", "## 视频生成:动画战斗(短镜)"),
    (r"## Seedance 2\.5", "## 视频生成:写实叙事"),
    # 提示词库正文里的产品名 → 角色泛称
    (r"Claude Code", "the coding agent"),
    (r"（Claude不读出来，画面里也没有Claude英文）", "（角色名不读出来，画面里也没有角色名英文）"),
    (r"由 Claude 写代码渲染完成", "由代码渲染完成"),
    (r"Claude", "the agent"),
    (r"Claude角色", "管家机器人角色"),
    (r"Claude场景", "管家机器人场景"),
    (r"Claude手里", "管家机器人手里"),
    (r"Claude表情", "管家机器人表情"),
    (r"变成了Claude", "变成了管家机器人"),
    (r"类似Claude的", "类似管家机器人的"),
    (r"音库里的Claude声音", "音库里的管家音色"),
    (r"Claude Motion: Opus 5\.5 Animated Story Prompt", "Animated Story Prompt (code-render)"),
    (r"Opus 5\.5", "the render model"),
    (r"Opus", "the render model"),
    (r"GPT-6", "the code model"),
    (r"GPT 6", "the code model"),
    (r"GPT角色", "向导机器人角色"),
    (r"GPT场景", "向导机器人场景"),
    (r"音库里的GPT声音", "音库里的向导音色"),
    (r"ChatGPT", "the chatbot"),
    (r"Gemini", "the design model"),
    (r"Grok", "the video model"),
    (r"Astra", "the code model"),
    (r"Tripo", "a 3D modeling tool"),
    (r"Remotion", "the code-render framework"),
    (r"remotion", "code-render"),
    (r"EdgeSpeak", "the TTS tool"),
    (r"Qwen3-TTS 1\.7B Base", "a local TTS model"),
    (r"mlx[_-]whisper large-v3-turbo", "本地转写"),
    (r"mlx[_-]whisper", "本地转写"),
    (r"[Ww]hisper", "本地转写"),
    (r"opus5\.5", "code-render"),
    (r"Opus5\.5", "Code-render"),
    (r"opus家族史", "代码动画家族史"),
    (r"vibe知识大赏", "知识动画大赏"),
    (r"opus ?5\.5", "代码动画"),
    # 新增来源(代码动效/片场/导演)里的残留名
    (r"GPT Image\s*[\d.]*(\s*/\s*[\d.]+)?", "图像模型"),
    (r"GPT把", "向导机器人把"),
    (r"Lyria\s*\d*", "配乐模型"),
    (r"Higgsfield MCP", "AI 视频工具"),
    (r"Higgsfield", "AI 视频工具"),
    (r"可灵", "视频模型"),
    (r"Just One API", "数据接口"),
    (r"Twitter", "海外社交平台"),
    (r"（X / ", "（海外社交平台 / "),
]

LINK_STRIP_DOMAINS = ("douyin.com", "bilibili.com", "youtube.com", "youtu.be",
                      "x.com", "twitter.com", "tiktok.com", "xiaohongshu.com",
                      "vericast.com", "wersm.com", "adweek.com", "wikipedia.org",
                      "philpot.education", "diggitmagazine.com", "studioBinder",
                      "nofilmschool", "artofthetitle")


def strip_links(text: str) -> str:
    """剥离指向外部站点的链接,保留文字。"""
    def _md_link(m: "re.Match") -> str:
        url = m.group(2).lower()
        return m.group(1) if not any(d in url for d in LINK_STRIP_DOMAINS) else m.group(1)

    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", _md_link, text)
    # 行尾裸链接(常见于参考列表)
    text = re.sub(r"\s*[—-]?\s*https?://\S+", "", text)
    # byline 里的来源标注
    text = re.sub(r"·\s*\[source\]\([^)]*\)", "", text)
    return text


def clean_text(text: str) -> str:
    for pat, repl in TEXT_RULES:
        text = re.sub(pat, repl, text)
    return text


# ---------------------------------------------------------------------------
# 轻量 markdown → HTML
# ---------------------------------------------------------------------------
def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = text.replace("&lt;br&gt;", "<br>")
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    return text


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i, n = 0, len(lines)
    list_stack: list[str] = []  # "ul" | "ol"

    def close_lists() -> None:
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    while i < n:
        line = lines[i]

        if line.strip().startswith("```"):
            close_lists()
            code_lines: list[str] = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_lists()
            level = min(len(m.group(1)) + 1, 6)  # h2 起排(文档 h1 并入页内层级)
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        if re.match(r"^\s*([-*+]|\d+\.)\s+", line):
            m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)
            indent, marker, body = m.group(1), m.group(2), m.group(3)
            tag = "ol" if marker[0].isdigit() else "ul"
            if not list_stack:
                out.append(f"<{tag}>")
                list_stack.append(tag)
            elif list_stack[-1] != tag and not indent:
                out.append(f"</{list_stack.pop()}>")
                out.append(f"<{tag}>")
                list_stack.append(tag)
            elif indent and len(list_stack) == 1:
                out.append(f"<{tag}>")
                list_stack.append(tag)
            out.append(f"<li>{inline(body)}</li>")
            i += 1
            continue

        if list_stack and not line.strip():
            close_lists()
            i += 1
            continue

        if line.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            close_lists()
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows: list[list[str]] = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<div class='tbl-wrap'><table><thead><tr>")
            out.extend(f"<th>{inline(c)}</th>" for c in header)
            out.append("</tr></thead><tbody>")
            for row in rows:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            out.append("</tbody></table></div>")
            continue

        if line.strip().startswith(">"):
            close_lists()
            quote_lines = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>" + inline(" ".join(quote_lines)) + "</blockquote>")
            continue

        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", line):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        if not line.strip():
            close_lists()
            i += 1
            continue

        close_lists()
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6}\s|```|\s*[-*+]\s|\s*\d+\.\s|\||>|\s*-{3,}\s*$)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")

    close_lists()
    return "\n".join(out)


def load_entry(path: Path, strip: bool) -> str:
    if not path.is_file():
        return f"<p class='missing'>缺文件:{html.escape(str(path))}</p>"
    text = path.read_text(encoding="utf-8")
    if strip:
        text = strip_links(text)
    text = clean_text(text)
    return md_to_html(text)


CSS = """
:root{--ink:#1f2430;--muted:#6b7280;--line:#e5e7eb;--accent:#b45309;--bg:#faf9f6;--side:#14161c;--side-ink:#c9ced9}
*{box-sizing:border-box}
body{margin:0;font-family:"Songti SC","Noto Serif CJK SC",Georgia,serif;color:var(--ink);background:var(--bg);line-height:1.75;font-size:16px}
.layout{display:grid;grid-template-columns:280px minmax(0,1fr);min-height:100vh}
aside{background:var(--side);color:var(--side-ink);padding:24px 0 48px;position:sticky;top:0;height:100vh;overflow-y:auto}
aside .brand{padding:0 20px 16px;border-bottom:1px solid #262a35;margin-bottom:12px}
aside .brand b{color:#fff;font-size:17px;letter-spacing:.5px}
aside .brand span{display:block;font-size:12px;color:#7c8494;margin-top:4px}
aside h3{font-size:12px;letter-spacing:2px;color:#8b93a5;padding:14px 20px 6px;margin:0;font-weight:600}
aside a{display:block;color:var(--side-ink);text-decoration:none;font-size:13.5px;padding:5px 20px 5px 28px;border-left:2px solid transparent}
aside a:hover{color:#fff;background:#1c2029}
main{width:100%;max-width:920px;margin:0 auto;padding:48px 56px 120px;overflow-wrap:break-word}
.doc h1{font-size:30px;margin:.2em 0 .6em;letter-spacing:1px}
.doc h2{font-size:22px;margin-top:2.2em;padding-bottom:.3em;border-bottom:1px solid var(--line)}
.doc h3{font-size:18px;margin-top:1.8em}
.doc h4{font-size:16px;margin-top:1.4em;color:#374151}
.doc p{margin:.8em 0}
.doc blockquote{margin:1.2em 0;padding:.6em 1.2em;border-left:3px solid var(--accent);background:#f6efe3;color:#5b4632;font-size:15px}
.doc code{background:#eee9df;padding:1px 6px;border-radius:4px;font-size:.88em;font-family:"SF Mono",Menlo,monospace}
.doc pre{background:#14161c;color:#dbe2f0;padding:16px 20px;border-radius:10px;overflow-x:auto;line-height:1.6}
.doc pre code{background:none;padding:0;color:inherit}
.doc table{border-collapse:collapse;width:100%;font-size:14.5px;margin:1.2em 0}
.doc th,.doc td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
.doc th{background:#f1ede4;font-weight:600;white-space:nowrap}
.doc tr:nth-child(even) td{background:#fbfaf7}
.tbl-wrap{overflow-x:auto}
.doc li{margin:.35em 0}
.doc hr{border:none;border-top:1px dashed var(--line);margin:2em 0}
.doc a{color:var(--accent)}
.doc :not(pre)>code{overflow-wrap:anywhere}
.missing{color:#b91c1c;background:#fef2f2;padding:10px 14px;border:1px solid #fecaca;border-radius:8px}
.top{position:fixed;right:28px;bottom:28px;background:var(--side);color:#fff;padding:8px 14px;border-radius:999px;font-size:13px;text-decoration:none;opacity:.85}
@media print{aside{display:none}.layout{display:block}main{padding:0;max-width:none}}
@media (max-width:900px){.layout{grid-template-columns:1fr}aside{position:static;height:auto}main{padding:28px 20px}}
"""


def build() -> int:
    nav_html: list[str] = []
    body_html: list[str] = []
    total_missing = 0

    for group, entries in GROUPS:
        nav_html.append(f"<h3>{html.escape(group)}</h3>")
        for eid, title, path, strip in entries:
            exists = path.is_file()
            if not exists:
                total_missing += 1
            nav_html.append(f'<a href="#{eid}">{html.escape(title)}</a>')
            badge = "" if exists else " <span style='color:#f87171'>(缺)</span>"
            body_html.append(
                f'<section class="doc" id="{eid}">\n'
                f"<h1>{html.escape(title)}{badge}</h1>\n"
                + load_entry(path, strip) +
                "\n</section>\n"
            )

    doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>创作知识总览 · 纯知识版</title>
<style>{CSS}</style>
</head>
<body>
<div class="layout">
<aside>
  <div class="brand"><b>创作知识总览</b><span>纯知识版 · 已去平台名/技术字样</span></div>
  {''.join(nav_html)}
</aside>
<main>
{''.join(body_html)}
</main>
</div>
<a class="top" href="#">回顶部 ↑</a>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    size_kb = OUT.stat().st_size // 1024
    print(f"OK 写出 {OUT} ({size_kb} KB, {len(GROUPS)} 组,缺失 {total_missing} 个文件)")
    return 0 if total_missing == 0 else 1


if __name__ == "__main__":
    sys.exit(build())
