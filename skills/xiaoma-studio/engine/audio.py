#!/usr/bin/env python3
"""xiaoma-studio 音频工具，只依赖 numpy + ffmpeg。

  python3 audio.py synth cues.json out.wav     按提示表合成配乐 + 卡点音效，响度归一到 -14 LUFS
  python3 audio.py analyze track.mp3 > beats.json   给现成音乐测 BPM、拍点、强弱段落

cues.json 示例：
{
  "bpm": 120, "duration": 15, "root": 45,
  "chords": [[0,3,7],[-4,0,3],[3,7,10],[-2,2,5]],   每小节一个和弦（相对 root 的半音）
  "layers": ["pad","bass","kick","hat","pluck"],      可选 pad/bass/kick/hat/pluck/clap
  "drop": 4.0, "breakdown": [10.0, 12.0],             drop 之前只有 pad；breakdown 区间去掉鼓
  "sfx": [{"t":0.0,"type":"whoosh"}, {"t":2.0,"type":"hit"}, {"t":3.5,"type":"pop"}]
}
sfx 类型：whoosh / hit / pop / tick / riser / swell / glitch / chime / thud
"""
import json
import subprocess
import sys
import wave

import numpy as np

SR = 48000


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    s_len = max(0, n - a - d - r)
    e = np.concatenate([np.linspace(0, 1, a, False), np.linspace(1, s, d, False), np.full(s_len, s), np.linspace(s, 0, r)])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def lowpass(x, cutoff):
    """一阶低通，cutoff 可以是标量或逐样本数组。装了 scipy 时标量走 lfilter 加速。"""
    if np.isscalar(cutoff):
        try:
            from scipy.signal import lfilter
            alpha = 1 - np.exp(-2 * np.pi * cutoff / SR)
            return lfilter([alpha], [1, alpha - 1], x)
        except ImportError:
            pass
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    alpha = 1 - np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += alpha[i] * (x[i] - acc)
        y[i] = acc
    return y


def saw(f, n, phase=0.0):
    t = np.arange(n) / SR
    return 2 * ((f * t + phase) % 1) - 1


def noise(n, seed):
    return np.random.default_rng(seed).uniform(-1, 1, n)


# ---------- 乐器 ----------
def kick(dur=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.95


def hat(seed, dur=0.06):
    n = int(dur * SR)
    x = np.diff(noise(n + 1, seed))
    return x * np.exp(-np.arange(n) / SR * 60) * 0.25


def clap(seed):
    n = int(0.25 * SR)
    x = lowpass(noise(n, seed), 3000) - lowpass(noise(n, seed), 600)
    t = np.arange(n) / SR
    return x * (np.exp(-t * 18) + 0.6 * np.exp(-((t - 0.012) % 0.011) * 300) * (t < 0.035)) * 0.8


def pad(freqs, dur):
    n = int(dur * SR)
    x = sum(saw(f * d, n, k * 0.13) for k, f in enumerate(freqs) for d in (0.997, 1.003))
    return lowpass(x / (len(freqs) * 2), 900) * env_adsr(n, 0.4, 0.3, 0.8, 0.6) * 0.5


def bass(f, dur):
    n = int(dur * SR)
    return lowpass(saw(f, n), 400) * env_adsr(n, 0.005, 0.15, 0.6, 0.05) * 0.7


def pluck(f, dur=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 14) * 0.3


# ---------- 音效 ----------
def sfx(kind, seed=0):
    t = lambda d: np.arange(int(d * SR)) / SR  # noqa: E731
    if kind == 'whoosh':
        x = t(0.6)
        cut = 300 + 5000 * np.sin(np.pi * x / 0.6) ** 2
        return lowpass(noise(len(x), seed), cut) * np.sin(np.pi * x / 0.6) ** 2 * 0.9
    if kind == 'hit':
        x = t(0.8)
        body = kick(0.8) * 1.0
        crack = lowpass(noise(len(x), seed), 6000) * np.exp(-x * 30) * 0.6
        return body + crack
    if kind == 'thud':
        return kick(0.5) * 0.8
    if kind == 'pop':
        x = t(0.12)
        f = 900 * np.exp(-x * 25) + 300
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 40) * 0.5
    if kind == 'tick':
        x = t(0.03)
        return np.sin(2 * np.pi * 3200 * x) * np.exp(-x * 200) * 0.35
    if kind == 'riser':
        x = t(2.0)
        cut = 200 + 7000 * (x / 2.0) ** 2
        return lowpass(noise(len(x), seed), cut) * (x / 2.0) ** 2 * 0.7
    if kind == 'swell':
        x = t(1.5)
        return sum(np.sin(2 * np.pi * f * x) for f in (220, 330, 440)) / 3 * np.sin(np.pi * x / 1.5) ** 2 * 0.35
    if kind == 'glitch':
        x = noise(int(0.15 * SR), seed)
        return np.sign(x) * (np.abs(x) > 0.6) * np.repeat(noise(16, seed + 1), len(x) // 16 + 1)[: len(x)] * 0.3
    if kind == 'chime':
        x = t(1.2)
        return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * k) for f, k in ((1318, 3), (1976, 4), (2637, 6))) / 3 * 0.4
    raise ValueError(f'未知音效类型 {kind}')


