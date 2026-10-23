"""把分镜表逐镜生成视频片段：构造提示词 → 调 video_backends → 写回 storyboard.json。

用法：
  python3 video_render.py <dir>/storyboard.json            # 干跑（默认）：只写 shot.video.prompt
  python3 video_render.py <dir>/storyboard.json --live     # 真出片（需配置 VIDEO_*，见 README）
  python3 video_render.py <dir>/storyboard.json --live --shots 1,3   # 只重出指定镜头

写回字段（storyboard.json 每镜可选 video）：
  prompt   本镜视频提示词
  backend  出片签名（video_backends.backend_id），换模型自动重出
  url      视频地址；dry-run 时是 dry-run: 前缀摘要
  ts       出片时间
幂等：已有 url 且 backend 签名相同的镜头跳过。
"""
import json
import sys
import time

import video_backends
from frames import TEXT_OK, NO_TEXT
from sbcommon import write_json

NO_TEXT_SUFFIX = NO_TEXT  # 视频同图：画面里不要出现文字，字幕后期做


def _style(sb):
    return sb.get('style') or {}


def _refs_map(sb):
    return {r['id']: r for r in sb.get('refs') or []}


def _sound_line(shot):
    parts = []
    if shot.get('dialogue'):
        parts.append(f"台词:{shot['dialogue']}")
    if shot.get('vo'):
        parts.append(f"旁白:{shot['vo']}")
    if shot.get('sfx'):
        parts.append(f"音效:{shot['sfx']}")
    return parts


def build_video_prompt(sb, shot):
    """一镜 → 视频提示词：画风前缀 + 景别/角度/运镜 + 设定 + 画面 + 声音段 + 禁文字。"""
    lines = []
    prefix = _style(sb).get('prompt_prefix', '')
    if prefix:
        lines.append(prefix)
    camera = '、'.join(x for x in (shot.get('shot_size'), shot.get('angle'), shot.get('movement')) if x)
    if camera:
        lines.append(camera)
    refs = _refs_map(sb)
    ref_descs = [f"{rid}（{refs[rid].get('name', '')}：{refs[rid].get('prompt') or refs[rid].get('description', '')}）"
                 for rid in shot.get('refs') or [] if rid in refs]
    if ref_descs:
        lines.append('设定:' + ';'.join(ref_descs))
    body = shot.get('visual') or ''
    sound = _sound_line(shot)
    if sound:
        body = body + ' | ' + ' | '.join(sound)
    lines.append(body)
    text = '\n'.join(lines)
    allow = _style(sb).get('allow_text') and '「' in (shot.get('on_screen_text') or '')
    return text + '\n' + (TEXT_OK if allow else NO_TEXT_SUFFIX)


def plan_video_jobs(sb):
    """全部镜头 → 生成任务（镜号、提示词、画幅、时长、运镜）。"""
    aspect = sb['project'].get('aspect', '16:9')
    jobs = []
    for shot in sb['shots']:
        jobs.append({
            'no': shot['no'],
            'prompt': build_video_prompt(sb, shot),
            'ratio': aspect,
            'duration': shot.get('duration_s', 5),
            'movement': shot.get('movement'),
        })
    return jobs


def apply_results(sb, jobs, results, backend_id):
    """把生成结果写回 shot.video（时间戳统一取当前）。"""
    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    by_no = {j['no']: j for j in jobs}
    for shot in sb['shots']:
        if shot['no'] not in by_no:
            continue
        r = results.get(shot['no'])
        video = dict(shot.get('video') or {})
        video.update({'prompt': by_no[shot['no']]['prompt'], 'backend': backend_id, 'ts': now})
        if r:
            if r.get('url'):
                video['url'] = r['url']
            elif r.get('error'):
                video['error'] = r['error']
        shot['video'] = video


def stale_shots(sb, backend_id, only=None):
    """需要出片的镜号：没有 url、或 backend 签名变了、或在 only 列表里。"""
    stale = []
    for shot in sb['shots']:
        if only and shot['no'] not in only:
            continue
        video = shot.get('video') or {}
        if not video.get('url') or video.get('backend') != backend_id:
            stale.append(shot['no'])
    return stale


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    path = argv[0]
    live = '--live' in argv
    only = None
    if '--shots' in argv:
        i = argv.index('--shots')
        only = {int(x) for x in argv[i + 1].split(',') if x.strip()}
    import sbcommon
    sb = sbcommon.load_storyboard(path)
    env = dict(__import__('os').environ)
    if live:
        env['VIDEO_DRY_RUN'] = '0'
    cfg = video_backends.video_config(env)
    problem = video_backends.config_problem(cfg)
    if live and problem:
        print(f'✗ {problem}')
        return 1
    bid = ('dry:' if cfg['dry_run'] else '') + video_backends.backend_id(cfg)
    todos = stale_shots(sb, bid, only)
    if not todos:
        print('✓ 全部镜头已有视频，无需出片')
        return 0
    jobs = [j for j in plan_video_jobs(sb) if j['no'] in todos]
    results = {}
    for j in jobs:
        print(f"· 镜头 {j['no']}({'真出片' if live else '干跑'})…")
        results[j['no']] = video_backends.generate_video(
            j['prompt'], ratio=j['ratio'], duration=j['duration'], movement=j['movement'],
            cfg=cfg, env=env) if not cfg['dry_run'] else {'url': f'dry-run:{j["prompt"][:60]}'}
        if results[j['no']].get('error'):
            print(f"  ✗ 镜头 {j['no']}:{results[j['no']]['error']}")
    apply_results(sb, [x for x in plan_video_jobs(sb)], results, backend_id=bid)
    write_json(path, sb)
    ok = sum(1 for r in results.values() if r.get('url'))
    print(f'✓ {ok}/{len(jobs)} 镜头完成 → {path}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
