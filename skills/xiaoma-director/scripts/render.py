#!/usr/bin/env python3
"""storyboard.json → 单文件 HTML 分镜表（分镜图 base64 内嵌）；--index 生成样例总览页。

用法：
  python3 render.py storyboard.json [-o storyboard.html]
  python3 render.py --index samples/ [-o samples/index.html]
"""
import argparse
import base64
import html
import sys
from pathlib import Path
from urllib.parse import quote

from sbcommon import fmt_tc, genre_name, is_num, load_storyboard, timecodes
from review import analyze
from validate import check

MIME = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}
REF_TYPES = {'character': '角色', 'product': '产品', 'location': '场景', 'prop': '道具'}
STATUS_CLASS = {'合适': 'st-ok', '偏紧': 'st-tight', '拖沓': 'st-drag', '已说明': 'st-noted'}
VERDICT_LABEL = {'APPROVE': '通过', 'APPROVE_WITH_NOTES': '有备注通过', 'REVISE': '退回修改'}
ISSUE_LABEL = {'fixed': '已修改', 'open': '待定', 'wontfix': '不改（已说明）'}

CSS = """
:root{--bg:#f6f5f2;--paper:#fff;--ink:#1d1d1f;--muted:#6b6b70;--line:#e3e1dc;--accent:#c2410c;--chip:#fff1e8}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--paper:#1d1d1f;--ink:#ececec;--muted:#9a9aa0;--line:#333;--accent:#fb923c;--chip:#3a2416}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.6 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:1680px;margin:0 auto;padding:32px 24px 64px}
header,section{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:22px 26px;margin-bottom:20px}
h1{margin:6px 0 4px;font-size:28px}
h2{font-size:18px;margin:0 0 14px}
h2 small{color:var(--muted);font-weight:400;font-size:13px;margin-left:6px}
.chip{display:inline-block;background:var(--chip);color:var(--accent);font-weight:600;font-size:12px;padding:2px 10px;border-radius:99px}
.core{color:var(--muted);margin:0 0 14px;font-size:15px}
.metas{display:flex;flex-wrap:wrap;gap:8px 28px}
.meta span{color:var(--muted);margin-right:6px;font-size:12px}
details{margin-top:12px;color:var(--muted)}
.kv div{margin:4px 0}
.kv b{display:inline-block;min-width:84px;color:var(--muted);font-weight:500}
.beats{display:flex;gap:3px;margin:16px 0 8px;height:46px}
.beat{background:var(--ink);color:var(--paper);border-radius:6px;padding:4px 8px;min-width:0;font-size:12px;display:flex;flex-direction:column;justify-content:center}
.beat:nth-child(even){background:var(--accent)}
.beat b,.beat span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.beat-list{margin:8px 0 0;padding-left:20px;color:var(--muted)}
.beat-list b{color:var(--ink)}
.refs{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.ref{margin:0}
.ref img,.ref .missing{width:100%;border-radius:8px;display:block}
.ref figcaption{margin-top:8px}
.ref p{margin:4px 0 0;color:var(--muted);font-size:13px}
.tag{font-size:11px;color:var(--accent);border:1px solid var(--accent);border-radius:4px;padding:0 5px;margin-left:6px;white-space:nowrap}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:1080px;font-size:13px}
th{position:sticky;top:0;background:var(--paper);text-align:left;font-weight:600;color:var(--muted);border-bottom:2px solid var(--ink);padding:8px;white-space:nowrap}
td{border-bottom:1px solid var(--line);padding:10px 8px;vertical-align:top}
td.no{font-size:20px;font-weight:700;color:var(--accent)}
td.tc{font-variant-numeric:tabular-nums;width:84px}
td.tc em{display:block;color:var(--accent);font-style:normal;font-weight:600}
td.tc .tr{display:block;margin-top:6px;color:var(--muted);white-space:normal;max-width:96px}
td.cam div:first-child{font-weight:600}
td.visual{min-width:180px}
td.purpose{min-width:150px}
td b{color:var(--muted);font-weight:500}
.frame{width:200px;border-radius:6px;display:block;cursor:zoom-in}
body.vertical td .frame{width:110px}
.missing{display:flex;align-items:center;justify-content:center;aspect-ratio:16/9;background:var(--line);color:var(--muted);font-size:12px;width:200px;border-radius:6px}
.st-ok{background:#a8a29e}.st-tight{background:#dc2626}.st-drag{background:#2563eb}.st-noted{background:#16a34a}
.verdict{display:inline-block;font-weight:700;font-size:14px;padding:3px 12px;border-radius:6px;color:#fff;background:#78716c;margin-bottom:8px}
.v-approve{background:#16a34a}.v-approve_with_notes{background:#ca8a04}.v-revise{background:#dc2626}
.chart{display:flex;gap:3px;height:150px;margin:16px 0 6px;align-items:stretch}
.chart .col{flex:1;min-width:6px;display:flex;flex-direction:column}
.chart .plot{position:relative;flex:1;border-bottom:1px solid var(--line)}
.chart .bar{position:absolute;bottom:0;left:0;right:0;border-radius:3px 3px 0 0}
.chart .need{position:absolute;left:-1px;right:-1px;border-top:2px dashed var(--ink);opacity:.55}
.chart span{font-size:10px;color:var(--muted);text-align:center;line-height:16px}
.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:var(--muted)}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px}
.legend i.dash{border-top:2px dashed var(--ink);height:0;border-radius:0;opacity:.55}
.pace-notes{margin:12px 0 0;padding-left:20px;color:var(--accent)}
table.issues{min-width:0;margin-top:14px}
table.issues td:nth-child(-n+2),table.issues td:last-child{white-space:nowrap}
table.issues small{color:var(--muted)}
.pace{display:inline-block;font-size:11px;color:#fff;border-radius:4px;padding:0 5px;margin-left:6px;font-style:normal;cursor:help}
#lb{position:fixed;inset:0;background:rgba(0,0,0,.86);display:flex;align-items:center;justify-content:center;z-index:9;cursor:zoom-out}
#lb[hidden]{display:none}
#lb img{max-width:94vw;max-height:94vh}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:12px;overflow:hidden;color:inherit;text-decoration:none;padding-bottom:14px}
.card:hover{border-color:var(--accent)}
.card img,.card .missing{width:100%;aspect-ratio:16/9;object-fit:contain;background:#000;display:block;border-radius:0}
.card .chip{margin:12px 14px 0}
.card h3{margin:6px 14px 2px;font-size:16px}
.card p{margin:0 14px;color:var(--muted);font-size:13px}
@media print{@page{size:A4 landscape;margin:10mm}body{background:#fff}header,section{border:none;padding:0}th{position:static}.frame{width:180px}}
@media screen and (max-width:1180px){
  table.shots{min-width:0}
  table.shots thead{display:none}
  table.shots,table.shots tbody{display:block}
  table.shots tr{display:grid;grid-template-columns:28px 220px minmax(0,1fr) minmax(0,1fr);column-gap:18px;row-gap:10px;padding:18px 0;border-bottom:1px solid var(--line)}
  body.vertical table.shots tr{grid-template-columns:28px 120px minmax(0,1fr) minmax(0,1fr)}
  table.shots td{display:block;border:none;padding:0;min-width:0}
  table.shots td.no{grid-column:1;grid-row:1/span 4}
  table.shots td.img{grid-column:2;grid-row:1/span 4}
  table.shots td.tc{width:auto}
  table.shots td.tc .tr{display:inline;margin:0 0 0 8px}
  table.shots td.tc em{display:inline;margin-left:8px}
  table.shots td.cam div{display:inline}
  table.shots td.cam div+div::before{content:" · ";color:var(--muted)}
  .frame,.missing{width:220px}
  body.vertical td .frame{width:120px}
  table.shots td:not(.no):not(.img)::before{content:attr(data-label);display:block;font-size:11px;color:var(--muted);margin-bottom:2px}
}
@media screen and (max-width:640px){
  main{padding:16px}
  table.shots tr{grid-template-columns:24px minmax(0,1fr)}
  body.vertical table.shots tr{grid-template-columns:24px minmax(0,1fr)}
  table.shots td.no{grid-row:1/span 9}
  table.shots td:not(.no){grid-column:2}
  table.shots td.img{grid-row:auto}
  .frame,.missing{width:100%}
}

.qa{font-size:12px;padding:2px 8px;border-radius:10px;white-space:nowrap}
.qa-pass{background:#1d7a46;color:#fff}.qa-repair{background:#9a6b00;color:#fff}.qa-fail{background:#a33;color:#fff}
.v-dry{color:#888;font-size:12px}.v-err{color:#a33;font-size:12px}.v-advice{color:#b8860b;font-size:11px;margin-top:4px}
"""