def place(buf, clip, at):
    i = int(at * SR)
    if i >= len(buf) or i + len(clip) <= 0:
        return
    j = min(len(buf), i + len(clip))
    buf[max(i, 0):j] += clip[max(0, -i): j - i]


def synth(cues):
    bpm, dur = cues['bpm'], cues['duration']
    beat = 60 / bpm
    root = cues.get('root', 45)
    chords = cues.get('chords', [[0, 3, 7], [-4, 0, 3], [3, 7, 10], [-2, 2, 5]])
    layers = set(cues.get('layers', ['pad', 'bass', 'kick', 'hat']))
    drop = cues.get('drop', 0)
    brk = cues.get('breakdown', [dur + 1, dur + 1])
    music = np.zeros(int((dur + 1) * SR))
    bar = beat * 4
    for b in range(int(np.ceil(dur / bar))):
        start = b * bar
        ch = chords[b % len(chords)]
        if 'pad' in layers:
            place(music, pad([midi_hz(root + 12 + c) for c in ch], bar + 0.5), start)
        drums = start >= drop and not (brk[0] <= start < brk[1])
        for k in range(4):
            tb = start + k * beat
            if tb >= dur:
                break
            in_brk = brk[0] <= tb < brk[1]
            if tb >= drop and not in_brk:
                if 'kick' in layers:
                    place(music, kick(), tb)
                if 'hat' in layers:
                    place(music, hat(b * 4 + k), tb + beat / 2)
                if 'clap' in layers and k in (1, 3):
                    place(music, clap(b * 4 + k), tb)
                if 'bass' in layers:
                    place(music, bass(midi_hz(root + ch[0]), beat * 0.9), tb)
            if 'pluck' in layers and (drums or in_brk):
                for s in range(2):
                    note = root + 24 + ch[(k * 2 + s) % len(ch)]
                    place(music, pluck(midi_hz(note)), tb + s * beat / 2)
    fx = np.zeros_like(music)
    for i, c in enumerate(cues.get('sfx', [])):
        place(fx, sfx(c['type'], i) * c.get('gain', 1.0), c['t'])
    mix = music * 0.8 + fx
    mix = mix[: int(dur * SR)]
    fade = int(0.05 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    return mix


def write_wav(path, mono):
    peak = np.max(np.abs(mono)) or 1
    st = np.stack([mono, mono], 1) / peak * 0.9
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype('<i2').tobytes())


def loudnorm(path, target=-14):
    tmp = path + '.tmp.wav'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', path, '-af', f'loudnorm=I={target}:TP=-1.0:LRA=11', '-ar', str(SR), tmp], check=True)
    subprocess.run(['mv', tmp, path], check=True)


def read_audio(path):
    raw = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', '22050', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32), 22050


def analyze(path):
    """能量谱通量测拍：BPM、首拍偏移、拍点列表、按响度分出的安静/高能段落。"""
    x, sr = read_audio(path)
    hop, win = 512, 2048
    frames = np.lib.stride_tricks.sliding_window_view(x, win)[::hop] * np.hanning(win)
    spec = np.abs(np.fft.rfft(frames, axis=1))
    flux = np.maximum(0, np.diff(np.log1p(spec), axis=0)).sum(1)
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    fps = sr / hop
    ac = np.correlate(flux, flux, 'full')[len(flux) - 1:]
    lags = np.arange(len(ac))
    bpms = 60 * fps / np.maximum(lags, 1)
    ok = (bpms >= 70) & (bpms <= 180)
    lag = lags[ok][np.argmax(ac[ok])]
    bpm = round(60 * fps / lag, 2)
    phases = [flux[p::lag].sum() for p in range(lag)]
    offset = int(np.argmax(phases)) / fps
    dur = len(x) / sr
    beats = [round(offset + i * 60 / bpm, 3) for i in range(int((dur - offset) / (60 / bpm)) + 1)]
    rms = np.sqrt(np.convolve(x ** 2, np.ones(sr) / sr, 'same'))[:: sr // 2]
    lo, hi = np.percentile(rms, 30), np.percentile(rms, 75)
    sections, cur, start = [], None, 0.0
    for i, v in enumerate(rms):
        lab = 'quiet' if v < lo else 'loud' if v > hi else 'mid'
        if lab != cur:
            if cur:
                sections.append({'label': cur, 'start': round(start, 2), 'end': round(i / 2, 2)})
            cur, start = lab, i / 2
    sections.append({'label': cur, 'start': round(start, 2), 'end': round(dur, 2)})
    sections = [s for s in sections if s['end'] - s['start'] >= 1.0]
    return {'bpm': bpm, 'offset': round(offset, 3), 'duration': round(dur, 2), 'beats': beats, 'sections': sections}


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] not in ('synth', 'analyze'):
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == 'synth':
        cues = json.load(open(sys.argv[2]))
        out = sys.argv[3] if len(sys.argv) > 3 else 'out/audio.wav'
        write_wav(out, synth(cues))
        loudnorm(out, cues.get('lufs', -14))
        print(f'写入 {out}（{cues["duration"]}s，{cues["bpm"]} BPM，{len(cues.get("sfx", []))} 个音效，-14 LUFS）')
    else:
        print(json.dumps(analyze(sys.argv[2]), ensure_ascii=False, indent=1))
