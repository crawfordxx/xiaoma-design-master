"""镜头切分与剪点检查（纯 numpy）。

度量：相邻两帧「对数亮度梯度幅值」的相关系数。对数让乘性光照变化（灯亮、屏幕点亮）
变成加性，梯度只看结构，所以开灯、屏幕亮起不会被当成切镜；真硬切相关系数掉到 0.3 以下，
而且是孤立的一帧（运动模糊会连续几帧都低，不算切点）。
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np

SMALL_W, SMALL_H = 64, 36
CUT_SIM = 0.35        # 低于它且两侧邻帧明显更高 → 硬切
EVENT_SIM = 0.70      # 低于它的孤立跳变 → 画面突变（开灯、闪光），剪点不要贴着它
ISOLATION = 0.30      # 邻帧至少比它高这么多才算孤立
BLACK_PEAK = 24.0     # 第 99 百分位亮度（0–255）低于它算黑帧；只看均值会把暗夜戏当黑场
FLASH_S = 0.3         # 短于它的镜头段算闪帧
DUP_SIM = 0.80        # 剪点两侧相似度高于它 → 重复画面


def read_frames(path: Path, fps: float | None = None, start: float = 0.0,
                dur: float | None = None) -> tuple[np.ndarray, float]:
    """解码为 (n, H, W) 灰度小图。返回 (帧, 帧率)。"""
    args = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", str(path)]
    if dur is not None:
        args += ["-t", f"{dur:.3f}"]
    vf = f"scale={SMALL_W}:{SMALL_H}:flags=area"
    if fps:
        vf = f"fps={fps}," + vf
    args += ["-vf", vf, "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw = subprocess.run(args, capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, SMALL_H, SMALL_W).astype(np.float32)
    if fps is None:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=r_frame_rate", "-of", "csv=p=0", str(path)],
                             capture_output=True, text=True).stdout.strip()
        num, _, den = out.partition("/")
        fps = float(num) / float(den or 1) if out else 24.0
    return frames, float(fps)


def _edge_vectors(frames: np.ndarray) -> np.ndarray:
    lum = np.log1p(frames)
    gx = np.diff(lum, axis=2)[:, :-1, :]
    gy = np.diff(lum, axis=1)[:, :, :-1]
    mag = np.hypot(gx, gy).reshape(len(frames), -1)
    mag = mag - mag.mean(1, keepdims=True)
    return mag / (np.linalg.norm(mag, axis=1, keepdims=True) + 1e-9)


def similarity(a: np.ndarray, b: np.ndarray) -> float:
    """两帧结构相似度（-1..1）。"""
    ea, eb = _edge_vectors(np.stack([a, b]))
    return float((ea * eb).sum())


def adjacent_similarity(frames: np.ndarray) -> np.ndarray:
    """sim[i] = 第 i 帧与第 i+1 帧的相似度。黑帧之间记 1（黑场内部不算变化）。"""
    if len(frames) < 2:
        return np.ones(0)
    e = _edge_vectors(frames)
    sim = (e[:-1] * e[1:]).sum(1)
    black = black_mask(frames)
    sim[black[:-1] & black[1:]] = 1.0
    return sim


def black_mask(frames: np.ndarray) -> np.ndarray:
    return np.percentile(frames.reshape(len(frames), -1), 99, axis=1) < BLACK_PEAK


def _isolated_drops(sim: np.ndarray, below: float) -> list[int]:
    """返回孤立低点下标 i（切在第 i 帧与第 i+1 帧之间）。"""
    out = []
    for i, s in enumerate(sim):
        if s >= below:
            continue
        left = sim[i - 1] if i > 0 else 1.0
        right = sim[i + 1] if i + 1 < len(sim) else 1.0
        if min(left, right) - s >= ISOLATION:
            out.append(i)
    return out


def detect_cuts(frames: np.ndarray, fps: float) -> list[float]:
    """硬切时间点（秒，切点后第一帧的时间）。黑帧与非黑帧的交界也算切点。"""
    sim = adjacent_similarity(frames)
    idx = set(_isolated_drops(sim, CUT_SIM))
    black = black_mask(frames)
    idx |= {i for i in range(len(black) - 1) if black[i] != black[i + 1]}
    return [round((i + 1) / fps, 3) for i in sorted(idx)]


def detect_events(frames: np.ndarray, fps: float) -> list[float]:
    """画面突变（不到切镜程度的孤立跳变，如开灯）。"""
    sim = adjacent_similarity(frames)
    cuts = set(_isolated_drops(sim, CUT_SIM))
    return [round((i + 1) / fps, 3) for i in _isolated_drops(sim, EVENT_SIM) if i not in cuts]


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    black: bool

    @property
    def dur(self) -> float:
        return self.end - self.start


def segments(frames: np.ndarray, fps: float) -> list[Segment]:
    """按硬切把片段分成若干镜头段，标出整段黑场。"""
    total = len(frames) / fps
    bounds = [0.0] + detect_cuts(frames, fps) + [total]
    black = black_mask(frames)
    out = []
    for a, b in zip(bounds, bounds[1:]):
        if b - a <= 1e-6:
            continue
        ia, ib = int(round(a * fps)), max(int(round(a * fps)) + 1, int(round(b * fps)))
        out.append(Segment(round(a, 3), round(b, 3), bool(black[ia:ib].mean() > 0.5)))
    return out


def overlap(a: tuple[float, float], b: tuple[float, float]) -> float:
    return max(0.0, min(a[1], b[1]) - max(a[0], b[0]))


def choose_segment(segs: list[Segment], speech: tuple[float, float] | None) -> Segment:
    """有人声：取和人声重叠最多的镜头段；没有：取最长的非黑段。"""
    usable = [s for s in segs if not s.black] or segs
    if speech:
        best = max(usable, key=lambda s: (overlap((s.start, s.end), speech), s.dur))
        if overlap((best.start, best.end), speech) > 0:
            return best
    return max(usable, key=lambda s: s.dur)


def avoid_slivers(start: float, dur: float, events: list[float], seg: Segment,
                  keep: tuple[float, float] | None = None, min_s: float = FLASH_S) -> tuple[float, bool]:
    """入出点贴着画面突变（<min_s）会留下闪帧：把窗口挪开。

    优先把入点往前挪，让突变前至少留 min_s；挪不动再挪到突变之后。keep 是必须保住的人声区间。
    返回 (新入点, 是否挪过)。
    """
    def ok(s: float) -> bool:
        inside = seg.start - 1e-6 <= s and s + dur <= seg.end + 1e-6
        covers = keep is None or (s <= keep[0] + 1e-6 and s + dur >= keep[1] - 1e-6)
        return inside and covers

    for ev in events:
        head, tail = ev - start, start + dur - ev
        if 0 < head < min_s:
            for cand in (ev - min_s, ev):
                if ok(cand):
                    return round(cand, 3), True
        elif 0 < tail < min_s:
            for cand in (ev - dur, ev + min_s - dur):
                if ok(cand):
                    return round(cand, 3), True
    return start, False


# ---------- 成片检查 ----------

def film_shots(frames: np.ndarray, fps: float) -> list[dict]:
    return [{"start": s.start, "end": s.end, "dur": round(s.dur, 3), "black": s.black}
            for s in segments(frames, fps)]


def flashes(shots: list[dict], min_s: float = FLASH_S) -> list[dict]:
    """短于 min_s 的非黑镜头段（片尾黑场不算）。"""
    return [s for s in shots if s["dur"] < min_s and not s["black"]]


def duplicate_at_cuts(frames: np.ndarray, fps: float, cut_times: list[float],
                      window: float = 0.5, thresh: float = DUP_SIM) -> list[dict]:
    """剪点两侧各取 window 秒，任一对帧结构相似度超过 thresh → 重复画面。

    返回 [{at, sim}]；同机位对照这类有意的重复需要人工确认。
    """
    e = _edge_vectors(frames)
    black = black_mask(frames)
    k = max(1, int(round(window * fps)))
    out = []
    for t in cut_times:
        i = int(round(t * fps))
        left = [j for j in range(max(0, i - k), i) if not black[j]]
        right = [j for j in range(i, min(len(frames), i + k)) if not black[j]]
        if not left or not right:
            continue
        best = float((e[left] @ e[right].T).max())
        if best >= thresh:
            out.append({"at": round(t, 3), "sim": round(best, 3)})
    return out


def black_tail(frames: np.ndarray, fps: float) -> float:
    black = black_mask(frames)
    n = 0
    for b in black[::-1]:
        if not b:
            break
        n += 1
    return round(n / fps, 3)
