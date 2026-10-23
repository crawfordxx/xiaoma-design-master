"""xiaoma-director 各脚本共用的常量与小工具。"""
import json
import math
import os
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
GENRES_DIR = SKILL_DIR / 'genres'

# 一镜只能有一个主导景别，从远到近排列
SHOT_SIZES = ['大远景', '远景', '全景', '中全景', '中景', '中近景', '近景', '特写', '大特写']

# 画幅 → gpt-image-2 出图尺寸（两边须为 16 的倍数）
ASPECT_SIZES = {
    '16:9': '1536x864',
    '9:16': '864x1536',
    '1:1': '1024x1024',
    '4:3': '1280x960',
    '2.39:1': '1792x752',
}


# 镜头节奏意图：快切放宽看清画面的下限，停留放宽拖沓的上限
TEMPOS = ['快切', '正常', '停留']

# 片种卡没写节奏参数时的默认值：asl 平均镜长区间，cps 舒适语速（字/秒），slack 余量（秒），
# hold 无台词镜停留上限（秒），hook 钩子最晚结束（秒，0 不查）
DEFAULT_PACE = {'asl': (1.5, 6.0), 'cps': 4.0, 'slack': 1.5, 'hold': 6.0, 'hook': 0.0}
PACE_BLOCK = re.compile(r'```pace\n(.*?)```', re.S)


def _pace_value(key, raw):
    """解析一项节奏参数；数字不合理（非有限、非正、区间反了）返回 None，交给默认值。"""
    try:
        if key == 'asl':
            lo, hi = (float(x) for x in raw.replace('–', '-').split('-'))
            return (lo, hi) if math.isfinite(lo) and math.isfinite(hi) and 0 < lo < hi else None
        v = float(raw)
    except ValueError:
        return None
    ok = math.isfinite(v) and (v >= 0 if key == 'hook' else v > 0)
    return v if ok else None


def pace_profile(gid, genres_dir=GENRES_DIR):
    """片种卡「节奏审核参数」里 ```pace 代码块的参数；缺的或写坏的项用默认值。"""
    card = Path(genres_dir) / f'{gid}.md'
    m = PACE_BLOCK.search(card.read_text(encoding='utf-8')) if card.is_file() else None
    if not m:
        return dict(DEFAULT_PACE)
    pairs = [line.split('=', 1) for line in m.group(1).splitlines() if '=' in line]
    parsed = {k.strip(): _pace_value(k.strip(), v.strip()) for k, v in pairs if k.strip() in DEFAULT_PACE}
    return {**DEFAULT_PACE, **{k: v for k, v in parsed.items() if v is not None}}


def load_storyboard(path):
    # utf-8-sig：Windows 记事本存的 JSON 带 BOM
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, data):
    """先写临时文件再替换，写到一半被打断也不会截断原文件。"""
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip())


LATIN_WORD = re.compile(r'[A-Za-z]+')
VOWEL_GROUP = re.compile(r'[aeiouy]+', re.IGNORECASE)
ACRONYM_MAX = 5              # 不超过这么长的全大写词按字母念（AI、TVC）


def _syllables(word):
    if word.isupper() and len(word) <= ACRONYM_MAX:
        return len(word)
    return max(1, len(VOWEL_GROUP.findall(word)))


def spoken_units(text):
    """念出来大约几个音节：汉字、数字按个算，英文单词按音节估；按字母算会把 TikTok 当成 6 个字。"""
    words = LATIN_WORD.findall(text)
    rest = LATIN_WORD.sub('', text)
    return sum(1 for ch in rest if ch.isalnum()) + sum(_syllables(w) for w in words)


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def genre_ids(genres_dir=GENRES_DIR):
    return sorted(p.stem for p in Path(genres_dir).glob('*.md'))


def genre_name(gid, genres_dir=GENRES_DIR):
    """片种卡第一行「# 名称」里的名称；卡不存在时退回 id。"""
    card = Path(genres_dir) / f'{gid}.md'
    if card.is_file():
        lines = card.read_text(encoding='utf-8').lstrip().splitlines()
        if lines and lines[0].startswith('# '):
            return lines[0][2:].strip()
    return gid


def timecodes(shots):
    """按各镜 duration_s 累加，返回 [(start_s, end_s), ...]。"""
    spans, t = [], 0.0
    for shot in shots:
        d = float(shot['duration_s'])
        spans.append((t, t + d))
        t += d
    return spans


def fmt_tc(seconds):
    """秒 → mm:ss.f，例如 75.5 → 01:15.5。"""
    m, s = divmod(round(seconds, 1), 60)
    return f'{int(m):02d}:{s:04.1f}'
