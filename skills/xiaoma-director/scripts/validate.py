#!/usr/bin/env python3
"""校验 storyboard.json：结构与类型、时长、景别、台词时长、扩展列、设定引用。

用法：python3 validate.py storyboard.json [--frames]
有 error 时退出码为 1；warning 只提示，不阻断。
"""
import argparse
import re
import sys
from pathlib import Path

from sbcommon import ASPECT_SIZES, SHOT_SIZES, TEMPOS, blank, genre_ids, is_num, load_storyboard, spoken_units

PROJECT_REQUIRED = ['title', 'genre', 'duration_s', 'aspect']
SHOT_REQUIRED = ['no', 'duration_s', 'shot_size', 'angle', 'movement', 'visual',
                 'transition', 'purpose', 'frame_prompt']
DICT_KEYS = ['project', 'strategy', 'style', 'post', 'review']
LIST_KEYS = ['shots', 'refs']
PROJECT_STR = ['title', 'genre', 'aspect', 'platform', 'audience', 'core_message', 'scope', 'segment_note']
REF_STR = ['type', 'name', 'description', 'prompt', 'image']
SHOT_STR = ['beat', 'shot_size', 'angle', 'movement', 'lens', 'visual', 'dialogue', 'vo', 'on_screen_text',
            'sfx', 'music', 'transition', 'purpose', 'notes', 'frame_prompt', 'frame', 'tempo', 'pace_note']
VERDICTS = ['APPROVE', 'APPROVE_WITH_NOTES', 'REVISE']
SEVERITIES = ['P0', 'P1', 'P2']
ISSUE_STATUS = ['fixed', 'open', 'wontfix']
ID_RE = re.compile(r'^[A-Za-z0-9_-]+$')   # 设定 id 会拼进文件名，只放行安全字符
CHARS_PER_SECOND = 5          # 中文口播语速上限
MIN_SHOT_S = 0.5
LONG_SHOT_S = 15
LONG_SHOT_OK = {'documentary', 'vlog'}
INNER_WORDS = ['意识到', '内心', '心想', '感到', '仿佛在说']
TOLERANCE = 0.05
# 行首或分隔符后的「说话人：」：只认全角冒号、名字不含数字和空白，免得把 10:30、3:2 当成说话人
SPEAKER = re.compile(r'(^|[\n／/；;])[ \t]*[^：:\n／/；;「」\d\s]{1,8}：')


def _not_str(d, k):
    return d.get(k) is not None and not isinstance(d.get(k), str)


def _not_str_list(v):
    return v is not None and not (isinstance(v, list) and all(isinstance(x, str) for x in v))


def _check_ref_types(refs):
    errors, seen = [], set()
    for i, r in enumerate(refs, 1):
        if not isinstance(r, dict):
            errors.append(f'第 {i} 个设定必须是对象')
            continue
        rid = r.get('id')
        if not isinstance(rid, str) or not ID_RE.match(rid):
            errors.append(f'第 {i} 个设定的 id 只能用字母、数字、下划线和短横线：{rid!r}')
        elif rid in seen:
            errors.append(f'设定 id 重复：{rid}')
        else:
            seen.add(rid)
        errors += [f'第 {i} 个设定的 {k} 必须是字符串' for k in REF_STR if _not_str(r, k)]
    return errors


def _check_shot_types(i, shot):
    if not isinstance(shot, dict):
        return [f'第 {i} 镜必须是对象']
    errors = [f'第 {i} 镜 {k} 必须是字符串' for k in SHOT_STR if _not_str(shot, k)]
    no = shot.get('no')
    if no is not None and (isinstance(no, bool) or not isinstance(no, int)):
        errors.append(f'第 {i} 镜 镜号必须是整数')
    if _not_str_list(shot.get('refs')):
        errors.append(f'第 {i} 镜 refs 必须是字符串列表')
    if shot.get('extra') is not None and not isinstance(shot.get('extra'), dict):
        errors.append(f'第 {i} 镜 extra 必须是对象')
    if shot.get('action_s') is not None and not (is_num(shot['action_s']) and shot['action_s'] >= 0):
        errors.append(f'第 {i} 镜 action_s 必须是不小于 0 的数字')
    return errors


