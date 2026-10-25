"""剪辑报告渲染：把 check.film_report 收集到的 dict 变成人能读的 Markdown。

纯标准库、纯函数，不碰 ffmpeg，所以没有素材的机器上也能测。
判定分三档：PASS（✅）/ WARN（⚠️ 要人看一眼，不一定是错）/ FAIL（❌ 必须修）。
门槛常量都写在文件头，改门槛只改这里。
"""
from __future__ import annotations

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
MARK = {PASS: "✅", WARN: "⚠️", FAIL: "❌"}

LUFS_TOL = 1.0          # 实测响度与目标之差（LU）
MAX_TAIL_BLACK = 3.0    # 片尾黑场秒数
MAX_SHOT_S = 5.0        # 非高潮单镜上限
MIN_SHOT_S = 0.5        # 单镜下限（短于它不可读）
FLASH_S = 0.3           # 闪帧门槛
COVER_OK = 0.6          # 台词转写覆盖率
DUP_SIM = 0.80          # 剪点两侧重复画面相似度
SFX_LIST_MAX = 40       # 报告里最多列多少条音效
BED_LIST_MAX = 24       # 报告里最多列多少段底噪


def _f(x, nd=2):
    return "—" if x is None else f"{float(x):.{nd}f}"


def _asl_range(asl_target) -> tuple[float, float] | None:
    """project.asl 可能是 [2.2, 3.8]、"2.2–3.8" 或缺省。"""
    if isinstance(asl_target, (list, tuple)) and len(asl_target) == 2:
        return float(asl_target[0]), float(asl_target[1])
    if isinstance(asl_target, str):
        nums = [n for n in asl_target.replace("~", "–").replace("-", "–").split("–") if n.strip()]
        try:
            if len(nums) == 2:
                return float(nums[0]), float(nums[1])
            if len(nums) == 1:
                v = float(nums[0])
                return round(v * 0.8, 3), round(v * 1.2, 3)
        except ValueError:
            return None
    return None


