from sbcommon import fmt_tc, timecodes
from validate import check, main

G = {'tvc'}


def errs(sb, **kw):
    return check(sb, genres=G, **kw)[0]


def warns(sb, genres=G):
    return check(sb, genres=genres)[1]


def test_timecodes_accumulate_durations():
    assert timecodes([{'duration_s': 2}, {'duration_s': 3.5}]) == [(0.0, 2.0), (2.0, 5.5)]


def test_fmt_tc():
    assert fmt_tc(3) == '00:03.0'
    assert fmt_tc(75.5) == '01:15.5'


def test_valid_storyboard_passes(sb):
    assert check(sb, genres=G) == ([], [])


def test_missing_shot_field(sb):
    sb['shots'][1]['purpose'] = ' '
    assert '第 2 镜 purpose 缺失' in errs(sb)


def test_unknown_genre(sb):
    sb['project']['genre'] = 'xx'
    assert any(e.startswith('project.genre 未知：xx') for e in errs(sb))


def test_bad_aspect(sb):
    sb['project']['aspect'] = '21:9'
    assert any(e.startswith('project.aspect 不支持：21:9') for e in errs(sb))


def test_shot_size_not_in_enum(sb):
    sb['shots'][0]['shot_size'] = '全景转特写'
    assert any('景别「全景转特写」不在枚举内' in e for e in errs(sb))


def test_shot_numbers_must_be_sequential(sb):
    sb['shots'][2]['no'] = 5
    assert '第 3 镜 镜号应为 3，实际是 5' in errs(sb)


def test_shot_durations_must_sum_to_total(sb):
    sb['shots'][2]['duration_s'] = 4
    assert '各镜时长之和 9s ≠ 总时长 10s' in errs(sb)


def test_beat_durations_must_sum_to_total(sb):
    sb['strategy']['beats'][1]['duration_s'] = 7
    assert '节拍时长之和 9s ≠ 总时长 10s' in errs(sb)


def test_speech_too_long_for_shot(sb):
    sb['shots'][0]['dialogue'] = '这是一句明显说不完的很长很长的台词'
    assert any(e.startswith('第 1 镜 台词和旁白共 17 字') for e in errs(sb))


def test_english_words_counted_by_syllable(sb):
    # 镜长 2s、上限 10 字：「上TikTok还是Amazon」= 3 汉字 + 2 + 3 音节 = 8，按字母算是 15
    sb['shots'][0]['vo'] = '上TikTok还是Amazon'
    assert not any('说不完' in e for e in errs(sb))


def test_speaker_names_not_counted_as_speech(sb):
    # 2.2 秒上限 11 字；连名字算是 12 字，去掉说话人名字是 7 字
    sb['shots'][0]['dialogue'] = '陆律师：林小姐请签字\n林夏：好'
    sb['shots'][0]['duration_s'] = 2.2
    sb['shots'][2]['duration_s'] = 4.8
    assert not any('台词和旁白' in e for e in errs(sb))


def test_extra_column_required(sb):
    sb['shots'][1]['extra'] = {}
    assert '第 2 镜 扩展列「卖点」未填' in errs(sb)


def test_unknown_ref(sb):
    sb['shots'][1]['refs'] = ['ghost']
    assert '第 2 镜 引用了不存在的设定「ghost」' in errs(sb)


def test_too_short_shot(sb):
    sb['shots'][0]['duration_s'] = 0.3
    sb['shots'][2]['duration_s'] = 6.7
    assert '第 1 镜 时长 0.3s 短于 0.5s' in errs(sb)


def test_non_numeric_duration(sb):
    sb['shots'][0]['duration_s'] = '2'
    assert '第 1 镜 duration_s 必须是数字' in errs(sb)


def test_long_shot_warns_except_documentary(sb):
    sb['project']['duration_s'] = 25
    sb['strategy']['beats'][1]['duration_s'] = 23
    sb['shots'][2]['duration_s'] = 20
    assert '第 3 镜 时长 20s 超过 15s' in warns(sb)
    sb['project']['genre'] = 'documentary'
    assert not any('超过 15s' in w for w in warns(sb, genres={'documentary'}))


def test_inner_monologue_warns(sb):
    sb['shots'][1]['visual'] = '女孩意识到自己迟到了'
    assert '第 2 镜 画面内容含拍不到的心理描写「意识到」' in warns(sb)


def test_three_identical_shots_warn(sb):
    for s in sb['shots']:
        s.update(shot_size='中景', angle='平视', movement='固定')
    assert '第 1–3 镜景别、角度、运镜完全相同' in warns(sb)


