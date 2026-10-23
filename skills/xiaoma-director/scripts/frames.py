#!/usr/bin/env python3
"""按 storyboard.json 批量出分镜图；出图模型由环境变量配置，见 image_backends.py 和 README。

用法：python3 frames.py storyboard.json [--dry-run] [--only s03,ref_hero] [--force] [--workers 4]
先出设定图（refs），再出各镜；引用了设定的镜头带设定图走改图，其余走文生图。
已有图默认跳过；提示词、画幅或所挂设定变了的会自动重出；--only 指定的会重出；--force 全部重出。
"""
import argparse
import json
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from image_backends import (backend_id, command_image, config_problem, image_config, openai_image,
                            request_size)
from sbcommon import ASPECT_SIZES, load_storyboard, write_json
from validate import check

MAX_REFS = 4                  # 改图参考图上限
LONG_EDGE = 1280
JPEG_QUALITY = 82
RECORD = Path('frames') / '.prompts.json'   # 每张图生成时的签名，用来发现改过的分镜
NO_TEXT = '画面里不要出现任何文字、字幕、水印和边框'
TEXT_OK = '画面里不要出现水印和边框'
# 设定图按类型约束画面主体；画风前缀里常有「人物是画面主体」，不写明会把人画进产品图
REF_SUFFIX = {
    'character': '角色设定参考图，单人全身，主体完整清晰',
    'product': '产品设定参考图，只拍这件物品本身，画面里不要出现任何人物和手',
    'prop': '道具设定参考图，只拍这件物品本身，画面里不要出现任何人物和手',
    'location': '场景设定参考图，空镜，画面里不要出现任何人物',
}
REF_SUFFIX_DEFAULT = '设定参考图，主体完整清晰'


def _join(*parts):
    return '，'.join(p for p in parts if p)


def _style(sb):
    return sb.get('style') or {}


def _suffix(sb, text):
    """allow_text 只放行提示词里用「」标出的字；没标字时模型会自己编标题，所以仍禁止出字。"""
    return TEXT_OK if _style(sb).get('allow_text') and '「' in text else NO_TEXT


def shot_prompt(sb, shot):
    camera = f"景别：{shot['shot_size']}，角度：{shot['angle']}"
    return _join(_style(sb).get('prompt_prefix'), camera, shot['frame_prompt'], _suffix(sb, shot['frame_prompt']))


def ref_prompt(sb, ref):
    kind = REF_SUFFIX.get(ref.get('type'), REF_SUFFIX_DEFAULT)
    return _join(_style(sb).get('prompt_prefix'), ref['prompt'], kind, _suffix(sb, ref['prompt']))


def with_paths(sb):
    """返回按 id 和镜号重新推导 refs[].image 与 shots[].frame 的新字典，不改原对象。

    一律重算、不沿用 JSON 里的旧值：增删镜头后镜号会重排，旧路径会让两镜抢同一张图。
    """
    shots = [{**s, 'frame': f"frames/s{s['no']:02d}.jpg"} for s in sb.get('shots') or []]
    if 'refs' not in sb:
        return {**sb, 'shots': shots}
    refs = [{**r, 'image': f"frames/ref_{r['id']}.jpg"} for r in sb['refs']]
    return {**sb, 'refs': refs, 'shots': shots}