JS = """
const lb=document.getElementById('lb');
document.addEventListener('click',e=>{
  const t=e.target;
  if(t.tagName==='IMG'&&t.classList.contains('frame')){lb.querySelector('img').src=t.src;lb.hidden=false}
  else if(lb.contains(t)){lb.hidden=true}
});
"""


def esc(v):
    return '' if v is None else html.escape(str(v))


def embed(base_dir, rel):
    """把图片读成 data URI；路径为空、文件不存在或跑出项目目录时返回空串。"""
    if not rel:
        return ''
    base = Path(base_dir).resolve()
    p = (base / rel).resolve()
    if not p.is_relative_to(base) or not p.is_file():   # 防止 ../ 或绝对路径把别的文件嵌进 HTML
        return ''
    mime = MIME.get(p.suffix.lower(), 'application/octet-stream')
    return f'data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}'


def _img(src, alt):
    if not src:
        return '<div class="missing">未出图</div>'
    return f'<img class="frame" src="{src}" alt="{esc(alt)}" loading="lazy">'


def _lines(pairs):
    """[(标签, 文本)] → 只渲染有内容的行。"""
    return ''.join(f'<div><b>{label}</b>{esc(text)}</div>' for label, text in pairs if text)


def _head(p):
    scope = p.get('segment_note') if p.get('scope') == 'segment' else '整片'
    duration = f"{p['duration_s']:g}s" if is_num(p.get('duration_s')) else None
    meta = [('时长', duration), ('画幅', p.get('aspect')), ('平台', p.get('platform')),
            ('受众', p.get('audience')), ('范围', scope)]
    cells = ''.join(f'<div class="meta"><span>{k}</span>{esc(v)}</div>' for k, v in meta if v)
    assumptions = p.get('assumptions') or []
    notes = ''.join(f'<li>{esc(a)}</li>' for a in assumptions)
    details = f'<details><summary>假设（{len(assumptions)} 条）</summary><ul>{notes}</ul></details>' if notes else ''
    return (f'<header><div class="chip">{esc(genre_name(p.get("genre")))}</div>'
            f'<h1>{esc(p.get("title"))}</h1><p class="core">{esc(p.get("core_message"))}</p>'
            f'<div class="metas">{cells}</div>{details}</header>')


