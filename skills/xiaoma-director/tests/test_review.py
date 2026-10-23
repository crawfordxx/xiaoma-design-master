import json

import pytest

import review
from review import analyze, analyze_shot, speech_need, text_need, view_need

PROF = {'asl': (1.5, 3.0), 'cps': 4.0, 'slack': 1.0, 'hold': 3.5, 'hook': 3.0}


def shot(**kw):
    base = {'no': 1, 'duration_s': 2, 'shot_size': '中景', 'angle': '平视', 'movement': '固定',
            'dialogue': '', 'vo': '', 'on_screen_text': ''}
    return {**base, **kw}


# ---- 下限 ----

def test_speech_need_uses_gross_rate_without_extra_pauses():
    # 片种语速是含气口的毛语速：6 字 ÷ 4 = 1.5，标点不另加停顿；说话人名字不计
    assert speech_need(shot(dialogue='林夏：你好，我是林夏。'), 4) == pytest.approx(1.5)


def test_speech_need_adds_gap_when_speaker_changes():
    # 2 字 0.5 + 换人 0.3
    assert speech_need(shot(dialogue='甲：好。\n乙：走。'), 4) == pytest.approx(0.8)


def test_speech_need_counts_english_by_syllable():
    # 「做」1 + TikTok 2 + Shop 1 + AI 按字母 2 = 6 音节 ÷ 4 = 1.5
    assert speech_need(shot(vo='做TikTok Shop，AI'), 4) == pytest.approx(1.5)


def test_speech_need_zero_without_speech():
    assert speech_need(shot(), 4) == 0


def test_text_need_ignores_production_notes_in_brackets():
    assert text_need(shot(on_screen_text='0 糖（后期花字）')) == pytest.approx(2 / 9 + 0.5)


def test_view_need_by_shot_size_and_fast_cut():
    assert view_need(shot(shot_size='全景')) == 2.0
    assert view_need(shot(shot_size='全景', tempo='快切')) == 0.5


# ---- 单镜判定 ----

def test_tight_when_wide_shot_too_short():
    r = analyze_shot(shot(shot_size='全景', duration_s=1.5), PROF)
    assert r['status'] == '偏紧' and r['need_by'] == '看清画面'


def test_tight_when_dialogue_cannot_be_said():
    # 11 字 ÷ 4 = 2.75 秒，只给 2 秒
    r = analyze_shot(shot(dialogue='林夏：你好，我是林夏，今天来取钟。', duration_s=2), PROF)
    assert r['status'] == '偏紧' and r['need_by'] == '台词'


def test_draggy_when_dialogue_shot_hangs_too_long():
    r = analyze_shot(shot(dialogue='林夏：你好，我是林夏，今天来取钟。', duration_s=4), PROF)   # 下限 2.75 + 余量 1
    assert r['status'] == '拖沓'


def test_silent_static_shot_limited_by_hold():
    assert analyze_shot(shot(shot_size='特写', duration_s=4), PROF)['status'] == '拖沓'
    assert analyze_shot(shot(shot_size='特写', duration_s=3.5), PROF)['status'] == '合适'


def test_camera_movement_buys_slack_on_silent_shot():
    assert analyze_shot(shot(shot_size='特写', duration_s=4, movement='缓推'), PROF)['status'] == '合适'


def test_stay_tempo_adds_two_seconds():
    assert analyze_shot(shot(shot_size='特写', duration_s=5.5, tempo='停留'), PROF)['status'] == '合适'


def test_fast_cut_held_too_long_is_draggy():
    assert analyze_shot(shot(shot_size='特写', duration_s=1.5, tempo='快切'), PROF)['status'] == '拖沓'


def test_pace_note_marks_issue_as_explained():
    r = analyze_shot(shot(shot_size='全景', duration_s=1.5, pace_note='闪回，故意看不清'), PROF)
    assert r['status'] == '已说明' and r['reason']


def test_ok_shot_has_no_reason():
    r = analyze_shot(shot(shot_size='中景', duration_s=2), PROF)
    assert r['status'] == '合适' and r['reason'] == '' and r['fix'] == ''


# ---- 全片判定 ----

