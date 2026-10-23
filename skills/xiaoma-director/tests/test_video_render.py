import json

import video_render as vr
from conftest import BASE


def test_prompt_merges_style_size_movement_visual_and_sound(sb):
    p = vr.build_video_prompt(sb, sb['shots'][1])
    assert p.startswith('电影感写实')
    assert '中景' in p and '缓推' in p
    assert '女孩拿起咖啡瓶' in p
    assert '旁白:早上好' in p
    assert vr.NO_TEXT_SUFFIX in p


def test_prompt_appends_refs_descriptions(sb):
    sb['shots'][1]['refs'] = ['hero']
    p = vr.build_video_prompt(sb, sb['shots'][1])
    assert '设定:hero（咖啡瓶：一个玻璃咖啡瓶）' in p


def test_prompt_omits_empty_sound_segments(sb):
    p = vr.build_video_prompt(sb, sb['shots'][0])  # 无台词无旁白无音效
    assert '台词:' not in p and '旁白:' not in p and '音效:' not in p


def test_prompt_respects_allow_text(sb):
    sb['style']['allow_text'] = True
    sb['shots'][1]['on_screen_text'] = '「早安」'
    p = vr.build_video_prompt(sb, sb['shots'][1])
    assert vr.NO_TEXT_SUFFIX not in p


def test_plan_jobs_covers_all_shots_with_ratio_duration(sb):
    jobs = vr.plan_video_jobs(sb)
    assert [j['no'] for j in jobs] == [1, 2, 3]
    assert all(j['ratio'] == '16:9' for j in jobs)
    assert jobs[0]['duration'] == 2


def test_apply_results_writes_back_and_is_idempotent(sb, tmp_path):
    cfg = {'backend': 'chat', 'model': 'vid-1'}
    jobs = vr.plan_video_jobs(sb)
    results = {1: {'url': 'https://cdn/1.mp4'}, 2: {'url': 'https://cdn/2.mp4'}, 3: {'url': 'https://cdn/3.mp4'}}
    vr.apply_results(sb, jobs, results, backend_id='chat:vid-1')
    assert sb['shots'][0]['video']['url'] == 'https://cdn/1.mp4'
    assert sb['shots'][0]['video']['backend'] == 'chat:vid-1'
    # 幂等:同 backend 已有 url 的镜头不再重出
    assert vr.stale_shots(sb, backend_id='chat:vid-1') == []
    assert vr.stale_shots(sb, backend_id='chat:vid-2') == [1, 2, 3]


def test_cli_dry_run_writes_prompts_only(sb, tmp_path, capsys):
    d = tmp_path / 'sb'
    d.mkdir()
    (d / 'storyboard.json').write_text(json.dumps(BASE, ensure_ascii=False), encoding='utf-8')
    rc = vr.main([str(d / 'storyboard.json')])
    assert rc == 0
    out = json.loads((d / 'storyboard.json').read_text(encoding='utf-8'))
    assert out['shots'][0]['video']['prompt']
    assert 'url' not in out['shots'][0]['video'] or out['shots'][0]['video']['url'].startswith('dry-run')