def _flex(v):
    """节拍条宽度只接受数字，原值不拼进 style 属性。"""
    return max(float(v), 0.0) if is_num(v) else 1


def _strategy(st):
    beats = st.get('beats') or []
    bar = ''.join(
        f'<div class="beat" style="flex:{_flex(b.get("duration_s"))}" title="{esc(b.get("purpose"))}">'
        f'<b>{esc(b.get("name"))}</b><span>{esc(b.get("duration_s"))}s</span></div>' for b in beats)
    items = ''.join(f'<li><b>{esc(b.get("name"))}</b>（{esc(b.get("duration_s"))}s）{esc(b.get("purpose"))}</li>'
                    for b in beats)
    rows = _lines([('一句话核心', st.get('logline')), ('视觉风格', st.get('visual_style')),
                   ('调性', st.get('tone')), ('音乐', st.get('music'))])
    return (f'<section><h2>创作策略</h2><div class="kv">{rows}</div>'
            f'<div class="beats">{bar}</div><ol class="beat-list">{items}</ol></section>')


def _refs(refs, base_dir):
    if not refs:
        return ''
    cards = ''.join(
        f'<figure class="ref">{_img(embed(base_dir, r.get("image")), r.get("name"))}'
        f'<figcaption><b>{esc(r.get("name"))}</b><span class="tag">{esc(REF_TYPES.get(r.get("type"), r.get("type")))}</span>'
        f'<p>{esc(r.get("description"))}</p></figcaption></figure>' for r in refs)
    return f'<section><h2>设定</h2><div class="refs">{cards}</div></section>'


