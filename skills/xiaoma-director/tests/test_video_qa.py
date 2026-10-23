import video_qa as vq


def _scores(v):
    return {d: v for d in vq.DIMENSIONS}


def test_seven_dimensions():
    assert len(vq.DIMENSIONS) == 7
    assert '主体一致性' in vq.DIMENSIONS


def test_score_total_and_pass():
    r = vq.score(_scores(80))
    assert r['total'] == 80 and r['verdict'] == 'pass'


def test_boundary_equal_threshold_is_pass():
    assert vq.score(_scores(75))['verdict'] == 'pass'


def test_repair_band_and_fail():
    assert vq.score(_scores(70))['verdict'] == 'repair'
    assert vq.score(_scores(65))['verdict'] == 'repair'
    assert vq.score(_scores(50))['verdict'] == 'fail'


def test_score_rejects_missing_or_bad_dimension():
    bad = _scores(80)
    del bad['运镜']
    try:
        vq.score(bad)
        assert False, '缺维度应报错'
    except ValueError as e:
        assert '运镜' in str(e)
    bad2 = _scores(101)
    try:
        vq.score(bad2)
        assert False, '越界应报错'
    except ValueError as e:
        assert '构图' in str(e) or '101' in str(e)


def test_repair_advice_prefers_edit_over_rerender():
    shot = {'no': 3}
    edit = vq.repair_advice(shot, 'repair', ['主体一致性不足'])
    assert '镜头 3' in edit and '局部修改' in edit
    redo = vq.repair_advice(shot, 'fail', ['画面质量不足'])
    assert '重出' in redo and '局部修改' not in redo
    assert vq.repair_advice(shot, 'pass', []) is None
