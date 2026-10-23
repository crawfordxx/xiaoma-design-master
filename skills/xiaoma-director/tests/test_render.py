import json

from render import collect, render_index, render_storyboard


def test_render_contains_every_shot_and_timecodes(sb, tmp_path):
    out = render_storyboard(sb, tmp_path)
    for s in sb['shots']:
        assert s['visual'] in out
    for tc in ['00:00.0', '00:02.0', '00:05.0', '00:10.0']:
        assert tc in out


def test_render_merges_sound_and_transition_columns(sb, tmp_path):
    out = render_storyboard(sb, tmp_path)
    assert '<th>声音 / 字幕</th>' in out and '<th>时间码 / 转场</th>' in out
    assert '<th>转场</th>' not in out and '<th>音效 / 音乐</th>' not in out
    assert '→ 叠化' in out


def test_render_shows_extra_columns(sb, tmp_path):
    out = render_storyboard(sb, tmp_path)
    assert '<th>卖点</th>' in out
    assert 'data-label="卖点">便携</td>' in out


def test_cells_carry_labels_for_narrow_layout(sb, tmp_path):
    out = render_storyboard(sb, tmp_path)
    for label in ['画面内容', '声音 / 字幕', '叙事目的', '备注']:
        assert f'data-label="{label}"' in out


def test_render_embeds_existing_frames(sb, tmp_path):
    (tmp_path / 'frames').mkdir()
    (tmp_path / 'frames' / 's01.jpg').write_bytes(b'\xff\xd8fake')
    sb['shots'][0]['frame'] = 'frames/s01.jpg'
    out = render_storyboard(sb, tmp_path)
    assert 'data:image/jpeg;base64,' in out
    assert out.count('未出图') == 3   # 第 2、3 镜和设定 hero 没图


def test_render_escapes_html(sb, tmp_path):
    sb['shots'][0]['visual'] = '<script>alert(1)</script>'
    out = render_storyboard(sb, tmp_path)
    assert '<script>alert(1)</script>' not in out
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in out


def test_index_links_each_sample(sb, tmp_path):
    for d in ['01-tvc', '02-brand-film']:
        (tmp_path / d).mkdir()
        (tmp_path / d / 'storyboard.json').write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    out = render_index(collect(tmp_path))
    assert 'href="01-tvc/storyboard.html"' in out
    assert 'href="02-brand-film/storyboard.html"' in out
    assert out.index('01-tvc') < out.index('02-brand-film')


# ---- 审查后补的用例 ----

def test_beat_flex_cannot_inject_attributes(sb, tmp_path):
    sb['strategy']['beats'][0]['duration_s'] = '1;x" onmouseover="alert(1)'
    out = render_storyboard(sb, tmp_path)
    assert 'onmouseover="alert(1)"' not in out


def test_embed_refuses_paths_outside_project(tmp_path):
    from render import embed
    (tmp_path / 'secret.txt').write_text('top secret')
    (tmp_path / 'proj').mkdir()
    assert embed(tmp_path / 'proj', '../secret.txt') == ''


def test_missing_duration_not_rendered_as_none(sb, tmp_path):
    del sb['project']['duration_s']
    assert 'Nones' not in render_storyboard(sb, tmp_path)


def test_main_rejects_invalid_storyboard(sb, tmp_path, capsys):
    from render import main
    sb['shots'][0]['shot_size'] = '全景转特写'
    p = tmp_path / 'storyboard.json'
    p.write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    assert main([str(p)]) == 1
    assert not (tmp_path / 'storyboard.html').exists()


def test_main_reports_unwritable_output(sb, tmp_path, capsys):
    from render import main
    p = tmp_path / 'storyboard.json'
    p.write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    assert main([str(p), '-o', str(tmp_path / 'nope' / 'x.html')]) == 1


def test_collect_skips_broken_sample(sb, tmp_path):
    (tmp_path / '01-ok').mkdir()
    (tmp_path / '01-ok' / 'storyboard.json').write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    (tmp_path / '02-bad').mkdir()
    (tmp_path / '02-bad' / 'storyboard.json').write_text('{oops', encoding='utf-8')
    assert [e['dir'] for e in collect(tmp_path)] == ['01-ok']


