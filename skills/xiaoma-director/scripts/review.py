#!/usr/bin/env python3
"""节奏机检：按台词、字幕、景别和片种节奏参数，逐镜判断秒数偏紧还是拖沓。

用法：python3 review.py storyboard.json
所需下限 = max(看清画面, 念完台词, 读完字幕, 动作做完)；低于下限是偏紧，高于「下限 + 余量」是拖沓。
存在没写 pace_note 的偏紧或拖沓时退出码为 1。数字出处见 references/director-review.md。
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from sbcommon import GENRES_DIR, blank, genre_name, is_num, load_storyboard, pace_profile, spoken_units
from validate import SPEAKER, check

# 看清画面的最短时长（秒），景别越远信息越多
VIEW_MIN = {'大远景': 3.0, '远景': 2.5, '全景': 2.0, '中全景': 1.8, '中景': 1.5,
            '中近景': 1.2, '近景': 1.0, '特写': 1.0, '大特写': 0.8}
FAST_VIEW_MIN = 0.5          # 快切：0.3–0.5 秒能看清主体
SPEAKER_GAP = 0.3            # 换人说话的气口；同一人句中的气口已含在片种的毛语速里
TEXT_CPS = 9                 # 字幕阅读速度（Netflix 简中成人标准）
TEXT_SETTLE = 0.5            # 字幕出现到开始读的识别时间
FAST_SLACK = 0.5
STAY_EXTRA = 2.0             # 「停留」意图额外允许的秒数
PACE_TOLERANCE = 0.1
EPS = 1e-9                   # 浮点误差，0.8 - 0.1 = 0.7000000000000001
UNIFORM_WINDOW = 4
UNIFORM_SAME = 3             # 窗口里有这么多镜同长就算匀速
NOTE_IN_BRACKETS = re.compile(r'[（(][^）)]*[）)]')


def _chars(text):
    return sum(1 for ch in text if ch.isalnum())


def speech_need(shot, cps):
    """念完台词和旁白要的秒数：字数 ÷ 片种毛语速（含气口）+ 换人气口；没有台词返回 0。"""
    dialogue = shot.get('dialogue') or ''
    speakers = len(SPEAKER.findall(dialogue))
    text = SPEAKER.sub(r'\1', dialogue) + (shot.get('vo') or '')
    n = spoken_units(text)
    if n == 0:
        return 0.0
    return n / cps + max(speakers - 1, 0) * SPEAKER_GAP


def text_need(shot):
    """读完屏幕字幕、字卡要的秒数；括号里的制作说明不计。"""
    n = _chars(NOTE_IN_BRACKETS.sub('', shot.get('on_screen_text') or ''))
    return n / TEXT_CPS + TEXT_SETTLE if n else 0.0


def view_need(shot):
    if shot.get('tempo') == '快切':
        return FAST_VIEW_MIN
    return VIEW_MIN.get(shot.get('shot_size'), 1.0)


def _upper(shot, need, silent, prof):
    """拖沓的判定线。"""
    tempo = shot.get('tempo') or '正常'
    if tempo == '快切':
        return need + FAST_SLACK
    if silent:   # movement 不以「固定」开头就算有运镜，多给一份余量
        moving = not str(shot.get('movement') or '').startswith('固定')
        base = max(need + prof['slack'], prof['hold']) + (prof['slack'] if moving else 0)
    else:
        base = need + prof['slack']
    return base + (STAY_EXTRA if tempo == '停留' else 0)


def _verdict(shot, d, need, need_by, upper, silent, prof):
    if d < need - PACE_TOLERANCE - EPS:
        what = {'台词': '删减台词', '字幕': '删减字幕', '动作': '精简动作'}.get(need_by, '换更紧的景别或标「快切」')
        return '偏紧', f'{need_by}需 {need:.1f}s，只给了 {d:g}s', f'延长到 {need:.1f}s 以上，或{what}、拆镜'
    if d > upper + PACE_TOLERANCE + EPS:
        if shot.get('tempo') == '快切':
            why = f'标了快切却给了 {d:g}s'
        elif silent:
            why = f'无台词镜给了 {d:g}s，超过上限 {upper:.1f}s'
        else:
            why = f'{need_by}只需 {need:.1f}s，给了 {d:g}s，超出余量 {prof["slack"]:g}s'
        return '拖沓', why, f'缩到 {upper:.1f}s 以内；确需停留就标 tempo「停留」并写 pace_note'
    return '合适', '', ''


def analyze_shot(shot, prof):
    """单镜节奏判定：返回 no、duration、need、need_by、upper、status、reason、fix。"""
    d = float(shot['duration_s'])
    action = float(shot['action_s']) if is_num(shot.get('action_s')) else 0.0   # 动作做完、界面看清，由编导估算
    parts = {'台词': speech_need(shot, prof['cps']), '字幕': text_need(shot), '看清画面': view_need(shot),
             '动作': action}
    need_by, need = max(parts.items(), key=lambda kv: kv[1])
    silent = parts['台词'] == 0 and parts['字幕'] == 0
    upper = _upper(shot, need, silent, prof)
    status, reason, fix = _verdict(shot, d, need, need_by, upper, silent, prof)
    if status != '合适' and not blank(shot.get('pace_note')):
        status, reason, fix = '已说明', f"{reason}（已说明：{shot['pace_note']}）", ''
    return {'no': shot['no'], 'duration': d, 'need': round(need, 1), 'need_by': need_by,
            'upper': round(upper, 1), 'status': status, 'reason': reason, 'fix': fix}


def _uniform_ranges(durations):
    """连续 UNIFORM_WINDOW 镜里有 UNIFORM_SAME 镜同长的区段，相邻窗口合并，返回 [(起, 止)] 镜号。"""
    starts = [i for i in range(len(durations) - UNIFORM_WINDOW + 1)
              if Counter(durations[i:i + UNIFORM_WINDOW]).most_common(1)[0][1] >= UNIFORM_SAME]
    ranges = []
    for i in starts:
        if ranges and i <= ranges[-1][1]:
            ranges[-1] = (ranges[-1][0], i + UNIFORM_WINDOW)
        else:
            ranges.append((i + 1, i + UNIFORM_WINDOW))
    return ranges


def _notes(sb, durations, asl, prof):
    """全片级提醒：整体快慢、匀速、钩子。"""
    notes = []
    avg = sum(durations) / len(durations)
    lo, hi = asl
    if avg < lo * 0.9:
        notes.append(f'整体偏快：平均镜长 {avg:.1f}s，低于本片种 {lo:g}–{hi:g}s')
    elif avg > hi * 1.1:
        notes.append(f'整体偏慢：平均镜长 {avg:.1f}s，高于本片种 {lo:g}–{hi:g}s')
    notes += [f'第 {a}–{b} 镜时长雷同，节奏匀速，考虑拉开长短' for a, b in _uniform_ranges(durations)]
    if len(durations) >= 6 and len(set(durations)) < 3:
        notes.append(f'全片只用了 {len(set(durations))} 种镜长，缺少快慢变化')
    beats = (sb.get('strategy') or {}).get('beats') or []
    first = beats[0].get('duration_s') if beats else None
    if prof['hook'] and is_num(first) and first > prof['hook']:
        notes.append(f"开头节拍「{beats[0].get('name')}」到 {first:g}s 才结束，本片种要求钩子在 {prof['hook']:g}s 内")
    return notes


def analyze(sb, genres_dir=None):
    """整份分镜的节奏机检；sb 须已通过 validate.check。"""
    project = sb['project']
    prof = pace_profile(project['genre'], genres_dir or GENRES_DIR)
    if 'hook' in project:   # 子类型（长版、竖屏短版）的钩子时限；0 表示不查
        prof = {**prof, 'hook': float(project['hook'])}
    asl = tuple(project['asl']) if project.get('asl') else prof['asl']
    shots = [analyze_shot(s, prof) for s in sb['shots']]
    durations = [s['duration'] for s in shots]
    return {'profile': prof, 'asl': asl, 'avg': round(sum(durations) / len(durations), 2),
            'shots': shots, 'notes': _notes(sb, durations, asl, prof)}


def _print_report(sb, a):
    counts = Counter(s['status'] for s in a['shots'])
    lo, hi = a['asl']
    print(f"节奏机检 · {genre_name(sb['project']['genre'])} · {len(a['shots'])} 镜 · "
          f"平均镜长 {a['avg']:g}s（区间 {lo:g}–{hi:g}s）")
    print(' · '.join(f'{k} {counts.get(k, 0)}' for k in ['合适', '偏紧', '拖沓', '已说明']))
    for s in a['shots']:
        if s['status'] in ('偏紧', '拖沓'):
            print(f"❌ 第 {s['no']} 镜 {s['status']}：{s['reason']} → {s['fix']}")
    for n in a['notes']:
        print(f'⚠️  {n}')
    rv = sb.get('review')
    if rv:
        still_open = sum(1 for it in rv.get('issues') or [] if it.get('status') == 'open')
        print(f"导演审片：{rv['verdict']}（{len(rv.get('issues') or [])} 条意见，{still_open} 条未关闭）")


def main(argv=None):
    ap = argparse.ArgumentParser(description='分镜节奏机检')
    ap.add_argument('path', help='storyboard.json 路径')
    a = ap.parse_args(argv)
    path = Path(a.path)
    try:
        sb = load_storyboard(path)
    except (OSError, ValueError) as e:
        print(f'❌ 读不了 {path}：{e}')
        return 1
    errors, _ = check(sb)
    if errors:
        print('❌ 分镜没通过校验，先跑 validate.py 改好：')
        for e in errors[:10]:
            print(f'   {e}')
        return 1
    result = analyze(sb)
    _print_report(sb, result)
    unresolved = sum(1 for s in result['shots'] if s['status'] in ('偏紧', '拖沓'))
    if unresolved:
        print(f'未处理 {unresolved} 处：改秒数、删字、拆镜，或写 pace_note 说明意图')
        return 1
    print('通过：没有未处理的偏紧或拖沓')
    return 0


if __name__ == '__main__':
    sys.exit(main())