def _pace_badge(pace):
    if not pace or pace['status'] == '合适':
        return ''
    return (f'<span class="pace {STATUS_CLASS[pace["status"]]}" title="{esc(pace["reason"])}">'
            f'{esc(pace["status"])}</span>')


QA_BADGE = {'pass': ('qa-pass', '✓ 过'), 'repair': ('qa-repair', '↻ 修'), 'fail': ('qa-fail', '✗ 重出')}


def _video_cell(shot):
    """出片格：链接 / 已备提示词 / 失败原因 + 质检徽标与修复建议。没有 video 返回 None。"""
    video = shot.get('video')
    if not video:
        return '—'
    parts = []
    url = video.get('url') or ''
    if video.get('error'):
        parts.append(f'<span class="v-err">出片失败：{esc(video["error"])}</span>')
    elif url.startswith('dry-run:'):
        parts.append('<span class="v-dry">已备提示词</span>')
    elif url:
        parts.append(f'<a href="{esc(url)}" target="_blank">▶ 片段</a>')
    qa = video.get('qa')
    if qa:
        cls, label = QA_BADGE.get(qa.get('verdict'), ('', qa.get('verdict', '')))
        parts.append(f'<span class="qa {cls}">{label} {esc(qa.get("total"))}</span>')
        if qa.get('advice'):
            parts.append(f'<div class="v-advice">{esc(qa["advice"])}</div>')
    return ''.join(parts) or '—'


def _row(shot, start, end, extra_cols, base_dir, pace=None, with_video=False):
    no = shot.get('no')
    camera = ''.join(f'<div>{esc(v)}</div>' for v in
                     [shot.get('shot_size'), shot.get('angle'), shot.get('movement'), shot.get('lens')] if v)
    sound = _lines([('台词 ', shot.get('dialogue')), ('旁白 ', shot.get('vo')), ('字幕 ', shot.get('on_screen_text')),
                    ('音效 ', shot.get('sfx')), ('音乐 ', shot.get('music'))])
    beat = f'<span class="tag">{esc(shot.get("beat"))}</span><br>' if shot.get('beat') else ''
    extra = shot.get('extra') or {}
    timing = (f'{fmt_tc(start)} – {fmt_tc(end)}<em>{esc(shot.get("duration_s"))}s</em>{_pace_badge(pace)}'
              f'<span class="tr">→ {esc(shot.get("transition"))}</span>')
    # 每格带 data-label：窄屏时表格变卡片，靠它显示字段名
    cells = [
        ('镜号', 'no', esc(no)),
        ('分镜图', 'img', _img(embed(base_dir, shot.get('frame')), f'第 {no} 镜')),
        ('时间码 / 转场', 'tc', timing),
        ('景别 · 角度 · 运镜', 'cam', camera),
        ('画面内容', 'visual', esc(shot.get('visual'))),
        ('声音 / 字幕', 'sound', sound),
        ('叙事目的', 'purpose', beat + esc(shot.get('purpose'))),
        *[(c, 'extra', esc(extra.get(c))) for c in extra_cols],
        ('备注', 'notes', esc(shot.get('notes'))),
        *( [('出片', 'video', _video_cell(shot))] if with_video else [] ),
    ]
    tds = ''.join(f'<td class="{cls}" data-label="{esc(label)}">{body}</td>' for label, cls, body in cells)
    return f'<tr>{tds}</tr>'


def _table(sb, base_dir, paces):
    shots = sb.get('shots') or []
    extra_cols = (sb.get('project') or {}).get('extra_columns') or []
    with_video = any(s.get('video') for s in shots)
    head = ['镜号', '分镜图', '时间码 / 转场', '景别 · 角度 · 运镜', '画面内容', '声音 / 字幕',
            '叙事目的', *extra_cols, '备注', *( ['出片'] if with_video else [] )]
    ths = ''.join(f'<th>{esc(h)}</th>' for h in head)
    rows = ''.join(_row(s, a, b, extra_cols, base_dir, p, with_video)
                   for s, (a, b), p in zip(shots, timecodes(shots), paces))
    return (f'<section><h2>分镜表<small>{len(shots)} 镜</small></h2><div class="scroll"><table class="shots">'
            f'<thead><tr>{ths}</tr></thead><tbody>{rows}</tbody></table></div></section>')


