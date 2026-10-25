"""剪辑技能公用：ffmpeg 调用、探测、字体探测、分镜读取、画幅。只依赖标准库 + numpy。"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np

SKILL_DIR = Path(__file__).resolve().parent.parent
FPS = 30
SR = 48000

# 画幅 → 输出分辨率（短边 720）
FRAME_SIZES = {
    "9:16": (720, 1280), "16:9": (1280, 720), "1:1": (720, 720),
    "4:3": (960, 720), "3:4": (720, 960), "2.39:1": (1280, 536),
}

# 中文字体候选：环境变量 > macOS > Linux 常见路径 > fc-list
FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
]


class EditorError(RuntimeError):
    """给用户看的明确错误（缺字体、缺 ffmpeg、缺分镜）。"""


def find_font(override: str | None = None) -> str:
    for cand in (override, os.environ.get("XIAOMA_FONT")):
        if cand:
            if Path(cand).is_file():
                return cand
            raise EditorError(f"指定的字体不存在: {cand}")
    for cand in FONT_CANDIDATES:
        if Path(cand).is_file():
            return cand
    if shutil.which("fc-list"):
        out = subprocess.run(["fc-list", ":lang=zh", "file"], capture_output=True, text=True).stdout
        files = [ln.split(":")[0].strip() for ln in out.splitlines() if ln.strip()]
        if files:
            return sorted(files)[0]
    raise EditorError("找不到中文字体。macOS 自带黑体/苹方；Linux 装 fonts-noto-cjk 或 fonts-wqy-microhei，"
                      "或用 --font / 环境变量 XIAOMA_FONT 指定 .ttf/.ttc 路径")


def require_ffmpeg() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise EditorError(f"没有 {tool}，先安装 ffmpeg")


def run(args: list[str]) -> str:
    """跑 ffmpeg 类命令，失败时把 stderr 尾巴抛出来。"""
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise EditorError(f"命令失败: {' '.join(args[:6])} …\n{r.stderr[-1500:]}")
    return r.stdout + r.stderr


def probe(path: Path) -> dict:
    """时长、宽高、帧率、有无音轨。"""
    out = run(["ffprobe", "-v", "error", "-show_entries",
               "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", str(path)])
    info = json.loads(out[out.find("{"):])
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    num, _, den = (v.get("r_frame_rate") or "0/1").partition("/")
    return {
        "duration": float(info.get("format", {}).get("duration") or 0),
        "width": int(v.get("width") or 0), "height": int(v.get("height") or 0),
        "fps": float(num) / float(den or 1) if float(den or 1) else 0.0,
        "has_audio": any(s.get("codec_type") == "audio" for s in info.get("streams", [])),
    }


def read_audio(path: Path, start: float = 0.0, dur: float | None = None, sr: int = SR) -> np.ndarray:
    """解码成 (n, 2) float32 立体声；没有音轨返回空数组。"""
    args = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", str(path)]
    if dur is not None:
        args += ["-t", f"{dur:.3f}"]
    args += ["-vn", "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"]
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        return np.zeros((0, 2), np.float32)
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()


def write_wav(path: Path, stereo: np.ndarray, sr: int = SR) -> None:
    """float (n, 2) → 24bit wav（经 ffmpeg，避免 16bit 截断精度）。"""
    data = np.clip(stereo, -1.0, 1.0).astype("<f4").tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", str(path)], input=data, check=True)


def load_storyboard(project_dir: Path, storyboard: Path | None = None) -> tuple[dict, Path]:
    """storyboard.json 默认在 <dir>/storyboard/storyboard.json，也接受 <dir>/storyboard.json。"""
    cands = [storyboard] if storyboard else [project_dir / "storyboard" / "storyboard.json",
                                             project_dir / "storyboard.json"]
    for c in cands:
        if c and c.is_file():
            return json.loads(c.read_text(encoding="utf-8")), c
    raise EditorError(f"找不到 storyboard.json（试过 {', '.join(str(c) for c in cands if c)}）")


def clip_path(project_dir: Path, no: int, clips_dir: Path | None = None) -> Path:
    return (clips_dir or project_dir / "clips") / f"s{no:02d}.mp4"


def frame_size(sb: dict) -> tuple[int, int]:
    aspect = str((sb.get("project") or {}).get("aspect", "9:16"))
    return FRAME_SIZES.get(aspect, FRAME_SIZES["9:16"])


def db(x: float) -> float:
    return 20 * np.log10(max(x, 1e-9))


def undb(d: float) -> float:
    return float(10 ** (d / 20))


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x)))) if x.size else 0.0