def load_record(base_dir):
    """读出图记录 {key: 签名}；没有或坏了就当空。"""
    try:
        return json.loads((Path(base_dir) / RECORD).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def save_record(base_dir, record):
    p = Path(base_dir) / RECORD
    p.parent.mkdir(parents=True, exist_ok=True)
    write_json(p, record)


def plan_jobs(sb, base_dir, only=None, force=False, record=None, cfg=None):
    """返回 (ref_jobs, shot_jobs)；sb 须已经过 with_paths。

    签名 = 模型 + 请求尺寸 + 提示词 + 所挂设定的提示词。图已存在但签名变了，说明分镜改过，要重出；
    没有记录的旧图视为有效。
    """
    record = record or {}
    cfg = cfg or image_config({})
    base = Path(base_dir)
    head = f"{backend_id(cfg)} {request_size(sb['project']['aspect'], cfg['sizes'])}"
    refs = sb.get('refs') or []
    ref_sig = {r['id']: ref_prompt(sb, r) for r in refs}

    def wanted(job):
        if only is not None:
            return job['key'] in only
        if force or not job['out'].is_file():
            return True
        return job['key'] in record and record[job['key']] != job['sig']

    def shot_job(s):
        ids = [r for r in (s.get('refs') or []) if r in ref_sig][:MAX_REFS]
        prompt = shot_prompt(sb, s)
        return {'key': f"s{s['no']:02d}", 'prompt': prompt, 'out': base / s['frame'],
                'refs': [base / f'frames/ref_{i}.jpg' for i in ids], 'ref_keys': [f'ref_{i}' for i in ids],
                'sig': '\n'.join([head, prompt, *(ref_sig[i] for i in ids)])}

    ref_jobs = [{'key': f"ref_{r['id']}", 'prompt': ref_sig[r['id']], 'out': base / r['image'], 'refs': [],
                 'ref_keys': [], 'sig': '\n'.join([head, ref_sig[r['id']]])} for r in refs]
    shot_jobs = [shot_job(s) for s in sb.get('shots') or []]
    return [j for j in ref_jobs if wanted(j)], [j for j in shot_jobs if wanted(j)]


def split_blocked(shot_jobs, ref_failures):
    """所挂设定图没出成功或不存在的镜头先不出：没参考图出出来会走样，还会被记成已带设定出过。

    返回 (可以出的镜头, {key: 原因})。
    """
    runnable, blocked = [], {}
    for job in shot_jobs:
        missing = [k for k, p in zip(job['ref_keys'], job['refs']) if k in ref_failures or not Path(p).is_file()]
        if missing:
            blocked[job['key']] = f"所挂设定图没出成功：{'、'.join(missing)}"
        else:
            runnable.append(job)
    return runnable, blocked


def crop_to_ratio(im, size):
    """按 size（宽x高）的比例居中裁切；比例已经对上就原样返回。"""
    w, h = (int(v) for v in size.split('x'))
    target = w / h
    width, height = im.size
    if abs(width / height - target) < 0.01:
        return im
    if width / height > target:          # 太宽，裁左右
        new_w = round(height * target)
        x = (width - new_w) // 2
        return im.crop((x, 0, x + new_w, height))
    new_h = round(width / target)        # 太高，裁上下
    y = (height - new_h) // 2
    return im.crop((0, y, width, y + new_h))


def to_jpeg(src, dst, size=None):
    """转成 JPG：上游偶尔不按请求尺寸出图（改图时常回 3:2），先按画幅裁正，再缩到长边 LONG_EDGE。"""
    from PIL import Image
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        rgb = im.convert('RGB')
    if size:
        rgb = crop_to_ratio(rgb, size)
    rgb.thumbnail((LONG_EDGE, LONG_EDGE))
    rgb.save(dst, 'JPEG', quality=JPEG_QUALITY, optimize=True)


def run_job(job, ctx):
    """出一张图；成功返回 None，失败返回错误信息。ctx 含 cfg、size（请求尺寸）、aspect、crop（画幅尺寸）。"""
    cfg = ctx['cfg']
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'out.png'
        err = (openai_image(job, ctx['size'], cfg, out) if cfg['backend'] == 'openai'
               else command_image(job, ctx['size'], ctx['aspect'], cfg, out))
        if err:
            return err
        files = sorted(Path(tmp).iterdir())   # 出图命令可能按真实格式改扩展名，不能写死文件名
        if not files:
            return '出图没有生成文件'
        to_jpeg(files[0], job['out'], ctx['crop'])
    return None


def run_all(jobs, ctx, workers, runner=run_job, on_done=None):
    """并发出图，返回 {key: 错误信息}；单张失败不影响其余。每成功一张就回调 on_done(job)。"""
    failures = {}
    if not jobs:
        return failures
    pool = ThreadPoolExecutor(max_workers=workers)
    futures = {pool.submit(runner, job, ctx): job for job in jobs}
    try:
        for fut in as_completed(futures):
            job = futures[fut]
            try:
                err = fut.result()
            except Exception as e:  # 单张图出错（含 PIL 解码失败）只记账，不中断整批
                err = repr(e)
            if err:
                failures[job['key']] = err
                print(f"❌ {job['key']}：{err}", flush=True)
            else:
                print(f"✅ {job['key']} → {job['out']}", flush=True)
                if on_done:
                    on_done(job)
    finally:
        pool.shutdown(cancel_futures=True)   # Ctrl-C 时不再发排队中的请求，免得继续扣费
    return failures


def _workers(v):
    n = int(v)
    if n < 1:
        raise argparse.ArgumentTypeError('并发数至少为 1')
    return n


def _preflight(cfg):
    """真正出图前的检查：出图配置齐全、Pillow 在。返回错误信息，没问题返回 None。"""
    problem = config_problem(cfg)
    if problem:
        return problem
    try:
        import PIL  # noqa: F401  出图后要靠它转 JPG，没装的话先付费的图会丢
    except ImportError:
        return '缺少 Pillow：先运行 pip install pillow'
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description='批量出分镜图（出图模型见 README「配置出图模型」）')
    ap.add_argument('path', help='storyboard.json 路径')
    ap.add_argument('--only', help='只重出这些，逗号分隔，如 s03,ref_hero')
    ap.add_argument('--force', action='store_true', help='全部重出')
    ap.add_argument('--workers', type=_workers, default=4, help='并发数')
    ap.add_argument('--dry-run', action='store_true', help='只列出要出的图和预估费用')
    a = ap.parse_args(argv)
    path, base = Path(a.path), Path(a.path).parent
    try:
        original = load_storyboard(path)
    except (OSError, ValueError) as e:
        print(f'❌ 读不了 {path}：{e}')
        return 1
    errors, _ = check(original)
    if errors:
        print('❌ 分镜没通过校验，先跑 validate.py 改好：')
        for e in errors[:10]:
            print(f'   {e}')
        return 1
    cfg = image_config(os.environ)
    sb = with_paths(original)
    only = {k.strip() for k in a.only.split(',') if k.strip()} if a.only else None
    record = load_record(base)
    ref_jobs, shot_jobs = plan_jobs(sb, base, only, a.force, record, cfg)
    n = len(ref_jobs) + len(shot_jobs)
    cost = f"，预估 {n * cfg['price']:.2f}" if cfg['price'] else ''
    print(f"待出图 {n} 张（设定 {len(ref_jobs)}，镜头 {len(shot_jobs)}；{backend_id(cfg)}）{cost}")
    if a.dry_run or n == 0:
        return 0
    problem = _preflight(cfg)
    if problem:
        print(f'❌ {problem}')
        return 1
    if sb != original:
        write_json(path, sb)

    def on_done(job):   # 每出一张就落盘记录，中途被打断也不会丢
        nonlocal record
        record = {**record, job['key']: job['sig']}
        save_record(base, record)

    aspect = sb['project']['aspect']
    ctx = {'cfg': cfg, 'size': request_size(aspect, cfg['sizes']), 'aspect': aspect, 'crop': ASPECT_SIZES[aspect]}
    ref_failures = run_all(ref_jobs, ctx, a.workers, on_done=on_done)
    runnable, blocked = split_blocked(shot_jobs, ref_failures)
    for key, why in blocked.items():
        print(f'⏸  {key}：{why}')
    failures = {**ref_failures, **blocked, **run_all(runnable, ctx, a.workers, on_done=on_done)}
    if failures:
        print(f"完成 {n - len(failures)}/{n}，未完成：{', '.join(failures)}；直接重跑会补出")
        return 1
    print(f'完成 {n}/{n}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