def _pace_chart(shots):
    """节奏曲线：柱高是时长，虚线是所需下限，颜色是判定。"""
    top = max(max(s['duration'], s['need']) for s in shots) * 1.1 or 1   # 顶部留余量，下限线不出界
    cols = ''.join(
        f'<div class="col" title="{esc(_bar_title(s))}"><div class="plot">'
        f'<div class="bar {STATUS_CLASS[s["status"]]}" style="height:{s["duration"] / top * 100:.1f}%"></div>'
        f'<i class="need" style="bottom:{s["need"] / top * 100:.1f}%"></i></div><span>{s["no"]}</span></div>'
        for s in shots)
    legend = ''.join(f'<span><i class="{c}"></i>{k}</span>' for k, c in STATUS_CLASS.items())
    return f'<div class="chart">{cols}</div><div class="legend">{legend}<span><i class="dash"></i>所需下限</span></div>'


def _bar_title(s):
    return f"第 {s['no']} 镜 {s['duration']:g}s，所需 {s['need']:g}s（{s['need_by']}）。{s['reason']}"


def _issues(review):
    rows = ''.join(
        f"<tr><td>{esc(it.get('shot') or '全片')}</td><td>{esc(it.get('severity'))}</td>"
        f"<td>{esc(it.get('symptom'))}<br><small>{esc(it.get('evidence'))}</small></td>"
        f"<td>{esc(it.get('fix'))}</td><td>{esc(ISSUE_LABEL.get(it.get('status'), it.get('status')))}</td></tr>"
        for it in review.get('issues') or [])
    if not rows:
        return ''
    return ('<table class="issues"><thead><tr><th>镜号</th><th>级别</th><th>问题</th><th>改法</th><th>状态</th>'
            f'</tr></thead><tbody>{rows}</tbody></table>')


def _review_section(sb, analysis):
    """导演审核版块：审片结论、节奏机检统计与曲线、全片提醒、审片意见。"""
    review = sb.get('review') or {}
    verdict = review.get('verdict')
    label = VERDICT_LABEL.get(verdict, '未审片')
    counts = {k: sum(1 for s in analysis['shots'] if s['status'] == k) for k in STATUS_CLASS}
    lo, hi = analysis['asl']
    stats = ' · '.join(f'{k} {v}' for k, v in counts.items())
    who = ' · '.join(str(x) for x in [review.get('reviewer'), review.get('date'),
                                      f"第 {review['rounds']} 轮" if review.get('rounds') else None] if x)
    rows = _lines([('审片', who), ('机检', f"{stats} · 平均镜长 {analysis['avg']:g}s（区间 {lo:g}–{hi:g}s）")])
    notes = ''.join(f'<li>{esc(n)}</li>' for n in analysis['notes'])
    return (f'<section class="review"><h2>导演审核</h2>'
            f'<span class="verdict v-{verdict.lower() if verdict in VERDICT_LABEL else "none"}">{esc(label)}</span>'
            f'<p class="core">{esc(review.get("summary"))}</p><div class="kv">{rows}</div>'
            f'{_pace_chart(analysis["shots"])}'
            + (f'<ul class="pace-notes">{notes}</ul>' if notes else '') + _issues(review) + '</section>')


def _post(sb):
    post = sb.get('post') or {}
    rows = _lines([('剪辑', post.get('edit')), ('调色', post.get('color')), ('声音', post.get('sound'))])
    out = f'<section><h2>剪辑与视听建议</h2><div class="kv">{rows}</div></section>' if rows else ''
    qs = ''.join(f'<li>{esc(q)}</li>' for q in sb.get('open_questions') or [])
    if qs:
        out += f'<section><h2>待确认事项</h2><ul>{qs}</ul></section>'
    return out


