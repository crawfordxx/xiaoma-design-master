"""选入出点（纯函数，便于测试）。

规则：
- 片段内部自带切镜 → 只取一个镜头段：对白镜取含人声的那段，无台词镜取最长的非黑段
- 对白镜：整句说完才出点（前留 PRE、后留 POST），分镜时长不够就拉长，绝不切半句
- 无台词镜：严格按分镜时长；所在镜头段不够长就用满并标记
- 入出点不贴着画面突变（开灯、闪光），避免剪点旁留下 <0.3 秒的闪帧
"""
from __future__ import annotations

import numpy as np

from common import SR
from scenecut import Segment, avoid_slivers, choose_segment, overlap

HEAD_SKIP = 0.4   # 生成片段开头常是参考图静帧
PRE = 0.25        # 人声前留
POST = 0.35       # 人声后留


def plan_window(total: float, planned: float, has_line: bool, speech: tuple[float, float] | None,
                segs: list[Segment], events: list[float]) -> dict:
    """返回 {start, dur, segment, flags}。"""
    segs = segs or [Segment(0.0, total, False)]
    seg = choose_segment(segs, speech if has_line else None)
    flags: list[str] = []
    if len(segs) > 1:
        flags.append(f"片段内部有切点，取 {seg.start:.2f}–{seg.end:.2f}s 这一段")
    keep = None
    if has_line and speech:
        a, b = max(0.0, speech[0] - PRE), min(total, speech[1] + POST)
        bound = seg
        if overlap((seg.start, seg.end), speech) < speech[1] - speech[0] - 1e-3:
            bound = Segment(0.0, total, False)            # 台词跨了内部切点：保台词，报告
            flags.append("台词跨片段内部切点，为保整句没有避开，建议重出")
        dur = min(bound.dur, max(planned, b - a))
        start = min(max(bound.start, a), bound.end - dur)
        keep, seg = (speech[0], speech[1]), bound
    else:
        dur = min(planned, seg.dur)
        if seg.dur < planned - 1e-3:
            flags.append(f"可用镜头段只有 {seg.dur:.2f}s，短于分镜 {planned:.2f}s")
        start = seg.start + (HEAD_SKIP if seg.start == 0 else 0.0)
        start = max(seg.start, min(start, seg.end - dur))
    inner = [e for e in events if seg.start < e < seg.end]
    start, moved = avoid_slivers(start, dur, inner, seg, keep)
    if moved:
        flags.append("入出点避开了画面突变，防闪帧")
    if has_line and not speech:
        flags.append("对白镜没定位到人声，按分镜时长剪，检查是否切掉半句")
    return {"start": round(max(0.0, start), 3), "dur": round(dur, 3),
            "segment": [seg.start, seg.end], "flags": flags}


def energy_span(stereo: np.ndarray, sr: int = SR, hop: float = 0.03,
                rise_db: float = 10.0, min_voice_frac: float = 0.15) -> tuple[float, float] | None:
    """转写没认出台词时的兜底：人声频带（250–3500Hz）能量高于底噪 rise_db 的首尾时间。

    逐帧做 FFT（加汉宁窗）而不是整段一次 brick-wall 滤波：整段滤波时强低频（电机、
    雨声低频）会从滤波器边缘振铃漏进人声带，把没人说话的段落认成人声。
    再加一道「人声带能量占 40Hz 以上总能量的比例 ≥ min_voice_frac」，纯低频隆隆声过不了。
    """
    if stereo.size == 0:
        return None
    x = stereo.mean(1) if stereo.ndim == 2 else stereo
    win, step = max(64, int(2 * hop * sr)), max(1, int(hop * sr))
    idx = np.arange(0, len(x) - win + 1, step)
    if len(idx) < 4:
        return None
    power = np.abs(np.fft.rfft(np.stack([x[i:i + win] for i in idx]) * np.hanning(win), axis=1)) ** 2
    f = np.fft.rfftfreq(win, 1 / sr)
    voice = power[:, (f > 250) & (f < 3500)].sum(1)
    frac = voice / (power[:, f > 40].sum(1) + 1e-20)
    level = 10 * np.log10(voice + 1e-20)
    loud = np.where((level > np.percentile(level, 20) + rise_db) & (frac > min_voice_frac))[0]
    if len(loud) < max(2, int(0.15 / hop)):
        return None
    return round(float(idx[loud[0]] / sr), 2), round(float((idx[loud[-1]] + win) / sr), 2)