def verdict(rep: dict) -> list[tuple[str, str, str]]:
    """逐条判定，返回 [(档, 项目, 说明)]。缺哪块就跳过哪块，不猜。"""
    out: list[tuple[str, str, str]] = []
    cuts, pacing = rep.get("cuts") or {}, rep.get("pacing") or {}
    loud, dial = rep.get("loudness") or {}, rep.get("dialogue") or {}
    text = rep.get("text") or {}

    target = rep.get("lufs_target", -16)
    i = loud.get("integrated_lufs")
    if i is None:
        out.append((WARN, "响度", "没测到 integrated LUFS（音轨缺失或过短）"))
    else:
        d = abs(i - target)
        out.append((PASS if d <= LUFS_TOL else FAIL, "响度",
                    f"{_f(i, 1)} LUFS，目标 {target}（差 {_f(d, 1)} LU，容差 {LUFS_TOL}）"))
    tp = loud.get("true_peak_dbfs")
    if tp is not None and tp > -1.0 + 0.5:
        out.append((WARN, "真峰值", f"{_f(tp, 1)} dBTP，超过 -1.0 dBTP 会被平台再压一次"))

    tail = cuts.get("black_tail_s")
    if tail is not None:
        out.append((PASS if tail <= MAX_TAIL_BLACK else FAIL, "片尾黑场",
                    f"{_f(tail)}s（门槛 ≤{MAX_TAIL_BLACK}s）"))

    fl = cuts.get("flashes") or []
    out.append((PASS if not fl else WARN, "闪帧",
                "无" if not fl else f"{len(fl)} 段短于 {FLASH_S}s：" +
                "、".join(f"{_f(s['start'])}s({_f(s['dur'])}s)" for s in fl[:6])))
    dup = cuts.get("duplicates") or []
    out.append((PASS if not dup else WARN, "剪点重复画面",
                "无" if not dup else f"{len(dup)} 处相似度 ≥{DUP_SIM}：" +
                "、".join(f"{_f(d['at'])}s(sim {_f(d['sim'])})" for d in dup[:6]) +
                "（同机位对照是有意的，人工确认）"))
    ex, mi = cuts.get("extra_cuts") or [], cuts.get("missing_cuts") or []
    out.append((PASS if not ex else WARN, "计划外的切点",
                "无" if not ex else f"{len(ex)} 处：" + "、".join(f"{_f(t)}s" for t in ex[:8]) +
                "（多半是片段内部自带切镜没被避开）"))
    out.append((PASS if not mi else WARN, "没检出的计划剪点",
                "无" if not mi else f"{len(mi)} 处：" + "、".join(f"{_f(t)}s" for t in mi[:8]) +
                "（相邻两镜画面太像，或该处是黑场）"))

    if pacing:
        asl, rng = pacing.get("asl"), _asl_range(pacing.get("asl_target"))
        if asl is None:
            out.append((WARN, "平均镜长", "没有 edl，算不出"))
        elif rng is None:
            out.append((WARN, "平均镜长", f"{_f(asl)}s（分镜没给 asl 基准，人工对照片种卡）"))
        else:
            out.append((PASS if rng[0] - 0.3 <= asl <= rng[1] + 0.3 else WARN, "平均镜长",
                        f"{_f(asl)}s，基准 {rng[0]}–{rng[1]}s"))
        over = pacing.get("over_plan") or []
        out.append((PASS if not over else WARN, "超出计划的镜头",
                    "无" if not over else f"{len(over)} 镜：" +
                    "、".join(f"#{r['no']}(+{_f(r['delta'])}s)" for r in over[:10])))
        long_ones = [r for r in pacing.get("over_5s") or [] if r["actual"] > MAX_SHOT_S]
        out.append((PASS if not long_ones else WARN, f"超过 {MAX_SHOT_S}s 的单镜",
                    "无" if not long_ones else
                    "、".join(f"#{r['no']}({_f(r['actual'])}s)" for r in long_ones[:10])))
        short_ones = [r for r in pacing.get("rows") or [] if r["actual"] < MIN_SHOT_S]
        out.append((PASS if not short_ones else WARN, f"短于 {MIN_SHOT_S}s 的单镜",
                    "无" if not short_ones else
                    "、".join(f"#{r['no']}({_f(r['actual'])}s)" for r in short_ones[:10])))
        planned, actual = pacing.get("planned_total"), pacing.get("actual_total")
        if planned and actual:
            drift = (actual - planned) / planned * 100
            out.append((PASS if abs(drift) <= 25 else WARN, "总时长漂移",
                        f"计划 {_f(planned, 1)}s → 实际 {_f(actual, 1)}s（{drift:+.0f}%）"))

    if rep.get("line_window") is None:
        out.append((WARN, "台词没被剪断", "没有 edl，无法核对剪辑窗口是否盖住人声"))
    elif rep["line_window"]:
        out.append((FAIL, "台词被剪断",
                    f"{len(rep['line_window'])} 镜的剪辑窗口没盖住素材里的人声：" +
                    "、".join(f"#{x['no']}(头 {x['clipped_head_s']}s / 尾 {x['clipped_tail_s']}s)"
                             for x in rep["line_window"][:8])))
    else:
        out.append((PASS, "台词没被剪断", "每个对白镜的剪辑窗口都盖住了素材里量到的人声区间"))

    if dial.get("skipped"):
        out.append((WARN, "台词转写自检", f"跳过：{dial['skipped']}；装上转写库重跑才能比对字幕与听到的内容"))
    elif "lines" in dial:
        low = dial.get("low_coverage") or []
        out.append((PASS if not low else WARN, "台词转写覆盖率",
                    f"{len(dial['lines'])} 句全部 ≥{COVER_OK}" if not low else
                    f"{len(low)} 句 <{COVER_OK}：" +
                    "、".join(f"#{x['no']}({_f(x['coverage'])})" for x in low[:8]) +
                    "（同音字也会拉低覆盖率，先听一下再判；上面「台词没被剪断」过了就不是剪断）"))
        st = dial.get("straddle") or []
        if not st:
            out.append((PASS, "台词跨剪点", "无"))
        elif rep.get("line_window") is not None:
            out.append((PASS, "台词跨剪点",
                        f"{len(st)} 句被转写当成跨剪点（" +
                        "、".join(f"{_f(x['at'])}s" for x in st[:8]) +
                        "），但剪辑窗口都盖住了人声 → 多半是上一镜尾音和这一镜起音被合成了一段，听一下确认"))
        else:
            out.append((FAIL, "台词跨剪点",
                        f"{len(st)} 句被剪点切断：" +
                        "、".join(f"{_f(x['at'])}s「{x['text'][:10]}」" for x in st[:8]) +
                        "（没有 edl 的人声区间可对，按不合格处理）"))
        un = dial.get("unverifiable") or []
        if un:
            out.append((WARN, "转写验不了的台词",
                        "、".join(f"#{x['no']}「{x['expected'][:8]}」" for x in un[:6]) +
                        "（不足两个字或只是口气，人耳确认）"))

    leaked = text.get("leaked_notes") or []
    out.append((PASS if not leaked else WARN, "制作备注上屏",
                "无" if not leaked else f"{len(leaked)} 处像备注的文字上了屏：" +
                "、".join(f"#{x['no']}「{x['text'][:14]}」" for x in leaked[:6]) +
                "（屏幕内容本身可能含「备注」二字，人工确认）"))

    sound = rep.get("sound") or {}
    stray = sound.get("stray_voice_muted") or []
    if stray:
        out.append((WARN, "无台词镜里的人声",
                    f"{len(stray)} 镜检出人声并已压低：" +
                    "、".join(f"#{x['no']}" for x in stray[:10]) + "（模型自己冒出来的，最好重出）"))
    if rep.get("asr_used_for_cut") is False:
        out.append((WARN, "剪辑没用人声定位",
                    "按分镜时长剪的，对白镜可能切掉半句；装上转写库重跑"))
    return out


