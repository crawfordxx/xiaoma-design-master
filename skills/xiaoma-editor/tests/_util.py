"""测试公用：把 scripts/ 加进 sys.path，造假帧、假分镜、假时间线。

全部纯 numpy，不需要 ffmpeg、不需要转写库、不需要任何素材文件。
文件名以 `_` 开头，unittest discover 的 `test*.py` 不会把它当测试模块。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
for p in (str(SCRIPTS), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

from scenecut import SMALL_H, SMALL_W, Segment  # noqa: E402  路径就位后再导入

FPS = 30.0


def pattern(seed: int, n: int, lo: int = 40, hi: int = 100) -> np.ndarray:
    """n 帧完全相同的随机结构图（float32, n×36×64）。同图相邻帧相似度 = 1。"""
    base = np.random.default_rng(seed).integers(lo, hi, size=(SMALL_H, SMALL_W))
    return np.repeat(base[None], n, axis=0).astype(np.float32)


def black(n: int) -> np.ndarray:
    return np.zeros((n, SMALL_H, SMALL_W), np.float32)


def concat(*blocks: np.ndarray) -> np.ndarray:
    return np.concatenate(blocks, axis=0)


def brighten(frames: np.ndarray, factor: float) -> np.ndarray:
    """整体加亮：梯度结构不变，只改亮度。用来验证「开灯」不被当成切镜。"""
    return np.clip(frames * factor, 0, 255).astype(np.float32)


def ramp(frames: np.ndarray, lo: float = 0.6, hi: float = 1.8) -> np.ndarray:
    """逐帧乘性亮度渐变（缓慢曝光变化）。"""
    k = np.linspace(lo, hi, len(frames), dtype=np.float32)[:, None, None]
    return np.clip(frames * k, 0, 255).astype(np.float32)


def stereo(seconds: float, sr: int = 48000) -> np.ndarray:
    return np.zeros((int(seconds * sr), 2), np.float32)


def tone(seconds: float, freq: float = 1000.0, amp: float = 0.3, sr: int = 48000) -> np.ndarray:
    """(n, 2) 正弦，用来当假台词。"""
    t = np.arange(int(seconds * sr)) / sr
    x = (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    return np.stack([x, x], axis=1)


def shot(no: int, dur: float, **kw) -> dict:
    base = {"no": no, "duration_s": dur, "dialogue": "", "vo": "",
            "on_screen_text": "", "sfx": "", "music": "", "beat": ""}
    base.update(kw)
    return base


def storyboard(shots: list[dict], refs: list[dict] | None = None, **project) -> dict:
    return {"project": {"aspect": "9:16", **project}, "refs": refs or [],
            "strategy": {"beats": []}, "shots": shots}


def timing(no: int, at: float, dur: float, shot_dict: dict | None = None,
           scene: str | None = None, events: list[float] | None = None,
           speech: tuple[float, float] | None = None):
    from sound import ShotTiming
    return ShotTiming(no, at, dur, shot_dict or shot(no, dur), scene, events or [], speech)


def timeline(durs: list[float], per_shot: dict[int, dict] | None = None) -> list:
    """按每镜时长排出成片时间线。per_shot 是 {镜号: {字段: 值}}。

    写成位置参数而不是 `**per_shot`：镜号是整数，`**{1: ...}` 在 Python 里不合法。
    """
    out, at = [], 0.0
    for i, d in enumerate(durs, start=1):
        kw = (per_shot or {}).get(i) or {}
        out.append(timing(i, round(at, 3), d, shot(i, d, **kw), scene=kw.get("scene")))
        at += d
    return out


def missing_dir(tmp: Path, name: str = "no-assets") -> Path:
    """一个确定不存在的目录：find_asset 会返回 None，走合成兜底。"""
    return tmp / name / "definitely-not-here"


SEG = Segment