def _check_review_types(review):
    """导演审片结论 review 的结构和枚举。"""
    errors = [] if review.get('verdict') in VERDICTS else [f"review.verdict 只能是 {'、'.join(VERDICTS)}"]
    issues = review.get('issues') or []
    if not (isinstance(issues, list) and all(isinstance(it, dict) for it in issues)):
        return errors + ['review.issues 必须是对象列表']
    for n, it in enumerate(issues, 1):
        if it.get('severity') not in SEVERITIES:
            errors.append(f"review 第 {n} 条意见 severity 只能是 {'、'.join(SEVERITIES)}")
        if it.get('status') not in ISSUE_STATUS:
            errors.append(f"review 第 {n} 条意见 status 只能是 {'、'.join(ISSUE_STATUS)}")
        shot = it.get('shot')
        if shot is not None and (isinstance(shot, bool) or not isinstance(shot, int)):
            errors.append(f'review 第 {n} 条意见 shot 必须是镜号（整数）或 null')
    return errors


def _bad_asl(asl):
    if asl is None:
        return False
    return not (isinstance(asl, list) and len(asl) == 2 and all(is_num(x) for x in asl) and 0 < asl[0] < asl[1])


def _check_types(sb):
    """结构或类型不对时后面的检查会崩，先在这里拦下；有错就不再往下查。"""
    if not isinstance(sb, dict):
        return ['顶层必须是对象（{…}）']
    errors = [f'{k} 必须是对象' for k in DICT_KEYS if k in sb and not isinstance(sb[k], dict)]
    errors += [f'{k} 必须是列表' for k in LIST_KEYS if k in sb and not isinstance(sb[k], list)]
    if errors:
        return errors
    project = sb.get('project') or {}
    errors += [f'project.{k} 必须是字符串' for k in PROJECT_STR if _not_str(project, k)]
    if _not_str_list(project.get('extra_columns')):
        errors.append('project.extra_columns 必须是字符串列表')
    if _bad_asl(project.get('asl')):
        errors.append('project.asl 必须是 [下限, 上限] 两个数字且下限小于上限')
    if 'hook' in project and not (is_num(project['hook']) and project['hook'] >= 0):
        errors.append('project.hook 必须是不小于 0 的数字（秒，0 表示不查）')
    if sb.get('review') is not None:
        errors += _check_review_types(sb['review'])
    beats = (sb.get('strategy') or {}).get('beats')
    if beats is not None and not (isinstance(beats, list) and all(isinstance(b, dict) for b in beats)):
        errors.append('strategy.beats 必须是对象列表')
    errors += _check_ref_types(sb.get('refs') or [])
    for i, shot in enumerate(sb.get('shots') or [], 1):
        errors += _check_shot_types(i, shot)
    return errors


def _speech_chars(shot):
    """台词和旁白里要念出来的字数（汉字、数字按个，英文按音节，不算标点和「林夏：」这类说话人前缀）。"""
    dialogue = SPEAKER.sub(r'\1', shot.get('dialogue') or '')
    return spoken_units(dialogue + (shot.get('vo') or ''))


def _check_project(project, genres):
    errors = [f'project.{k} 缺失' for k in PROJECT_REQUIRED if blank(project.get(k))]
    if project.get('genre') and project['genre'] not in genres:
        errors.append(f"project.genre 未知：{project['genre']}（可选：{'、'.join(sorted(genres))}）")
    if project.get('aspect') and project['aspect'] not in ASPECT_SIZES:
        errors.append(f"project.aspect 不支持：{project['aspect']}（可选：{'、'.join(ASPECT_SIZES)}）")
    if not blank(project.get('duration_s')) and not is_num(project.get('duration_s')):
        errors.append('project.duration_s 必须是数字')
    return errors


def _check_shot(i, shot, genre, extra_cols, ref_ids):
    tag = f'第 {i} 镜'
    errors = [f'{tag} {k} 缺失' for k in SHOT_REQUIRED if blank(shot.get(k))]
    warnings = []
    if shot.get('no') != i:
        errors.append(f"{tag} 镜号应为 {i}，实际是 {shot.get('no')}")
    if shot.get('shot_size') and shot['shot_size'] not in SHOT_SIZES:
        errors.append(f"{tag} 景别「{shot['shot_size']}」不在枚举内（{'、'.join(SHOT_SIZES)}）")
    if shot.get('tempo') and shot['tempo'] not in TEMPOS:
        errors.append(f"{tag} tempo 只能是 {'、'.join(TEMPOS)}，实际是「{shot['tempo']}」")
    d = shot.get('duration_s')
    if not blank(d) and not is_num(d):
        errors.append(f'{tag} duration_s 必须是数字')
    elif is_num(d):
        if d < MIN_SHOT_S:
            errors.append(f'{tag} 时长 {d}s 短于 {MIN_SHOT_S}s')
        if d > LONG_SHOT_S and genre not in LONG_SHOT_OK:
            warnings.append(f'{tag} 时长 {d}s 超过 {LONG_SHOT_S}s')
        n = _speech_chars(shot)
        if n > d * CHARS_PER_SECOND:
            errors.append(f'{tag} 台词和旁白共 {n} 字，{d}s 内说不完（上限 {int(d * CHARS_PER_SECOND)} 字）')
    for col in extra_cols:
        if blank((shot.get('extra') or {}).get(col)):
            errors.append(f'{tag} 扩展列「{col}」未填')
    for rid in shot.get('refs') or []:
        if rid not in ref_ids:
            errors.append(f'{tag} 引用了不存在的设定「{rid}」')
    for w in INNER_WORDS:
        if w in (shot.get('visual') or ''):
            warnings.append(f'{tag} 画面内容含拍不到的心理描写「{w}」')
    return errors, warnings