def _table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_（无）_\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def _pacing_md(p: dict) -> str:
    rng = _asl_range(p.get("asl_target"))
    head = [f"## 二、节奏：计划 vs 实际\n",
            f"- 平均镜长 **{_f(p.get('asl'))}s**" +
            (f"（分镜基准 {rng[0]}–{rng[1]}s）" if rng else "（分镜没给 asl 基准）"),
            f"- 总时长：计划 {_f(p.get('planned_total'), 1)}s → 实际 {_f(p.get('actual_total'), 1)}s",
            f"- 超出计划 {len(p.get('over_plan') or [])} 镜 / 短于计划 {len(p.get('under_plan') or [])} 镜\n"]
    rows = [[str(r["no"]), _f(r["planned"]), _f(r["actual"]),
             f"{r['delta']:+.2f}", "对白" if r.get("dialogue") else "", _f(r.get("in")),
             "；".join(r.get("flags") or [])] for r in p.get("rows") or []]
    head.append(_table(["镜", "计划s", "实际s", "偏差", "台词", "入点s", "标记"], rows))
    over = p.get("over_plan") or []
    if over:
        head.append("**被素材撑长的镜头**（按偏差排序，前 10）：\n")
        head.append(_table(["镜", "计划s", "实际s", "偏差s"],
                           [[str(r["no"]), _f(r["planned"]), _f(r["actual"]), f"{r['delta']:+.2f}"]
                            for r in sorted(over, key=lambda r: -r["delta"])[:10]]))
    return "\n".join(head) + "\n"


def _cuts_md(c: dict) -> str:
    out = ["## 三、剪点与画面\n",
           _table(["项", "值"], [
               ["检出镜头段数", str(c.get("detected_shots", "—"))],
               ["帧率", _f(c.get("fps"), 3)],
               ["计划外的切点", "、".join(f"{_f(t)}s" for t in c.get("extra_cuts") or []) or "无"],
               ["没检出的计划剪点", "、".join(f"{_f(t)}s" for t in c.get("missing_cuts") or []) or "无"],
               [f"闪帧（<{FLASH_S}s）", "、".join(f"{_f(s['start'])}–{_f(s['end'])}s"
                                                 for s in c.get("flashes") or []) or "无"],
               [f"剪点重复画面（sim≥{DUP_SIM}）",
                "、".join(f"{_f(d['at'])}s(sim {_f(d['sim'])})" for d in c.get("duplicates") or []) or "无"],
               ["片尾黑场", f"{_f(c.get('black_tail_s'))}s"],
           ])]
    return "\n".join(out) + "\n"


