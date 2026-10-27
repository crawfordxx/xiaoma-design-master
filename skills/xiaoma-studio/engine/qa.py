#!/usr/bin/env python3
"""成片体检：规格、音轨（48 kHz 立体声）、时长、响度、真峰值、单帧跳变（pop）、静止段（dead air）、画面边缘漏底（黑边）。

  python3 qa.py out/video.mp4 [--static 2.0] [--duration 10] [--ignore 0.1,3.5]

--duration：给了目标时长就检查成片是否正好这么长（误差不超过 1 帧）。
--ignore：故意的硬切 / 闪白时刻（秒，逗号分隔），前后 1 帧内的跳变不再报。

pop：某帧与前后差异是邻居中位数的 3 倍以上，通常是元素提前/延后一帧出现。
静止段：连续超过 N 秒几乎没变化，违反「每 2-4 秒必须有新东西」。
"""
import json
import re
import subprocess
import sys

import numpy as np


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,color_space,sample_rate,channels:format=duration', '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(path):
    """返回 (整体响度 LUFS, 真峰值 dBTP)，读不出来的项为 None。"""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-vn', '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], capture_output=True, text=True)

    def pick(key):
        m = re.search(rf'"{key}"\s*:\s*"(-?[\d.]+)"', r.stderr)
        return float(m.group(1)) if m else None
    return pick('input_i'), pick('input_tp')


def frame_diffs(path, w=160):
    info = probe(path)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    h = int(round(v['height'] * w / v['width'] / 2) * 2)
    num, den = map(int, v['r_frame_rate'].split('/'))
    raw = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', path, '-vf', f'scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    diff = np.abs(np.diff(frames, axis=0))
    return diff.mean((1, 2)), (diff > 4).mean((1, 2)), num / den


def edge_leaks(path, info, step=0.25):
    """每 step 秒取一帧，查四条边上有没有「整条暗且平」的带：底层素材平移、缩放后没铺满画布时就会漏出来。
    返回 [(秒, 边, 宽度 px)]。"""
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    w, h = int(v['width']), int(v['height'])
    raw = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', path, '-vf', f'fps={1 / step},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    out = []
    for k, f in enumerate(frames):
        for side, lines in (('右', f.T[::-1]), ('左', f.T), ('下', f[::-1]), ('上', f)):
            n = 0
            for line in lines[: max(w, h) // 8]:
                if (line < 30).mean() > 0.9:          # 九成以上像素都很暗：允许有细线、字幕压在漏底上
                    n += 1
                else:
                    break
            if n >= 4:
                out.append((round(k * step, 2), side, n))
    return out


def main():
    path = sys.argv[1]
    static_s = float(sys.argv[sys.argv.index('--static') + 1]) if '--static' in sys.argv else 2.0
    target = float(sys.argv[sys.argv.index('--duration') + 1]) if '--duration' in sys.argv else None
    ignore = [float(x) for x in sys.argv[sys.argv.index('--ignore') + 1].split(',')] if '--ignore' in sys.argv else []
    info = probe(path)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    a = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    print(f"规格  {v['width']}x{v['height']}  {v['r_frame_rate']}fps  {v['codec_name']}/{v['pix_fmt']}  {float(info['format']['duration']):.2f}s  音轨:{a['codec_name'] if a else '无'}")
    if a:
        sr, ch = int(a.get('sample_rate', 0)), int(a.get('channels', 0))
        flag = '' if sr == 48000 and ch == 2 else '  ← 规格要 48 kHz 立体声'
        print(f'音轨  {sr} Hz  {ch} 声道{flag}')
    if v.get('color_space') in (None, 'unknown'):
        print('色彩  未标注 → 播放器可能按 BT.601 解释，颜色偏移；用新版 render.mjs 重出（已默认标 BT.709）')
    d, changed, fps = frame_diffs(path)
    if target is not None:
        dur = float(info['format']['duration'])
        flag = '' if abs(dur - target) <= 1 / fps + 1e-3 else f'  ← 目标 {target:.3f}s，差了 {dur - target:+.3f}s'
        print(f'时长  {dur:.3f}s{flag}')
    if a:
        lufs, tp = loudness(path)
        flag = '' if lufs is not None and -16 <= lufs <= -12 else '  ← 建议 -14 LUFS'
        print(f'响度  {lufs} LUFS{flag}')
        flag = '' if tp is not None and tp <= -1 else '  ← 真峰值要 ≤ -1 dBTP，否则平台转码后会削波'
        print(f'真峰值 {tp} dBTP{flag}')
    pops = []
    for i in range(2, len(d) - 2):
        nb = np.median([d[i - 2], d[i - 1], d[i + 1], d[i + 2]])
        if d[i] > 6 and d[i] > 3 * max(nb, 0.5):
            pops.append(round((i + 1) / fps, 2))
    pops = [p for p in pops if not any(abs(p - x) <= 1.5 / fps for x in ignore)]
    print(f"单帧跳变 {len(pops)} 处" + (f": {pops[:20]}" if pops else '') + (f"（已忽略 {len(ignore)} 个标注为有意的时刻）" if ignore else ''))
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
    leaks = edge_leaks(path, info)
    if leaks:
        spans = {}
        for t, side, n in leaks:
            spans.setdefault(side, []).append((t, n))
        desc = '；'.join(f"{side}边 {v[0][0]}–{v[-1][0]}s 最宽 {max(n for _, n in v)}px" for side, v in spans.items())
        print(f"边缘漏底 {len(leaks)} 帧 ← {desc}（素材没铺满画布，放大或收小移动幅度；片头片尾的黑场是故意的就忽略）")
    else:
        print('边缘漏底 0 处')
    print('提示：跳变若是有意的硬切/闪白可忽略；静止段若是结尾定格可忽略。')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main()