def test_index_shows_short_scope_label(sb, tmp_path):
    sb['project']['scope'] = 'segment'
    sb['project']['segment_note'] = '全片 180 秒，本分镜取开头 90 秒，负责立住主角和问题'
    (tmp_path / '01-x').mkdir()
    (tmp_path / '01-x' / 'storyboard.json').write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    out = render_index(collect(tmp_path))
    assert '节选' in out and '负责立住主角' not in out


# ---- 导演审核版块 ----

def test_review_section_shows_unreviewed_state(sb, tmp_path):
    out = render_storyboard(sb, tmp_path)
    assert '导演审核' in out and '未审片' in out


def test_review_section_shows_verdict_and_issues(sb, tmp_path):
    sb['review'] = {'verdict': 'APPROVE_WITH_NOTES', 'reviewer': '独立审片', 'summary': '整体顺',
                    'issues': [{'shot': 2, 'severity': 'P1', 'symptom': '旁白说完画面挂太久',
                                'fix': '缩到 2.5s', 'status': 'fixed'}]}
    out = render_storyboard(sb, tmp_path)
    assert '有备注通过' in out and '旁白说完画面挂太久' in out and '整体顺' in out


def test_pace_chart_has_one_bar_per_shot(sb, tmp_path):
    out = render_storyboard(sb, tmp_path)
    assert out.count('class="bar ') == len(sb['shots'])


def test_tight_shot_gets_badge_in_table(sb, tmp_path):
    sb['shots'][0]['shot_size'] = '大远景'   # 2 秒的大远景看不清
    out = render_storyboard(sb, tmp_path)
    assert 'class="pace st-tight"' in out


def test_index_card_shows_review_verdict(sb, tmp_path):
    sb['review'] = {'verdict': 'APPROVE_WITH_NOTES', 'issues': []}
    (tmp_path / '01-x').mkdir()
    (tmp_path / '01-x' / 'storyboard.json').write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    (tmp_path / '02-y').mkdir()
    del sb['review']
    (tmp_path / '02-y' / 'storyboard.json').write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    out = render_index(collect(tmp_path))
    assert '审片：有备注通过' in out and '审片：未审片' in out


# ---- 视频出片列（7b/7c 产物） ----

def test_no_video_column_when_no_shot_has_video(sb, tmp_path):
    out = render_storyboard(sb, tmp_path)
    assert '<th>出片</th>' not in out


def test_video_column_shows_link_and_qa_badge(sb, tmp_path):
    sb['shots'][0]['video'] = {'prompt': 'p', 'backend': 'task:vid', 'url': 'https://cdn/1.mp4', 'ts': 't',
                               'qa': {'total': 85.9, 'verdict': 'pass'}}
    out = render_storyboard(sb, tmp_path)
    assert '<th>出片</th>' in out
    assert 'href="https://cdn/1.mp4"' in out
    assert 'qa-pass' in out and '85.9' in out
    # 无视频的镜显示占位,不炸
    assert out.count('data-label="出片"') == 3


def test_video_repair_advice_renders_escaped(sb, tmp_path):
    sb['shots'][1]['video'] = {'prompt': 'p', 'backend': 'dry:chat:', 'url': 'dry-run:p',
                               'qa': {'total': 62.0, 'verdict': 'repair',
                                      'advice': '镜头 2 局部修改：<b>主体一致性</b>（拿原片加指令改）'}}
    out = render_storyboard(sb, tmp_path)
    assert 'qa-repair' in out
    assert '&lt;b&gt;主体一致性&lt;/b&gt;' in out


def test_dry_run_url_shows_prompt_ready_not_link(sb, tmp_path):
    sb['shots'][0]['video'] = {'prompt': 'p', 'backend': 'dry:chat:', 'url': 'dry-run:p'}
    out = render_storyboard(sb, tmp_path)
    assert '已备提示词' in out
    assert 'href="dry-run:' not in out


def test_video_error_renders(sb, tmp_path):
    sb['shots'][0]['video'] = {'prompt': 'p', 'backend': 'task:vid', 'error': '内容不合规'}
    out = render_storyboard(sb, tmp_path)
    assert '出片失败' in out and '内容不合规' in out
