#!/usr/bin/env python3
"""成片体检：规格、响度、单帧跳变（pop）、静止段（dead air）。

  python3 qa.py out/video.mp4 [--static 2.0]

pop：某帧与前后差异是邻居中位数的 3 倍以上，通常是元素提前/延后一帧出现。
静止段：连续超过 N 秒几乎没变化，违反「每 2-4 秒必须有新东西」。
"""
import json
import re
import subprocess
import sys

import numpy as np


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt:format=duration', '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-vn', '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    m = re.search(r'"input_i"\s*:\s*"(-?[\d.]+)"', r.stderr)
    return float(m.group(1)) if m else None


def frame_diffs(path, w=160):
    info = probe(path)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    h = int(round(v['height'] * w / v['width'] / 2) * 2)
    num, den = map(int, v['r_frame_rate'].split('/'))
    raw = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', path, '-vf', f'scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    diff = np.abs(np.diff(frames, axis=0))
    return diff.mean((1, 2)), (diff > 4).mean((1, 2)), num / den


def main():
    path = sys.argv[1]
    static_s = float(sys.argv[sys.argv.index('--static') + 1]) if '--static' in sys.argv else 2.0
    info = probe(path)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    a = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    print(f"规格  {v['width']}x{v['height']}  {v['r_frame_rate']}fps  {v['codec_name']}/{v['pix_fmt']}  {float(info['format']['duration']):.2f}s  音轨:{a['codec_name'] if a else '无'}")
    if a:
        lufs = loudness(path)
        flag = '' if lufs is not None and -16 <= lufs <= -12 else '  ← 建议 -14 LUFS'
        print(f'响度  {lufs} LUFS{flag}')
    d, changed, fps = frame_diffs(path)
    pops = []
    for i in range(2, len(d) - 2):
        nb = np.median([d[i - 2], d[i - 1], d[i + 1], d[i + 2]])
        if d[i] > 6 and d[i] > 3 * max(nb, 0.5):
            pops.append(round((i + 1) / fps, 2))
    print(f"单帧跳变 {len(pops)} 处" + (f": {pops[:20]}" if pops else ''))
    still = changed < 0.0005  # 变化像素不足 0.05%（160px 宽下约 7 个像素）
    runs, start = [], None
    for i, s in enumerate(np.append(still, False)):
        if s and start is None:
            start = i
        elif not s and start is not None:
            if (i - start) / fps >= static_s:
                runs.append((round(start / fps, 2), round(i / fps, 2)))
            start = None
    print(f"静止段(≥{static_s}s) {len(runs)} 处" + (f": {runs}" if runs else ''))
    print('提示：跳变若是有意的硬切/闪白可忽略；静止段若是结尾定格可忽略。')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main()