def _check_durations(sb, total):
    errors = []
    shot_sum = sum(s['duration_s'] for s in sb.get('shots') or [] if is_num(s.get('duration_s')))
    if abs(shot_sum - total) > TOLERANCE:
        errors.append(f'各镜时长之和 {shot_sum:g}s ≠ 总时长 {total:g}s')
    beats = (sb.get('strategy') or {}).get('beats') or []
    if beats:
        beat_sum = sum(b['duration_s'] for b in beats if is_num(b.get('duration_s')))
        if abs(beat_sum - total) > TOLERANCE:
            errors.append(f'节拍时长之和 {beat_sum:g}s ≠ 总时长 {total:g}s')
    return errors


def _check_repeats(shots):
    warnings = []
    for i in range(2, len(shots)):
        trio = [(s.get('shot_size'), s.get('angle'), s.get('movement')) for s in shots[i - 2:i + 1]]
        if trio[0] == trio[1] == trio[2]:
            warnings.append(f'第 {i - 1}–{i + 1} 镜景别、角度、运镜完全相同')
    return warnings


def _check_files(sb, base_dir):
    items = [(f"设定「{r.get('id')}」", r.get('image')) for r in sb.get('refs') or []]
    items += [(f'第 {i} 镜', s.get('frame')) for i, s in enumerate(sb.get('shots') or [], 1)]
    errors = []
    for tag, rel in items:
        if blank(rel):
            errors.append(f'{tag} 没有分镜图路径')
        elif not (Path(base_dir) / rel).is_file():
            errors.append(f'{tag} 分镜图不存在：{rel}')
    return errors


def check(sb, genres=None, base_dir=None):
    """返回 (errors, warnings)。base_dir 不为 None 时同时检查设定图和分镜图文件。"""
    type_errors = _check_types(sb)
    if type_errors:
        return type_errors, []
    genres = set(genre_ids() if genres is None else genres)
    project = sb.get('project') or {}
    shots = sb.get('shots') or []
    errors = _check_project(project, genres)
    warnings = []
    if not shots:
        errors.append('shots 为空')
    ref_ids = {r.get('id') for r in sb.get('refs') or []}
    extra_cols = project.get('extra_columns') or []
    for i, shot in enumerate(shots, 1):
        e, w = _check_shot(i, shot, project.get('genre'), extra_cols, ref_ids)
        errors += e
        warnings += w
    if is_num(project.get('duration_s')) and shots:
        errors += _check_durations(sb, project['duration_s'])
    warnings += _check_repeats(shots)
    if base_dir is not None:
        errors += _check_files(sb, base_dir)
    return errors, warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description='校验 storyboard.json')
    ap.add_argument('path', help='storyboard.json 路径')
    ap.add_argument('--frames', action='store_true', help='同时检查设定图和分镜图文件')
    a = ap.parse_args(argv)
    path = Path(a.path)
    try:
        sb = load_storyboard(path)
    except (OSError, ValueError) as e:   # ValueError 涵盖 JSON 解析错误和编码错误
        print(f'❌ 读不了 {path}：{e}')
        return 1
    errors, warnings = check(sb, base_dir=path.parent if a.frames else None)
    for w in warnings:
        print(f'⚠️  {w}')
    for e in errors:
        print(f'❌ {e}')
    if errors:
        print(f'未通过：{len(errors)} 个错误，{len(warnings)} 个提醒')
        return 1
    print(f"通过：{len(sb['shots'])} 镜，{len(warnings)} 个提醒")
    return 0


if __name__ == '__main__':
    sys.exit(main())