def test_frames_checked_when_base_dir_given(sb, tmp_path):
    sb['refs'][0]['image'] = 'frames/ref_hero.jpg'
    for i, s in enumerate(sb['shots'], 1):
        s['frame'] = f'frames/s{i:02d}.jpg'
    (tmp_path / 'frames').mkdir()
    for name in ['ref_hero.jpg', 's01.jpg', 's02.jpg']:
        (tmp_path / 'frames' / name).write_bytes(b'x')
    assert errs(sb, base_dir=tmp_path) == ['第 3 镜 分镜图不存在：frames/s03.jpg']


def test_main_returns_1_on_bad_json(tmp_path, capsys):
    p = tmp_path / 'storyboard.json'
    p.write_text('{oops', encoding='utf-8')
    assert main([str(p)]) == 1
    assert '读不了' in capsys.readouterr().out


# ---- 审查后补的健壮性用例 ----

def test_top_level_not_object():
    assert check([], genres=G) == (['顶层必须是对象（{…}）'], [])


def test_wrong_types_reported_not_raised(sb):
    sb['project']['genre'] = ['tvc']
    sb['shots'][1]['refs'] = 'hero'
    sb['shots'].append('oops')
    e = errs(sb)
    assert 'project.genre 必须是字符串' in e
    assert '第 2 镜 refs 必须是字符串列表' in e
    assert '第 4 镜必须是对象' in e


def test_ref_id_charset_and_uniqueness(sb):
    sb['refs'].append({**sb['refs'][0]})
    sb['refs'].append({**sb['refs'][0], 'id': '../evil'})
    e = errs(sb)
    assert '设定 id 重复：hero' in e
    assert any('id 只能用字母、数字、下划线和短横线' in x for x in e)


def test_nan_duration_rejected(sb):
    sb['shots'][0]['duration_s'] = float('nan')
    assert '第 1 镜 duration_s 必须是数字' in errs(sb)


def test_bool_shot_number_rejected(sb):
    sb['shots'][1]['no'] = True
    assert '第 2 镜 镜号必须是整数' in errs(sb)


def test_times_in_dialogue_not_mistaken_for_speaker(sb):
    sb['shots'][0]['dialogue'] = '我们约在10:30准时出发'   # 12 字，2 秒上限 10 字
    assert any(e.startswith('第 1 镜 台词和旁白共 12 字') for e in errs(sb))


def test_main_survives_wrong_types(tmp_path, capsys):
    p = tmp_path / 'storyboard.json'
    p.write_text('{"project": "x", "shots": "y"}', encoding='utf-8')
    assert main([str(p)]) == 1
    assert 'project 必须是对象' in capsys.readouterr().out


def test_main_reads_utf8_bom(sb, tmp_path):
    import json
    p = tmp_path / 'storyboard.json'
    p.write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8-sig')
    assert main([str(p)]) == 0


# ---- 导演审核新字段 ----

def test_tempo_must_be_known(sb):
    sb['shots'][0]['tempo'] = '超快'
    assert any('tempo 只能是' in e for e in errs(sb))


def test_project_asl_must_be_pair(sb):
    sb['project']['asl'] = [3, 2]
    assert 'project.asl 必须是 [下限, 上限] 两个数字且下限小于上限' in errs(sb)


def test_project_hook_must_be_non_negative_number(sb):
    for hook in (-1, '3', True, float('nan')):
        sb['project']['hook'] = hook
        assert 'project.hook 必须是不小于 0 的数字（秒，0 表示不查）' in errs(sb), hook
    for hook in (0, 3, 9.5):
        sb['project']['hook'] = hook
        assert errs(sb) == [], hook


def test_review_fields_checked(sb):
    sb['review'] = {'verdict': 'OK', 'issues': [{'shot': 1, 'severity': 'P9', 'status': 'done'}]}
    e = errs(sb)
    assert any(x.startswith('review.verdict 只能是') for x in e)
    assert any('severity 只能是' in x for x in e)
    assert any('status 只能是' in x for x in e)


def test_valid_review_passes(sb):
    sb['shots'][0]['tempo'] = '快切'
    sb['shots'][0]['pace_note'] = '开场冲击'
    sb['project']['asl'] = [1.5, 3]
    sb['review'] = {'verdict': 'APPROVE_WITH_NOTES', 'issues': [
        {'shot': 2, 'severity': 'P2', 'symptom': '略长', 'status': 'wontfix'}]}
    assert errs(sb) == []


def test_action_s_must_be_non_negative_number(sb):
    sb['shots'][0]['action_s'] = '3秒'
    assert '第 1 镜 action_s 必须是不小于 0 的数字' in errs(sb)
