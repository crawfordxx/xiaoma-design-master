#!/usr/bin/env python3
"""成片体检 + 剪点重复帧 / 闪帧检查 + 剪辑报告；也能做素材体检。

用法:
    python3 check.py clips <项目目录> [--clips 目录]           素材体检：每段时长、内部切点、画面突变、人声区间
    python3 check.py film <成片.mp4> [--edl edl.json] [--storyboard storyboard.json] [--out 目录] [--no-asr]

film 模式产出（--out 目录，默认成片旁的 <成片名>-review/）：
    report.json / report.md   剪辑报告（计划 vs 实际时长、平均镜长、超时镜头、闪帧、重复画面、黑场、响度、台词完整度、字卡审计）
    sheet.jpg                 每镜中间帧拼图（带镜号和时间码），用来目检字卡和画面
有 edl 时 report.md 还会复制一份到成片旁边：<成片名>.report.md
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asr  # noqa: E402
import cards  # noqa: E402
import scenecut as sc  # noqa: E402
from common import (EditorError, clip_path, find_font, load_storyboard, probe, read_audio,  # noqa: E402
                    require_ffmpeg)
from plan import energy_span  # noqa: E402
from report import render_markdown  # noqa: E402

NOTE_WORDS = re.compile(r"后期|合成|备注|字卡|竖排|画右|画左|小窗|名牌|屏幕|片名下")
MATCH_TOL = 2.5   # 帧：检测到的切点与计划剪点的容差
COVER_OK = 0.6    # 台词转写覆盖率低于它 → 可能被剪断，也可能是同音字，要人耳确认
MIN_CHECKABLE_CHARS = 2   # 少于两个字的台词（“嗯”“走”这类口气词）转写验不了，不列入覆盖率
LINE_FIT_TOL = 0.05       # 秒：剪辑窗口盖住素材人声区间的容差


def loudness(video: Path) -> dict:
    log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    tail = log[log.rfind("Summary:"):]
    get = lambda key: (re.search(key + r":\s*(-?[\d.]+)", tail) or [None, None])[1]  # noqa: E731
    return {"integrated_lufs": _f(get("I")), "lra": _f(get("LRA")), "true_peak_dbfs": _f(get("Peak"))}


def _f(x):
    return float(x) if x not in (None, "") else None


def contact_sheet(video: Path, marks: list[tuple[str, float]], out: Path, font: str | None,
                  cell_w: int = 240, cols: int = 6) -> Path | None:
    from PIL import Image, ImageDraw, ImageFont
    tiles = []
    for label, t in marks:
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                            "-vf", f"scale={cell_w}:-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                           capture_output=True)
        if not r.stdout:
            continue
        import io
        im = Image.open(io.BytesIO(r.stdout)).convert("RGB")
        fnt = ImageFont.truetype(font, 16) if font else ImageFont.load_default()
        ImageDraw.Draw(im).text((6, 4), label, fill="yellow", font=fnt, stroke_width=2, stroke_fill="black")
        tiles.append(im)
    if not tiles:
        return None
    h = max(t.height for t in tiles)
    rows = (len(tiles) - 1) // cols + 1
    sheet = Image.new("RGB", (cols * cell_w, rows * h), "black")
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * cell_w, (i // cols) * h))
    sheet.save(out, quality=85)
    return out


def cut_checks(video: Path, plan_cuts: list[float], pic_end: float | None) -> dict:
    frames, fps = sc.read_frames(video)
    shots = sc.film_shots(frames, fps)
    detected = [s["start"] for s in shots[1:]]
    tol = MATCH_TOL / fps
    expected = plan_cuts + ([pic_end] if pic_end else [])
    extra = [t for t in detected if expected and all(abs(t - c) > tol for c in expected)]
    missing = [c for c in plan_cuts if all(abs(t - c) > tol for t in detected)]
    return {"fps": fps, "detected_shots": len(shots), "shots": shots,
            "flashes": sc.flashes(shots), "extra_cuts": extra, "missing_cuts": missing,
            "duplicates": sc.duplicate_at_cuts(frames, fps, plan_cuts),
            "black_tail_s": sc.black_tail(frames, fps)}


def line_window_check(plans: list[dict]) -> list[dict]:
    """台词有没有被剪断（不靠转写，所以不受同音字影响）。

    素材里量到的人声区间（edl 的 speech_clip）必须被剪辑窗口 start..start+dur 盖住；
    盖不住就是真把字剪掉了，报开头 / 结尾各被切了多少秒。
    """
    out = []
    for p in plans:
        sp = p.get("speech_clip")
        if not p.get("has_line") or not sp:
            continue
        head = sp[0] - p["start"]                      # <0 → 入点在人声之后，切了头
        tail = p["start"] + p["dur"] - sp[1]            # <0 → 出点在人声之前，切了尾
        if head < -LINE_FIT_TOL or tail < -LINE_FIT_TOL:
            out.append({"no": p["no"], "clipped_head_s": round(max(0.0, -head), 2),
                        "clipped_tail_s": round(max(0.0, -tail), 2),
                        "speech_in_clip": [round(sp[0], 2), round(sp[1], 2)],
                        "window": [p["start"], round(p["start"] + p["dur"], 2)]})
    return out


def dialogue_checks(video: Path, plans: list[dict], sb: dict, cuts: list[float]) -> dict:
    segs = asr.transcribe(video)
    if segs is None:
        return {"skipped": "没装本地转写库"}
    shots = {s["no"]: s for s in sb["shots"]}
    lines, straddle, unverifiable = [], [], []
    for p in plans:
        expected = cards.line_text(shots[p["no"]].get("dialogue"))
        if not expected:
            continue
        if len(asr.chars(expected)) < MIN_CHECKABLE_CHARS:
            unverifiable.append({"no": p["no"], "expected": expected})   # “嗯……”这类，转写验不了
            continue
        a, b = p["at"], p["at"] + p["dur"]
        heard = "".join(s["text"] for s in segs if sc.overlap((s["start"], s["end"]), (a, b)) > 0.2)
        lines.append({"no": p["no"], "expected": expected, "heard": heard,
                      "coverage": asr.coverage(expected, heard)})
    for s in segs:
        for c in cuts:
            if s["start"] + 0.25 < c < s["end"] - 0.25:
                straddle.append({"at": c, "text": s["text"], "start": s["start"], "end": s["end"]})
    return {"lines": lines, "low_coverage": [x for x in lines if x["coverage"] < COVER_OK],
            "unverifiable": unverifiable, "straddle": straddle, "transcript": segs}


def pacing(plans: list[dict], sb: dict) -> dict:
    rows = [{"no": p["no"], "planned": p["planned"], "actual": p["dur"], "delta": round(p["dur"] - p["planned"], 2),
             "dialogue": p["has_line"], "in": p["start"], "flags": p.get("flags", [])} for p in plans]
    durs = [r["actual"] for r in rows]
    asl = round(sum(durs) / len(durs), 2)
    planned_total = round(sum(r["planned"] for r in rows), 2)
    over = [r for r in rows if r["delta"] > 0.05]
    under = [r for r in rows if r["delta"] < -0.05]
    target = (sb.get("project") or {}).get("asl")
    return {"rows": rows, "asl": asl, "asl_target": target, "planned_total": planned_total,
            "actual_total": round(sum(durs), 2), "over_plan": over, "under_plan": under,
            "over_5s": [r for r in rows if r["actual"] > 5.0]}


def text_audit(plans: list[dict], dropped: list[dict]) -> dict:
    leaked = [{"no": p["no"], "text": c["text"]} for p in plans for c in p.get("cards", [])
              if NOTE_WORDS.search(c["text"])]
    return {"dropped": dropped, "leaked_notes": leaked}


def film_report(video: Path, edl_path: Path | None, sb: dict | None, out_dir: Path, use_asr: bool = True) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    edl = json.loads(edl_path.read_text(encoding="utf-8")) if edl_path else None
    plans = (edl or {}).get("shots", [])
    plan_cuts = [p["at"] for p in plans[1:]]
    pic_end = plans[-1]["at"] + plans[-1]["dur"] if plans and edl.get("tail_black") else None
    rep = {"video": video.name, "duration_s": round(probe(video)["duration"], 2),
           "cuts": cut_checks(video, plan_cuts, pic_end), "loudness": loudness(video)}
    if edl and sb:
        rep["pacing"] = pacing(plans, sb)
        rep["text"] = text_audit(plans, edl.get("dropped_text", []))
        rep["sound"] = edl.get("sound", {})
        rep["lufs_target"] = edl.get("lufs_target", -16)
        rep["asr_used_for_cut"] = edl.get("asr")
        rep["line_window"] = line_window_check(plans)
        if use_asr:
            rep["dialogue"] = dialogue_checks(video, plans, sb, plan_cuts)
    try:
        font = find_font()
    except EditorError:
        font = None
    marks = ([(f"#{p['no']} {p['at']:.1f}s", p["at"] + p["dur"] / 2) for p in plans] if plans else
             [(f"{s['start']:.1f}s", (s["start"] + s["end"]) / 2) for s in rep["cuts"]["shots"]])
    sheet = contact_sheet(video, marks[:72], out_dir / "sheet.jpg", font)
    rep["sheet"] = sheet.name if sheet else None
    rep["cuts"].pop("shots")
    (out_dir / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    md = out_dir / "report.md"
    md.write_text(render_markdown(rep), encoding="utf-8")
    if edl:
        shutil.copy(md, video.with_name(video.stem + ".report.md"))
    return md


def clips_report(project: Path, clips_dir: Path | None, sb: dict) -> list[dict]:
    rows = []
    for shot in sb["shots"]:
        clip = clip_path(project, shot["no"], clips_dir)
        if not clip.is_file():
            rows.append({"no": shot["no"], "missing": True})
            continue
        info = probe(clip)
        frames, fps = sc.read_frames(clip)
        segs = asr.transcribe(clip, project / "edit" / "asr")
        span = asr.speech_span(segs)
        if span is None and cards.line_text(shot.get("dialogue")) and segs is not None:
            span = energy_span(read_audio(clip))
        rows.append({"no": shot["no"], "duration": round(info["duration"], 2), "size": f"{info['width']}x{info['height']}",
                     "fps": round(info["fps"], 2), "audio": info["has_audio"],
                     "internal_cuts": [s.start for s in sc.segments(frames, fps)[1:]],
                     "events": sc.detect_events(frames, fps), "black_tail": sc.black_tail(frames, fps),
                     "planned": shot["duration_s"], "dialogue": bool(cards.line_text(shot.get("dialogue"))),
                     "speech": span, "heard": " ".join(s["text"] for s in segs or [])})
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    c = sub.add_parser("clips")
    c.add_argument("project_dir")
    c.add_argument("--clips")
    c.add_argument("--storyboard")
    f = sub.add_parser("film")
    f.add_argument("video")
    f.add_argument("--edl")
    f.add_argument("--storyboard")
    f.add_argument("--out")
    f.add_argument("--no-asr", action="store_true")
    args = ap.parse_args(argv)
    try:
        require_ffmpeg()
        if args.mode == "clips":
            project = Path(args.project_dir).resolve()
            sb, _ = load_storyboard(project, Path(args.storyboard) if args.storyboard else None)
            rows = clips_report(project, Path(args.clips).resolve() if args.clips else None, sb)
            print(json.dumps(rows, ensure_ascii=False, indent=1))
            return 0
        video = Path(args.video).resolve()
        sb = json.loads(Path(args.storyboard).read_text(encoding="utf-8")) if args.storyboard else None
        edl = Path(args.edl).resolve() if args.edl else None
        if edl and sb is None:
            raise EditorError("给了 --edl 时也要给 --storyboard")
        out = Path(args.out).resolve() if args.out else video.with_name(video.stem + "-review")
        print(film_report(video, edl, sb, out, not args.no_asr))
        return 0
    except EditorError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
