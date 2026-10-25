"""声音层：环境底噪（按场景）、音效（按 sfx 字段 + 关键节拍）、BGM 长音 pad（按 music 字段，对白避让）、混音。

所有层先在 numpy 里按样本对齐到成片总长，再统一做两遍 loudnorm。合成音色复用 studio/engine/audio.py。
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from common import SKILL_DIR, SR, db, read_audio, rms, run, undb

sys.path.insert(0, str(SKILL_DIR / "studio" / "engine"))
import audio as studio  # noqa: E402  技能内软链 studio -> xiaoma-studio

AUDIO_EXT = (".wav", ".flac", ".mp3", ".m4a", ".aac", ".mp4", ".mov")
BED_REL_DB = -20.0     # 底噪 RMS 比台词低
BGM_REL_DB = -14.0     # BGM RMS 比台词低（无台词时）
DUCK_DB = -12.0        # 对白段 BGM 再降
SFX_PEAK_REL_DB = 6.0  # 音效峰值相对台词 RMS
FALLBACK_REF_DB = -26.0


@dataclass
class ShotTiming:
    """一镜在成片里的位置，和声音层需要的信息。时间都以秒计。"""
    no: int
    at: float
    dur: float
    shot: dict
    scene: str | None = None
    events: list[float] = field(default_factory=list)     # 画面突变（相对镜头起点）
    speech: tuple[float, float] | None = None              # 人声区间（相对镜头起点）


# ---------- 素材查找 ----------

def find_asset(folder: Path, name: str) -> Path | None:
    for ext in AUDIO_EXT:
        p = folder / f"{name}{ext}"
        if p.is_file():
            return p
    return None


def load_loop(path: Path, n: int, xfade: float = 0.5) -> np.ndarray:
    """读素材为单声道，短了就交叉淡化循环铺满 n 个样本。"""
    x = read_audio(path).mean(1)
    if len(x) == 0:
        return np.zeros(n, np.float32)
    if len(x) >= n:
        return x[:n]
    k = min(int(xfade * SR), len(x) // 3)
    out = np.zeros(n, np.float32)
    pos = 0
    ramp = np.linspace(0, 1, k, dtype=np.float32) if k else np.zeros(0, np.float32)
    while pos < n:
        seg = x.copy()
        if pos and k:
            seg[:k] *= ramp
            out[pos:pos + k] *= 1 - ramp[: max(0, min(k, n - pos))]
        end = min(n, pos + len(seg))
        out[pos:end] += seg[: end - pos]
        pos += len(seg) - k if k else len(seg)
    return out


# ---------- 场景与底噪 ----------

def assign_scenes(shots: list[dict], refs: list[dict]) -> list[str | None]:
    """镜头的场景：shot.scene > refs 里第一个 location > 沿用上一镜。"""
    locs = {r["id"] for r in refs or [] if r.get("type") == "location"}
    out, cur = [], None
    for s in shots:
        cand = s.get("scene") or next((r for r in s.get("refs") or [] if r in locs), None)
        cur = cand or cur
        out.append(cur)
    first = next((c for c in out if c), None)
    return [c or first for c in out]


def bed_preset(ref: dict | None) -> str:
    text = " ".join(str((ref or {}).get(k, "")) for k in ("name", "description", "prompt"))
    if "雨" in text:
        return "rain"
    if re.search(r"街|路口|外立面|广场|野外|山|海|室外|楼外", text):
        return "outdoor"
    return "room"


def _shaped_noise(n: int, seed: int, lo: float, hi: float, tilt: float) -> np.ndarray:
    """频域整形噪声：lo–hi 带通，tilt=-1 粉红、-2 褐色。"""
    spec = np.fft.rfft(np.random.default_rng(seed).standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    gain = np.where((f > lo) & (f < hi), 1.0, 0.0) * np.power(np.maximum(f, 20.0) / 1000.0, tilt / 2)
    x = np.fft.irfft(spec * gain, n)
    return (x / (np.max(np.abs(x)) + 1e-9)).astype(np.float32)


def synth_bed(preset: str, n: int, seed: int = 7) -> np.ndarray:
    """没有底噪素材时的兜底：雨 / 室外远噪 / 室内房间音。"""
    if n <= 0:
        return np.zeros(0, np.float32)
    if preset == "rain":
        x = _shaped_noise(n, seed, 300, 9000, -0.6)
        drops = np.random.default_rng(seed + 1).random(n) > 0.9995
        return x + np.convolve(drops.astype(np.float32), np.exp(-np.arange(240) / 40.0), "same") * 0.15
    if preset == "outdoor":
        return _shaped_noise(n, seed, 30, 1500, -1.6)
    t = np.arange(n) / SR
    hum = 0.02 * np.sin(2 * np.pi * 50 * t) + 0.01 * np.sin(2 * np.pi * 100 * t)
    return _shaped_noise(n, seed, 25, 600, -2.0) + hum.astype(np.float32)


def render_beds(timeline: list[ShotTiming], refs: list[dict], beds_dir: Path, n: int,
                xfade: float = 0.3) -> tuple[np.ndarray, list[dict]]:
    """按场景分段铺底噪，场景切换处交叉淡化。返回 (单声道, 用料清单)。"""
    by_id = {r["id"]: r for r in refs or []}
    spans: list[list] = []
    for t in timeline:
        if spans and spans[-1][0] == t.scene:
            spans[-1][2] = t.at + t.dur
        else:
            spans.append([t.scene, t.at, t.at + t.dur])
    if spans:
        spans[-1][2] = n / SR
    out = np.zeros(n, np.float32)
    used = []
    k = int(xfade * SR)
    for i, (scene, a, b) in enumerate(spans):
        i0, i1 = int(a * SR), min(n, int(b * SR) + (k if i < len(spans) - 1 else 0))
        length = i1 - i0
        src = find_asset(beds_dir, scene) if scene else None
        if src:
            x, origin = load_loop(src, length), f"素材 {src.name}"
        else:
            preset = bed_preset(by_id.get(scene))
            x, origin = synth_bed(preset, length, seed=i + 7), f"合成兜底（{preset}）"
        x = x / (rms(x) + 1e-9)
        if i > 0 and k:
            x[:k] *= np.linspace(0, 1, k)
        if i < len(spans) - 1 and k:
            x[-k:] *= np.linspace(1, 0, k)
        out[i0:i1] += x[:length]
        used.append({"scene": scene, "from": round(a, 2), "to": round(b, 2), "source": origin})
    return out, used


# ---------- 音效 ----------

SFX_RULES: list[tuple[str, str, list[tuple[float, float]]]] = [
    # (正则, 合成类型, [(相对偏移秒, 增益)])
    (r"敲门|叩门", "thud", []),                       # 次数从「三下」解析
    (r"落地|闷响|砸|摔|撞|跌", "thud", [(0.0, 0.8)]),
    (r"钥匙|叮铃|铜铃|铃铛", "chime", [(0.0, 0.6)]),
    (r"提示音|接单|叮咚|通知音", "pop", [(0.0, 0.7)]),
    (r"震", "tick", [(0.0, 0.6), (0.12, 0.6)]),
    (r"咔哒|开关|门锁|锁|门链|插销|按键", "tick", [(0.0, 0.8)]),
    (r"电流|通电|短路|滋啦", "glitch", [(0.0, 0.5)]),
    (r"数字滚动|跳秒|滴答|秒针", "tick", [(i * 0.12, 0.5) for i in range(6)]),
    (r"呼啸|掠过|甩过", "whoosh", [(0.0, 0.6)]),
    (r"冲击|重击|轰|爆炸", "hit", [(0.0, 0.9)]),
]
STOP_AFTER = re.compile(r"^.{0,2}(停|止|消失|不响|没了)")
END_ANCHOR = re.compile(r"黑场|同落|同时落|结尾|收尾")
COUNT = {"一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "几": 3}


def parse_sfx(text: str | None, dur: float, events: list[float]) -> list[dict]:
    """sfx 文字 → [{t, type, gain}]（t 相对镜头起点）。按分句排先后，第一个分句踩画面突变点。"""
    if not text:
        return []
    clauses = [c for c in re.split(r"[；;。，,]", text) if c.strip()]
    anchor_end = bool(END_ANCHOR.search(text))
    cues = []
    for ci, clause in enumerate(clauses):
        seen = set()
        for pattern, kind, hits in SFX_RULES:
            m = re.search(pattern, clause)
            if not m or kind in seen or STOP_AFTER.search(clause[m.end():]):
                continue
            seen.add(kind)
            if pattern.startswith("敲门"):
                cnt = re.search(r"([一两二三四几])\s*下", clause)
                hits = [(i * 0.32, 0.7) for i in range(COUNT.get(cnt.group(1), 3) if cnt else 3)]
            if anchor_end:
                base = max(0.0, dur - 0.05 - hits[-1][0])
            elif ci == 0 and events:
                base = events[0]
            else:
                base = min(dur * ci / max(1, len(clauses)) + 0.15, max(0.0, dur - 0.3))
            cues += [{"t": round(base + off, 3), "type": kind, "gain": g} for off, g in hits]
    return cues


KEY_BEAT = re.compile(r"反转|揭|翻盘|高潮|爽点|兑现")


def beat_cues(beats: list[dict], timeline: list[ShotTiming]) -> list[dict]:
    """关键节拍（反转/揭晓/高潮…）：起拍点放 riser 引入 + hit 落地；有画面突变就踩在突变上。"""
    cues = []
    for b in beats or []:
        if not KEY_BEAT.search(str(b.get("name", "")) + str(b.get("purpose", ""))[:6]):
            continue
        shots = [t for t in timeline if t.shot.get("beat") == b.get("name")]
        if not shots:
            continue
        hit = next((t.at + e for t in shots for e in t.events), shots[0].at)
        cues.append({"t": round(max(0.0, hit - 2.0), 3), "type": "riser", "gain": 0.5, "beat": b["name"]})
        cues.append({"t": round(hit, 3), "type": "hit", "gain": 0.8, "beat": b["name"]})
    return cues


def render_sfx(cues: list[dict], sfx_dir: Path, n: int) -> tuple[np.ndarray, list[dict]]:
    """同一类型用同一条声音（有 sound/sfx/<type>.wav 用素材，没有用合成），保证母题一致。"""
    out = np.zeros(n, np.float64)
    cache: dict[str, tuple[np.ndarray, str]] = {}
    for c in cues:
        if c["type"] not in cache:
            src = find_asset(sfx_dir, c["type"])
            cache[c["type"]] = ((read_audio(src).mean(1), f"素材 {src.name}") if src
                                else (studio.sfx(c["type"], seed=3), "合成"))
        clip, _ = cache[c["type"]]
        peak = np.max(np.abs(clip)) or 1.0
        studio.place(out, clip / peak * c.get("gain", 1.0), c["t"])
    used = [{**c, "source": cache[c["type"]][1]} for c in cues]
    return out.astype(np.float32), used


# ---------- BGM ----------

OFF_NOW = re.compile(r"^\s*无\s*$|^\s*无[，。（(]|抽掉|全静|骤停|静音|切断|无音乐|不要音乐")
HARD_OFF = re.compile(r"抽掉|骤停|切断")
STOP_END = re.compile(r"停\s*$|停[。，；]|淡出|收住")
RISE = re.compile(r"弦乐|上行|升|温暖|抒情|希望|明亮")
DRONE = re.compile(r"低频|低音|长音|压抑|悬疑|紧张|不安")


def music_mood(text: str) -> str:
    return "rise" if RISE.search(text) else "drone" if DRONE.search(text) else "pad"


def plan_music(timeline: list[ShotTiming]) -> list[dict]:
    """music 字段 → 情绪段落 [{mood, t0, t1, fade_in, fade_out}]。字段缺省时沿用上一镜。"""
    segs: list[dict] = []
    cur = None
    for t in timeline:
        text = str(t.shot.get("music") or "").strip()
        if text and OFF_NOW.search(text):
            if cur:
                cur["t1"], cur["fade_out"] = t.at, (0.03 if HARD_OFF.search(text) else 0.4)
                segs.append(cur)
            cur = None
            continue
        mood = music_mood(text) if text else (cur or {}).get("mood")
        if mood is None:
            continue
        if cur is None or cur["mood"] != mood:
            if cur:
                cur["t1"], cur["fade_out"] = t.at, 0.4
                segs.append(cur)
            cur = {"mood": mood, "t0": t.at, "fade_in": 0.8}
        cur["t1"] = t.at + t.dur
        if text and STOP_END.search(text):
            cur["fade_out"] = 0.4
            segs.append(cur)
            cur = None
    if cur:
        cur.setdefault("fade_out", 0.6)
        segs.append(cur)
    return [{**s, "t0": round(s["t0"], 3), "t1": round(s["t1"], 3)} for s in segs if s["t1"] > s["t0"]]


def synth_music(mood: str, n: int) -> np.ndarray:
    t = np.arange(n) / SR
    if mood == "drone":
        lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t)
        tone = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((55, 1.0), (82.4, 0.5), (110.3, 0.3)))
        return (tone * lfo + 0.3 * _shaped_noise(n, 11, 30, 200, -2)).astype(np.float32)
    if mood == "rise":
        glide = np.power(2, (t / max(t[-1], 1e-6)) / 12)          # 整段上行一个半音
        swell = 0.35 + 0.65 * (t / max(t[-1], 1e-6))
        phase = 2 * np.pi * np.cumsum(glide) / SR
        tone = sum(a * np.sin(phase * f) for f, a in ((220, 1.0), (329.6, 0.6), (440, 0.4), (554.4, 0.25)))
        return (tone * swell).astype(np.float32)
    return studio.pad([studio.midi_hz(57 + c) for c in (0, 3, 7)], n / SR)[:n].astype(np.float32)


def render_music(segs: list[dict], music_dir: Path, n: int) -> tuple[np.ndarray, list[dict]]:
    out = np.zeros(n, np.float32)
    used = []
    for s in segs:
        i0, i1 = int(s["t0"] * SR), min(n, int(s["t1"] * SR))
        length = i1 - i0
        if length <= 0:
            continue
        src = find_asset(music_dir, s["mood"])
        x = load_loop(src, length) if src else synth_music(s["mood"], length)
        x = x / (rms(x) + 1e-9)
        fi, fo = min(length // 2, int(s["fade_in"] * SR)), min(length // 2, int(s["fade_out"] * SR))
        if fi:
            x[:fi] *= np.linspace(0, 1, fi)
        if fo:
            x[-fo:] *= np.linspace(1, 0, fo)
        out[i0:i1] += x[:length]
        used.append({**s, "source": f"素材 {src.name}" if src else "合成 pad"})
    return out, used


# ---------- 混音 ----------

def duck_envelope(n: int, intervals: list[tuple[float, float]], depth_db: float = DUCK_DB,
                  ramp: float = 0.15) -> np.ndarray:
    """台词区间内降 depth_db，前后 ramp 秒线性过渡。"""
    g = np.ones(n, np.float32)
    low, k = undb(depth_db), int(ramp * SR)
    for a, b in intervals:
        i0, i1 = max(0, int(a * SR)), min(n, int(b * SR))
        if i1 <= i0:
            continue
        g[i0:i1] = np.minimum(g[i0:i1], low)
        if k:
            r0 = max(0, i0 - k)
            g[r0:i0] = np.minimum(g[r0:i0], np.linspace(1, low, i0 - r0))
            r1 = min(n, i1 + k)
            g[i1:r1] = np.minimum(g[i1:r1], np.linspace(low, 1, r1 - i1))
    return g


def fit(x: np.ndarray, n: int) -> np.ndarray:
    """补零或截断到 n 个样本（保持声道维度）。"""
    if len(x) >= n:
        return x[:n]
    pad = [(0, n - len(x))] + [(0, 0)] * (x.ndim - 1)
    return np.pad(x, pad)


def reference_db(dialog: np.ndarray, speech: list[tuple[float, float]]) -> float:
    parts = [dialog[int(a * SR):int(b * SR)] for a, b in speech]
    parts = [p for p in parts if p.size]
    level = rms(np.concatenate(parts)) if parts else rms(dialog)
    return db(level) if level > 1e-5 else FALLBACK_REF_DB


def mix(dialog: np.ndarray, bed: np.ndarray, music: np.ndarray, fx: np.ndarray,
        speech: list[tuple[float, float]], n: int) -> tuple[np.ndarray, dict]:
    """四层对齐到 n 个样本后按相对台词的电平混合。返回 (立体声, 电平信息)。"""
    dialog = fit(dialog.reshape(len(dialog), -1) if dialog.ndim == 1 else dialog, n)
    if dialog.shape[1] == 1:
        dialog = np.repeat(dialog, 2, axis=1)
    ref = reference_db(dialog, speech)
    bed, music, fx = fit(bed, n), fit(music, n), fit(fx, n)
    bed_g = undb(ref + BED_REL_DB) / (rms(bed[bed != 0]) + 1e-9) if np.any(bed) else 0.0
    active = music[np.abs(music) > 1e-6]
    mus_g = undb(ref + BGM_REL_DB) / (rms(active) + 1e-9) if active.size else 0.0
    fx_peak = np.max(np.abs(fx)) if np.any(fx) else 1.0
    fx_g = undb(ref + SFX_PEAK_REL_DB) / fx_peak
    duck = duck_envelope(n, speech)
    mono = bed * bed_g + music * mus_g * duck + fx * fx_g
    out = dialog + mono[:, None]
    return out.astype(np.float32), {"ref_db": round(ref, 1), "bed_db": round(ref + BED_REL_DB, 1),
                                     "bgm_db": round(ref + BGM_REL_DB, 1), "duck_db": DUCK_DB}


def loudnorm(src: Path, dst: Path, target: float = -16.0, tp: float = -1.5) -> dict:
    """两遍 loudnorm（先测再校），比单遍准。返回第一遍测得的数据。"""
    log = run(["ffmpeg", "-hide_banner", "-i", str(src), "-af",
               f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"])
    m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
    af = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", af, "-ar", str(SR), "-c:a", "pcm_s24le", str(dst)])
    return m