def _sound_md(s: dict) -> str:
    if not s:
        return ""
    lv = s.get("levels") or {}
    out = ["## 四、声音层\n",
           f"- 台词参考电平 {_f(lv.get('ref_db'), 1)} dB → 底噪 {_f(lv.get('bed_db'), 1)} dB、"
           f"BGM {_f(lv.get('bgm_db'), 1)} dB（对白段再降 {lv.get('duck_db', '—')} dB）",
           f"- 混音后未做响度归一时是 {_f(s.get('pre_loudnorm_lufs'), 1)} LUFS，"
           f"归一到 {s.get('lufs_target', '—')} LUFS" if s.get("pre_loudnorm_lufs") is not None
           else "- 混音后未做响度归一",
           f"- 对白避让区间 {len(s.get('speech_intervals') or [])} 段\n"]
    beds = s.get("beds") or []
    out.append(f"**环境底噪**（{len(beds)} 段）\n")
    out.append(_table(["场景", "起s", "止s", "用料"],
                      [[str(b.get("scene") or "—"), _f(b.get("from")), _f(b.get("to")), str(b.get("source"))]
                       for b in beds[:BED_LIST_MAX]]))
    if len(beds) > BED_LIST_MAX:
        out.append(f"_…另有 {len(beds) - BED_LIST_MAX} 段_\n")
    mus = s.get("music") or []
    out.append(f"**BGM 情绪段落**（{len(mus)} 段）\n")
    out.append(_table(["情绪", "起s", "止s", "淡入", "淡出", "用料"],
                      [[str(m.get("mood")), _f(m.get("t0")), _f(m.get("t1")), _f(m.get("fade_in")),
                        _f(m.get("fade_out")), str(m.get("source"))] for m in mus]))
    fx = s.get("sfx") or []
    kinds: dict[str, int] = {}
    for f in fx:
        kinds[f.get("type", "?")] = kinds.get(f.get("type", "?"), 0) + 1
    out.append(f"**音效**（{len(fx)} 个）：" +
               ("、".join(f"{k}×{v}" for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])) or "无") + "\n")
    out.append(_table(["时间s", "类型", "增益", "镜", "用料"],
                      [[_f(f.get("t")), str(f.get("type")), _f(f.get("gain")), str(f.get("no", "—")),
                        str(f.get("source"))] for f in fx[:SFX_LIST_MAX]]))
    if len(fx) > SFX_LIST_MAX:
        out.append(f"_…另有 {len(fx) - SFX_LIST_MAX} 个_\n")
    stray = s.get("stray_voice_muted") or []
    if stray:
        out.append("**无台词镜里检出的人声（已压低）**：" +
                   "、".join(f"#{x['no']} {_f(x['from'])}–{_f(x['to'])}s" for x in stray) + "\n")
    return "\n".join(out) + "\n"


def _dialogue_md(rep: dict) -> str:
    d, lw = rep.get("dialogue") or {}, rep.get("line_window")
    if not d and lw is None:
        return ""
    out = ["## 五、台词\n"]
    if lw is not None:
        out.append(f"**剪辑窗口 vs 素材人声**（不靠转写，同音字不影响）："
                   + ("全部盖住，没把字剪掉" if not lw else f"{len(lw)} 镜没盖住") + "\n")
        if lw:
            out.append(_table(["镜", "切掉头 s", "切掉尾 s", "素材人声区间", "剪辑窗口"],
                              [[str(x["no"]), _f(x["clipped_head_s"]), _f(x["clipped_tail_s"]),
                                f"{_f(x['speech_in_clip'][0])}–{_f(x['speech_in_clip'][1])}",
                                f"{_f(x['window'][0])}–{_f(x['window'][1])}"] for x in lw]))
    if not d:
        return "\n".join(out) + "\n"
    if d.get("skipped"):
        out.append(f"转写自检跳过：{d['skipped']}。装上本地转写库重跑 `check.py film` 才有下面这张表。\n")
        return "\n".join(out) + "\n"
    out.append(f"**转写自检**（覆盖率 = 分镜台词里的字有多少被听到；同音字会拉低它）\n")
    out.append(_table(["镜", "覆盖率", "分镜台词", "转写听到的"],
                      [[str(x["no"]), _f(x["coverage"]), x["expected"][:24], (x["heard"] or "（没听到）")[:24]]
                       for x in d.get("lines") or []]))
    un = d.get("unverifiable") or []
    if un:
        out.append("**转写验不了的台词**（不足两个字或只是口气，人耳确认）：" +
                   "、".join(f"#{x['no']}「{x['expected']}」" for x in un) + "\n")
    st = d.get("straddle") or []
    if st:
        out.append("**被剪点切断的句子**：" +
                   "、".join(f"{_f(x['at'])}s「{x['text'][:12]}」" for x in st) + "\n")
    return "\n".join(out) + "\n"


