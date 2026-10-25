#!/usr/bin/env python3
"""粗剪主入口：逐镜生成的片段 → 成片。

用法:
    python3 assemble.py <项目目录> [--out 成片.mp4] [--storyboard 路径] [--clips 目录]
                        [--label "AI 生成 · 纯属虚构"] [--tail-black 1.0] [--lufs -16] [--no-asr] [--no-check]

项目目录约定：storyboard/storyboard.json（或 storyboard.json）、clips/sNN.mp4、可选 sound/{beds,sfx,music,vo}/。
流程：体检素材（内部切点、画面突变、人声） → 选入出点 → 粗剪拼接 → 声音层混音 → 字幕字卡 → 成片体检 → 剪辑报告。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asr  # noqa: E402
import cards  # noqa: E402
import scenecut as sc  # noqa: E402
import sound  # noqa: E402
from common import (FPS, SR, EditorError, clip_path, find_font, frame_size, load_storyboard,  # noqa: E402
                    probe, read_audio, require_ffmpeg, run, write_wav)
from plan import energy_span, plan_window  # noqa: E402

MAX_TAIL_BLACK = 3.0
STRAY_MUTE_DB = -30.0


def analyse_clip(clip: Path, shot: dict, asr_cache: Path, use_asr: bool) -> dict:
    """素材体检：时长、画面切分、突变点、人声区间。"""
    info = probe(clip)
    frames, fps = sc.read_frames(clip)
    segs = asr.transcribe(clip, asr_cache) if use_asr else None
    speech, how = asr.speech_span(segs), "转写" if segs else None
    has_line = bool(cards.line_text(shot.get("dialogue")))
    if has_line and speech is None and segs is not None:
        speech, how = energy_span(read_audio(clip)), "能量"
    return {"info": info, "segments": sc.segments(frames, fps), "events": sc.detect_events(frames, fps),
            "speech": speech, "speech_by": how if speech else None, "asr": segs,
            "has_line": has_line, "asr_ok": segs is not None}


def plan_shots(sb: dict, project: Path, clips_dir: Path | None, work: Path, use_asr: bool) -> list[dict]:
    plans, at_frames = [], 0
    for shot in sb["shots"]:
        clip = clip_path(project, shot["no"], clips_dir)
        if not clip.is_file():
            print(f"警告：缺片段 {clip.name}，跳过第 {shot['no']} 镜", file=sys.stderr)
            continue
        a = analyse_clip(clip, shot, work / "asr", use_asr)
        p = plan_window(a["info"]["duration"], float(shot["duration_s"]), a["has_line"], a["speech"],
                        a["segments"], a["events"])
        frames = max(1, round(p["dur"] * FPS))
        p.update({"no": shot["no"], "clip": clip.name, "planned": float(shot["duration_s"]),
                  "frames": frames, "dur": round(frames / FPS, 3), "at": round(at_frames / FPS, 3),
                  "has_line": a["has_line"], "speech_by": a["speech_by"], "speech_clip": a["speech"],
                  "clip_cuts": [s.start for s in a["segments"][1:]], "clip_events": a["events"],
                  "src_w": a["info"]["width"], "src_h": a["info"]["height"], "has_audio": a["info"]["has_audio"]})
        plans.append(p)
        at_frames += frames
    if not plans:
        raise EditorError("一个可用片段都没有")
    return plans


def render_cut(plans: list[dict], project: Path, clips_dir: Path | None, W: int, H: int,
               tail: float, work: Path) -> tuple[Path, Path, int]:
    """一条 ffmpeg 滤镜图：逐镜裁切、统一规格、按帧数对齐、拼接，片尾补黑场。返回 (画面, 同期声, 总帧数)。"""
    inputs, chains, labels = [], [], []
    k = 0
    for p in plans:
        clip = clip_path(project, p["no"], clips_dir)
        s, e = p["start"], p["start"] + p["dur"]
        spf = SR // FPS
        inputs += ["-i", str(clip)]
        v = (f"[{k}:v]trim=start={s:.3f}:end={e + 0.2:.3f},setpts=PTS-STARTPTS,"
             f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,"
             f"tpad=stop_mode=clone:stop_duration=1,trim=end_frame={p['frames']},setpts=PTS-STARTPTS[v{k}]")
        if p["has_audio"]:
            a = (f"[{k}:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,aresample={SR},"
                 f"aformat=channel_layouts=stereo,apad,atrim=end_sample={p['frames'] * spf}[a{k}]")
        else:
            a = f"anullsrc=r={SR}:cl=stereo,atrim=end_sample={p['frames'] * spf}[a{k}]"
        chains += [v, a]
        labels.append(f"[v{k}][a{k}]")
        k += 1
    tail_frames = round(tail * FPS)
    if tail_frames:
        chains += [f"color=c=black:s={W}x{H}:r={FPS},trim=end_frame={tail_frames},setsar=1[vt]",
                   f"anullsrc=r={SR}:cl=stereo,atrim=end_sample={tail_frames * (SR // FPS)}[at]"]
        labels.append("[vt][at]")
    chains.append(f"{''.join(labels)}concat=n={len(labels)}:v=1:a=1[v][a]")
    video, dialog = work / "cut.mp4", work / "dialog.wav"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chains),
         "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", str(video),
         "-map", "[a]", "-c:a", "pcm_s24le", str(dialog)])
    total = sum(p["frames"] for p in plans) + tail_frames
    return video, dialog, total


def timeline(plans: list[dict], sb: dict) -> list[sound.ShotTiming]:
    shots = {s["no"]: s for s in sb["shots"]}
    scenes = dict(zip([s["no"] for s in sb["shots"]], sound.assign_scenes(sb["shots"], sb.get("refs", []))))
    out = []
    for p in plans:
        rel = lambda t: round(t - p["start"], 3)  # noqa: E731
        ev = [rel(e) for e in p["clip_events"] if p["start"] < e < p["start"] + p["dur"]]
        sp = p.get("speech_clip")
        speech = (max(0.0, rel(sp[0])), min(p["dur"], rel(sp[1]))) if sp else None
        out.append(sound.ShotTiming(p["no"], p["at"], p["dur"], shots[p["no"]], scenes[p["no"]], ev, speech))
    return out


def speech_intervals(tl: list[sound.ShotTiming], sound_dir: Path) -> list[tuple[float, float]]:
    """对白区间（BGM 避让用）：有人声定位用人声区间，否则整镜；有旁白音频也算。"""
    out = []
    for t in tl:
        if cards.line_text(t.shot.get("dialogue")):
            a, b = t.speech or (0.0, t.dur)
            out.append((t.at + a - 0.1, t.at + b + 0.2))
        if t.shot.get("vo") and sound.find_asset(sound_dir / "vo", f"s{t.no:02d}"):
            out.append((t.at, t.at + t.dur))
    return out


def build_sound(plans: list[dict], sb: dict, dialog_wav: Path, n: int, sound_dir: Path,
                work: Path, lufs: float, keep_stray: bool) -> tuple[Path, dict]:
    tl = timeline(plans, sb)
    dialog = sound.fit(read_audio(dialog_wav), n)
    muted = []
    for p, t in zip(plans, tl):
        if not p["has_line"] and t.speech and not keep_stray:
            a, b = int((t.at + t.speech[0] - 0.1) * SR), int((t.at + t.speech[1] + 0.1) * SR)
            env = sound.duck_envelope(n, [(a / SR, b / SR)], STRAY_MUTE_DB, ramp=0.05)
            dialog = dialog * env[:, None]
            muted.append({"no": p["no"], "from": round(a / SR, 2), "to": round(b / SR, 2)})
            p["flags"].append("无台词镜检出人声（已压低）")
    for t in tl:
        vo = sound.find_asset(sound_dir / "vo", f"s{t.no:02d}") if t.shot.get("vo") else None
        if vo:
            clip = read_audio(vo)
            i = int(t.at * SR)
            m = max(0, min(len(clip), n - i))
            dialog[i:i + m] += clip[:m]
    speech = speech_intervals(tl, sound_dir)
    bed, beds_used = sound.render_beds(tl, sb.get("refs", []), sound_dir / "beds", n)
    cues = [{**c, "t": round(t.at + c["t"], 3), "no": t.no}
            for t in tl for c in sound.parse_sfx(t.shot.get("sfx"), t.dur, t.events)]
    cues += sound.beat_cues((sb.get("strategy") or {}).get("beats"), tl)
    fx, fx_used = sound.render_sfx(cues, sound_dir / "sfx", n)
    segs = sound.plan_music(tl)
    music, music_used = sound.render_music(segs, sound_dir / "music", n)
    # 片尾黑场：底噪和 BGM 在画面结束后 0.3 秒内收掉，不拖尾
    pic_end = int((plans[-1]["at"] + plans[-1]["dur"]) * SR)
    fade = sound.duck_envelope(n, [(pic_end / SR + 0.3, n / SR + 1)], -80.0, ramp=0.3)
    mixed, levels = sound.mix(dialog, bed * fade, music * fade, fx, speech, n)
    raw, norm = work / "mix_raw.wav", work / "mix.wav"
    write_wav(raw, mixed)
    measured = sound.loudnorm(raw, norm, target=lufs)
    return norm, {"levels": levels, "beds": beds_used, "sfx": fx_used, "music": music_used,
                  "speech_intervals": [(round(a, 2), round(b, 2)) for a, b in speech],
                  "stray_voice_muted": muted, "pre_loudnorm_lufs": measured.get("input_i")}


def build_overlays(plans: list[dict], sb: dict, ts: cards.Typesetter, label: str, work: Path) -> tuple[list, list]:
    shots = {s["no"]: s for s in sb["shots"]}
    ovs, dropped = [], []
    pngdir = work / "png"
    pngdir.mkdir(exist_ok=True)

    def add(im, x, y, t0, t1, name):
        path = pngdir / f"{name}.png"
        im.save(path)
        ovs.append(cards.Overlay(path, int(x), int(y), round(t0, 3), round(t1, 3)))

    for p in plans:
        shot, t0, t1 = shots[p["no"]], p["at"], p["at"] + p["dur"]
        line = cards.line_text(shot.get("dialogue")) or cards.line_text(shot.get("vo"))
        if line:
            a, b = t0, t1
            if p.get("speech_clip") and cards.line_text(shot.get("dialogue")):
                a = max(t0, t0 + p["speech_clip"][0] - p["start"] - 0.15)
                b = min(t1, t0 + p["speech_clip"][1] - p["start"] + 0.4)
            add(*ts.subtitle(line), a, b, f"sub{p['no']:02d}")
        cs, drop = cards.parse_ost(shot.get("on_screen_text"))
        dropped += [{"no": p["no"], "text": d} for d in drop]
        box = cards.map_screen_box(shot.get("screen_box"), p["src_w"], p["src_h"], ts.W, ts.H)
        for ci, c in enumerate(cs):
            ca, cb = t0 + c.start * p["dur"], t0 + c.end * p["dur"]
            for j, (im, x, y) in enumerate(ts.place(c, box)):
                add(im, x, y, ca, cb, f"ost{p['no']:02d}_{ci}_{j}")
        p["cards"] = [{"kind": c.kind, "text": c.text, "screen_box": bool(box) if c.kind == "screen" else None}
                      for c in cs]
    end = plans[-1]["at"] + plans[-1]["dur"]
    if label:
        add(*ts.label(label), 0, end, "label")
    return ovs, dropped


def render_final(cut: Path, mix: Path, overlays: list, out: Path) -> None:
    inputs = ["-i", str(cut), "-i", str(mix)]
    chain, last = [], "0:v"
    for k, o in enumerate(overlays):
        inputs += ["-i", str(o.png)]
        chain.append(f"[{last}][{k + 2}:v]overlay={o.x}:{o.y}:enable='between(t,{o.t0:.3f},{o.t1 - 0.001:.3f})'[o{k}]")
        last = f"o{k}"
    graph = ";".join(chain) if chain else "[0:v]null[o]"
    last = last if chain else "o"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", f"[{last}]", "-map", "1:a",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir")
    ap.add_argument("--out", help="成片路径，默认 <项目目录>/final.mp4")
    ap.add_argument("--storyboard")
    ap.add_argument("--clips", help="片段目录，默认 <项目目录>/clips")
    ap.add_argument("--work", help="中间文件目录，默认 <项目目录>/edit/<成片名>")
    ap.add_argument("--sound", help="声音素材目录，默认 <项目目录>/sound")
    ap.add_argument("--label", default="AI 生成 · 纯属虚构", help="角标文字，空字符串不加")
    ap.add_argument("--tail-black", type=float, default=1.0, help=f"片尾黑场秒数（≤{MAX_TAIL_BLACK}）")
    ap.add_argument("--lufs", type=float, default=-16.0)
    ap.add_argument("--font")
    ap.add_argument("--no-asr", action="store_true", help="不做人声定位，按分镜时长剪")
    ap.add_argument("--keep-stray-voice", action="store_true", help="无台词镜里检出的人声不压低")
    ap.add_argument("--no-check", action="store_true", help="不跑成片体检")
    args = ap.parse_args(argv)
    try:
        return run_assemble(args)
    except EditorError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1


def run_assemble(args: argparse.Namespace) -> int:
    require_ffmpeg()
    project = Path(args.project_dir).resolve()
    sb, sb_path = load_storyboard(project, Path(args.storyboard) if args.storyboard else None)
    out = Path(args.out).resolve() if args.out else project / "final.mp4"
    work = Path(args.work).resolve() if args.work else project / "edit" / out.stem
    work.mkdir(parents=True, exist_ok=True)
    sound_dir = Path(args.sound).resolve() if args.sound else project / "sound"
    clips_dir = Path(args.clips).resolve() if args.clips else None
    tail = min(max(args.tail_black, 0.0), MAX_TAIL_BLACK)
    if args.tail_black > MAX_TAIL_BLACK:
        print(f"警告：片尾黑场 {args.tail_black}s 超过 {MAX_TAIL_BLACK}s，已截到 {MAX_TAIL_BLACK}s", file=sys.stderr)
    use_asr = not args.no_asr and asr.available()
    if not args.no_asr and not use_asr:
        print("警告：没装本地转写库，跳过人声定位，对白镜按分镜时长剪，可能切掉半句；"
              "装上后重跑（asr.py 顶部写了当前支持哪个实现，见 SKILL.md「环境依赖」）", file=sys.stderr)
    W, H = frame_size(sb)
    ts = cards.Typesetter(find_font(args.font), W, H)

    print("1/5 体检素材、选入出点", flush=True)
    plans = plan_shots(sb, project, clips_dir, work, use_asr)
    print("2/5 粗剪拼接", flush=True)
    cut, dialog, total_frames = render_cut(plans, project, clips_dir, W, H, tail, work)
    n = total_frames * (SR // FPS)
    print("3/5 声音层混音", flush=True)
    mix, sound_info = build_sound(plans, sb, dialog, n, sound_dir, work, args.lufs, args.keep_stray_voice)
    print("4/5 字幕字卡、出成片", flush=True)
    overlays, dropped = build_overlays(plans, sb, ts, args.label, work)
    render_final(cut, mix, overlays, out)
    edl = {"storyboard": sb_path.name, "fps": FPS, "size": [W, H], "tail_black": tail,
           "duration": round(total_frames / FPS, 3), "shots": plans, "sound": sound_info,
           "dropped_text": dropped, "asr": use_asr, "lufs_target": args.lufs}
    edl_path = work / "edl.json"
    edl_path.write_text(json.dumps(edl, ensure_ascii=False, indent=1, default=_json), encoding="utf-8")
    print(f"成片 {out}（{len(plans)} 镜，{edl['duration']:.1f}s）；剪辑单 {edl_path}")
    if not args.no_check:
        print("5/5 成片体检、剪辑报告", flush=True)
        import check
        report = check.film_report(out, edl_path, sb, work / "review", use_asr)
        print(f"剪辑报告 {report}")
    return 0


def _json(o):
    if isinstance(o, sc.Segment):
        return {"start": o.start, "end": o.end, "black": o.black}
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    raise TypeError(type(o))


if __name__ == "__main__":
    sys.exit(main())