def page(title, body, vertical=False):
    cls = ' class="vertical"' if vertical else ''
    return (f'<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(title)}</title><style>{CSS}</style></head>'
            f'<body{cls}>{body}<div id="lb" hidden><img alt=""></div><script>{JS}</script></body></html>\n')


def render_storyboard(sb, base_dir):
    project = sb.get('project') or {}
    analysis = analyze(sb)
    body = (_head(project) + _strategy(sb.get('strategy') or {}) + _refs(sb.get('refs') or [], base_dir)
            + _review_section(sb, analysis) + _table(sb, base_dir, analysis['shots']) + _post(sb))
    return page(f"{project.get('title') or '分镜表'} · 分镜表", f'<main>{body}</main>',
                vertical=project.get('aspect') == '9:16')


def collect(samples_dir):
    """读取 samples_dir 下各子目录的 storyboard.json，按目录名排序；读不了或不合规的跳过并提示。"""
    entries = []
    for f in sorted(Path(samples_dir).glob('*/storyboard.json')):
        try:
            sb = load_storyboard(f)
        except (OSError, ValueError) as e:
            print(f'⚠️  跳过 {f}：{e}')
            continue
        errors, _ = check(sb)
        if errors:
            print(f'⚠️  跳过 {f}：{errors[0]}')
            continue
        p = sb['project']
        shots = sb['shots']
        first = shots[0].get('frame') or ''
        has_thumb = bool(first) and (f.parent / first).is_file()
        entries.append({
            'dir': f.parent.name, 'title': p.get('title'), 'genre': p.get('genre'),
            'duration_s': p.get('duration_s'), 'aspect': p.get('aspect'), 'shots': len(shots),
            'scope': '节选' if p.get('scope') == 'segment' else '整片',   # 完整说明留在详情页
            'thumb': quote(f'{f.parent.name}/{first}') if has_thumb else '',
            'verdict': VERDICT_LABEL.get((sb.get('review') or {}).get('verdict'), '未审片'),
        })
    return entries


def render_index(entries):
    cards = []
    for e in entries:
        thumb = f'<img src="{esc(e["thumb"])}" alt="" loading="lazy">' if e['thumb'] else '<div class="missing">未出图</div>'
        cards.append(
            f'<a class="card" href="{esc(e["dir"])}/storyboard.html">{thumb}'
            f'<div class="chip">{esc(genre_name(e["genre"]))}</div><h3>{esc(e["title"])}</h3>'
            f'<p>{esc(e["duration_s"])}s · {esc(e["aspect"])} · {e["shots"]} 镜 · {esc(e["scope"])}</p>'
            f'<p>审片：{esc(e["verdict"])}</p></a>')
    body = (f'<main><header><h1>分镜样例总览</h1><p class="core">{len(entries)} 个片种，点卡片看分镜表</p></header>'
            f'<div class="cards">{"".join(cards)}</div></main>')
    return page('分镜样例总览', body)


def main(argv=None):
    ap = argparse.ArgumentParser(description='渲染分镜表 HTML')
    ap.add_argument('path', help='storyboard.json；配合 --index 时是样例目录')
    ap.add_argument('--index', action='store_true', help='把目录下各子目录的分镜表汇成总览页')
    ap.add_argument('-o', '--out', help='输出路径')
    a = ap.parse_args(argv)
    src = Path(a.path)
    try:
        if a.index:
            out = Path(a.out) if a.out else src / 'index.html'
            text = render_index(collect(src))
        else:
            out = Path(a.out) if a.out else src.parent / 'storyboard.html'
            sb = load_storyboard(src)
            errors, _ = check(sb)
            if errors:
                print('❌ 分镜没通过校验，先跑 validate.py 改好再渲染：')
                for e in errors[:10]:
                    print(f'   {e}')
                return 1
            text = render_storyboard(sb, src.parent)
        out.write_text(text, encoding='utf-8')
    except (OSError, ValueError) as e:   # ValueError 涵盖 JSON 解析错误和编码错误
        print(f'❌ 渲染失败：{e}')
        return 1
    print(f'已生成 {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