def _text_md(t: dict) -> str:
    if not t:
        return ""
    out = ["## 六、字卡审计\n"]
    drop = t.get("dropped") or []
    out.append(f"**没有上屏的内容**（{len(drop)} 条，制作备注与虚构声明都在这里）\n")
    out.append(_table(["镜", "内容"], [[str(x["no"]), str(x["text"])[:60]] for x in drop]))
    leaked = t.get("leaked_notes") or []
    if leaked:
        out.append("**像制作备注却上了屏的字**（人工确认）：" +
                   "、".join(f"#{x['no']}「{x['text'][:20]}」" for x in leaked) + "\n")
    return "\n".join(out) + "\n"


def render_markdown(rep: dict) -> str:
    """report dict → Markdown 全文。缺 edl/storyboard 时只出机检那几节。"""
    v = verdict(rep)
    n_fail = sum(1 for x in v if x[0] == FAIL)
    n_warn = sum(1 for x in v if x[0] == WARN)
    head = [f"# 剪辑报告 · {rep.get('video', '?')}\n",
            f"成片时长 **{_f(rep.get('duration_s'), 1)}s**　判定：**{n_fail} 项不合格 / {n_warn} 项待人工确认**"
            + ("　全部通过" if not n_fail and not n_warn else "") + "\n",
            "## 一、总判定\n",
            _table(["", "项目", "说明"], [[MARK[lvl], name, msg] for lvl, name, msg in v])]
    parts = ["\n".join(head)]
    if rep.get("pacing"):
        parts.append(_pacing_md(rep["pacing"]))
    if rep.get("cuts"):
        parts.append(_cuts_md(rep["cuts"]))
    if rep.get("sound"):
        parts.append(_sound_md({**rep["sound"], "lufs_target": rep.get("lufs_target")}))
    if rep.get("dialogue") or rep.get("line_window") is not None:
        parts.append(_dialogue_md(rep))
    if rep.get("text"):
        parts.append(_text_md(rep["text"]))
    parts.append("## 七、不合格怎么修\n\n"
                 "- 响度不对：改 `assemble.py --lufs`，或检查是否只有底噪没有台词（参考电平会掉到兜底值）\n"
                 "- 片尾黑场超 3s：`--tail-black 1.0`；卡点后不要接空镜拖时长\n"
                 f"- 闪帧 / 计划外切点：片段内部自带切镜，看 edl 里该镜的 `clip_cuts`，"
                 f"改 `plan.py` 的 HEAD_SKIP 或重出该镜\n"
                 f"- 剪点重复画面：上一镜出点和下一镜入点是同一帧画面，"
                 f"挪入点（`avoid_slivers`）或换镜；同机位对照是有意的，确认后忽略\n"
                 f"- 台词被剪断（窗口没盖住人声）：素材里那句话比可用镜头段长，"
                 f"加长该镜 `duration_s` 或重出一段更长的；装转写库才能量到人声区间\n"
                 f"- 台词覆盖率 <{COVER_OK}：先看「台词没被剪断」是否 ✅。✅ 就多半是同音字（地名、人名），"
                 f"把关键词上字幕；❌ 才真的要去改入出点\n"
                 "- 制作备注上屏：把 `on_screen_text` 里的备注写进括号，`parse_ost` 会自动丢掉\n"
                 "- 平均镜长超基准：不是剪慢，是分镜给长了；回到分镜改 `duration_s`\n")
    if rep.get("sheet"):
        parts.append(f"_每镜中间帧拼图：`{rep['sheet']}`（目检字卡位置、屏幕区域、画面漂移）_\n")
    return "\n".join(parts)