def _sb(durations, **project):
    shots = [shot(no=i, duration_s=d) for i, d in enumerate(durations, 1)]
    return {'project': {'genre': 'tvc', 'duration_s': sum(durations), **project},
            'strategy': {'beats': [{'name': '钩子', 'duration_s': durations[0]},
                                   {'name': '其余', 'duration_s': sum(durations[1:])}]},
            'shots': shots}


@pytest.fixture
def genres(tmp_path):
    (tmp_path / 'tvc.md').write_text('# TVC 广告\n\n```pace\nasl = 1.5-3\ncps = 4\nslack = 1\nhold = 3.5\nhook = 3\n```\n',
                                     encoding='utf-8')
    return tmp_path


def test_overall_too_slow(genres):
    notes = analyze(_sb([3.5, 3.4, 3.3, 3.2]), genres)['notes']
    assert any(n.startswith('整体偏慢') for n in notes)


def test_project_asl_overrides_genre(genres):
    a = analyze(_sb([3.5, 3.4, 3.3, 3.2], asl=[3, 4]), genres)
    assert a['asl'] == (3, 4) and not any('整体' in n for n in a['notes'])


def test_late_hook_flagged(genres):
    assert any('钩子' in n for n in analyze(_sb([2.5, 2, 2, 2.4]), genres)['notes']) is False
    assert any('钩子' in n for n in analyze(_sb([5, 2, 2, 2.4]), genres)['notes'])


def test_project_hook_overrides_genre(genres):
    # 长版放宽、竖屏短版收紧；0 表示不查
    assert not any('钩子' in n for n in analyze(_sb([5, 2, 2, 2.4], hook=6), genres)['notes'])
    assert any('2s 内' in n for n in analyze(_sb([2.5, 2, 2, 2.4], hook=2), genres)['notes'])
    a = analyze(_sb([9, 2, 2, 2.4], hook=0), genres)
    assert a['profile']['hook'] == 0 and not any('钩子' in n for n in a['notes'])


def test_uniform_rhythm_flagged(genres):
    notes = analyze(_sb([2, 2, 2, 3, 1.5, 2.5]), genres)['notes']
    assert any('第 1–4 镜时长雷同' in n for n in notes)


def test_late_hook_flagged(genres):
    notes = analyze(_sb([3.5, 2, 2.5, 1.5]), genres)['notes']
    assert any('钩子' in n for n in notes)


def test_main_exit_code_reflects_unresolved_issues(sb, tmp_path, capsys):
    sb['shots'][0]['shot_size'] = '大远景'   # 2 秒的大远景看不清
    p = tmp_path / 'storyboard.json'
    p.write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    assert review.main([str(p)]) == 1
    assert '偏紧' in capsys.readouterr().out
    sb['shots'][0]['pace_note'] = '开场闪一下，故意不让看清'
    for s in sb['shots'][1:]:
        s['pace_note'] = '测试'
    p.write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    assert review.main([str(p)]) == 0


def test_action_time_raises_need_and_avoids_false_drag():
    s = shot(dialogue='周太太：五十万，够你那裁缝铺开十年。', duration_s=4.5)   # 台词只需约 3.6s
    assert analyze_shot(s, PROF)['status'] == '拖沓'
    r = analyze_shot({**s, 'action_s': 4}, PROF)
    assert r['status'] == '合适' and r['need_by'] == '动作'


def test_action_time_can_make_shot_tight():
    r = analyze_shot(shot(duration_s=2, action_s=3), PROF)
    assert r['status'] == '偏紧' and r['need_by'] == '动作'


# ---- 代码审查后补的用例 ----

def test_tolerance_boundary_is_not_misjudged():
    assert analyze_shot(shot(shot_size='大特写', duration_s=0.7), PROF)['status'] == '合适'   # 需 0.8，差 0.1 在容差内


def test_silent_action_driven_shot_gets_slack_and_correct_reason():
    r = analyze_shot(shot(shot_size='特写', duration_s=8.8, action_s=8), PROF)
    assert r['status'] == '合适'          # 上限 = 8 + 余量 1
    r = analyze_shot(shot(shot_size='特写', duration_s=10, action_s=8), PROF)
    assert r['status'] == '拖沓' and '9.0s' in r['reason'] and '停留上限' not in r['reason']


def test_tight_action_suggests_trimming_action_not_lens():
    r = analyze_shot(shot(duration_s=2, action_s=3), PROF)
    assert '精简动作' in r['fix'] and '景别' not in r['fix']
