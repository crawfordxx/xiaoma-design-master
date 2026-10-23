from sbcommon import DEFAULT_PACE, pace_profile


def _card(tmp_path, body):
    (tmp_path / 'tvc.md').write_text(f'# TVC 广告\n\n## 节奏审核参数\n\n```pace\n{body}```\n', encoding='utf-8')
    return tmp_path


def test_pace_block_parsed(tmp_path):
    d = _card(tmp_path, 'asl = 1.5-3\ncps = 3.5\nslack = 1\nhold = 3.5\nhook = 3\n')
    assert pace_profile('tvc', d) == {'asl': (1.5, 3.0), 'cps': 3.5, 'slack': 1.0, 'hold': 3.5, 'hook': 3.0}


def test_missing_keys_and_bad_numbers_use_defaults(tmp_path):
    d = _card(tmp_path, 'cps = 4.5\nslack = 很多\n')
    prof = pace_profile('tvc', d)
    assert prof['cps'] == 4.5
    assert prof['slack'] == DEFAULT_PACE['slack']
    assert prof['asl'] == DEFAULT_PACE['asl']


def test_missing_card_uses_defaults(tmp_path):
    assert pace_profile('nope', tmp_path) == DEFAULT_PACE


def test_unreasonable_values_fall_back_to_defaults(tmp_path):
    d = _card(tmp_path, 'asl = 5-2\ncps = 0\nslack = nan\nhook = 0\n')
    prof = pace_profile('tvc', d)
    assert prof['asl'] == DEFAULT_PACE['asl'] and prof['cps'] == DEFAULT_PACE['cps']
    assert prof['slack'] == DEFAULT_PACE['slack'] and prof['hook'] == 0


def test_en_dash_range_accepted(tmp_path):
    assert pace_profile('tvc', _card(tmp_path, 'asl = 1.5–3\n'))['asl'] == (1.5, 3.0)


def test_every_genre_card_has_complete_pace_block():
    import re
    from sbcommon import GENRES_DIR, PACE_BLOCK, genre_ids
    for gid in genre_ids():
        block = PACE_BLOCK.search((GENRES_DIR / f'{gid}.md').read_text(encoding='utf-8'))
        assert block, gid
        keys = {line.split('=')[0].strip() for line in block.group(1).splitlines() if '=' in line}
        assert keys == set(DEFAULT_PACE), gid
