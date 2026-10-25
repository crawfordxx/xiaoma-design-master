"""可选的本地语音转写：定位人声区间、成片台词自检。没装转写库时返回 None，由调用方降级。"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ASR_MODEL = os.environ.get("XIAOMA_ASR_MODEL", "mlx-community/whisper-large-v3-turbo")
# 无人声处转写模型常见的幻听套话
HALLUCINATION = ("字幕", "志愿者", "订阅", "点赞", "谢谢观看", "谢谢大家", "明镜", "请不吝")
CACHE_VER = "v3"
PUNCT = set("，。！？、：；“”‘’「」『』（）()《》…—-·,.!?:;\"' ～~")


def available() -> bool:
    try:
        import mlx_whisper  # noqa: F401
        return True
    except ImportError:
        return False


def _is_cjk(c: str) -> bool:
    return "\u4e00" <= c <= "\u9fff" or c.isdigit()


def clean_segments(segs: list[dict], duration: float | None = None) -> list[dict]:
    """过滤空段、过短段、单字、套话、复读和非中文乱码幻听；时间夹到素材时长内（模型会按 30 秒窗口报时）。"""
    out = []
    for s in segs:
        text = (s.get("text") or "").strip()
        start, end = float(s["start"]), float(s["end"])
        if duration is not None:
            if start >= duration - 0.05:
                continue
            end = min(end, duration)
        letters = [c for c in text if c.isalpha() or c.isdigit()]
        cjk = sum(_is_cjk(c) for c in letters)
        if cjk < 2 or cjk < 0.7 * len(letters) or end - start < 0.3:
            continue
        if any(h in text for h in HALLUCINATION) or "\ufffd" in text:
            continue
        # 复读（压缩比高）和低置信度段多是无人声处的幻听；nan 也一并丢掉
        if float(s.get("compression_ratio", 1.0)) > 2.4 or not float(s.get("avg_logprob", 0.0)) > -1.0:
            continue
        words = [(round(float(w["start"]), 2), round(min(float(w["end"]), end), 2))
                 for w in s.get("words") or [] if (w.get("word") or "").strip() and float(w["start"]) < end]
        out.append({"start": round(start, 2), "end": round(end, 2), "text": text, "words": words})
    return out


def transcribe(media: Path, cache_dir: Path | None = None) -> list[dict] | None:
    """返回清洗后的 [{start, end, text}]；没装转写库返回 None。按文件大小+修改时间缓存。"""
    if not available():
        return None
    cache = None
    if cache_dir:
        st = media.stat()
        cache = cache_dir / f"{media.stem}.{st.st_size}.{int(st.st_mtime)}.{CACHE_VER}.json"
        if cache.is_file():
            return json.loads(cache.read_text(encoding="utf-8"))
    import mlx_whisper
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(media), "-vn", "-ac", "1", "-ar", "16000",
                        str(wav)], check=True)
        r = mlx_whisper.transcribe(str(wav), path_or_hf_repo=ASR_MODEL, language="zh",
                                   condition_on_previous_text=False, word_timestamps=True)
        duration = wav.stat().st_size / 32000.0
    segs = clean_segments(r.get("segments", []), duration)
    if cache:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(segs, ensure_ascii=False), encoding="utf-8")
    return segs


def speech_span(segs: list[dict] | None) -> tuple[float, float] | None:
    """人声起止：优先词级时间戳（段级时间戳常从 0 秒算起，偏粗）。"""
    if not segs:
        return None
    words = [w for s in segs for w in s.get("words") or []]
    if words:
        return words[0][0], words[-1][1]
    return segs[0]["start"], segs[-1]["end"]


def chars(text: str) -> str:
    return "".join(c for c in text if c not in PUNCT and not c.isspace())


def coverage(expected: str, heard: str) -> float:
    """台词里的字有多少出现在转写里（按字计数，容忍语序与同音错字以外的差异）。"""
    exp = chars(expected)
    if not exp:
        return 1.0
    pool = list(chars(heard))
    hit = 0
    for c in exp:
        if c in pool:
            pool.remove(c)
            hit += 1
    return round(hit / len(exp), 2)
