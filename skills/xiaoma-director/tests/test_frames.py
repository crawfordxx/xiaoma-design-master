from PIL import Image

import frames
from frames import plan_jobs, run_all, shot_prompt, to_jpeg, with_paths


def test_shot_prompt_includes_prefix_size_and_no_text(sb):
    p = shot_prompt(sb, sb['shots'][0])
    assert p.startswith('电影感写实')
    assert '特写' in p and '冰块落进玻璃杯' in p
    assert frames.NO_TEXT in p


def test_allow_text_only_when_prompt_quotes_text(sb):
    sb['style']['allow_text'] = True
    sb['shots'][0]['frame_prompt'] = '屏幕中央写着「AI 原生」'
    p = shot_prompt(sb, sb['shots'][0])
    assert frames.TEXT_OK in p and frames.NO_TEXT not in p


def test_allow_text_without_quoted_text_still_forbids_text(sb):
    sb['style']['allow_text'] = True
    assert frames.NO_TEXT in shot_prompt(sb, sb['shots'][0])   # 冰块落进玻璃杯，没有「」


def test_product_ref_prompt_excludes_people(sb):
    # 画风前缀常带「人物是画面主体」，产品设定图会被画进一个人
    assert '不要出现任何人物' in frames.ref_prompt(sb, sb['refs'][0])


def test_character_ref_prompt_is_single_person(sb):
    ref = {'id': 'a', 'type': 'character', 'prompt': '26 岁女生'}
    assert '单人' in frames.ref_prompt(sb, ref)


def test_ref_prompt_forbids_text_unless_quoted(sb):
    sb['style']['allow_text'] = True
    assert frames.NO_TEXT in frames.ref_prompt(sb, sb['refs'][0])


def test_with_paths_fills_defaults_without_mutating(sb):
    out = with_paths(sb)
    assert out['shots'][1]['frame'] == 'frames/s02.jpg'
    assert out['refs'][0]['image'] == 'frames/ref_hero.jpg'
    assert 'frame' not in sb['shots'][1]


def test_with_paths_rederives_stale_paths_after_renumbering(sb):
    # 插镜头后镜号重排，JSON 里留着的旧路径会让两镜抢同一张图
    sb['shots'][1]['frame'] = 'frames/s01.jpg'
    sb['refs'][0]['image'] = 'frames/ref_old.jpg'
    out = with_paths(sb)
    assert [s['frame'] for s in out['shots']] == ['frames/s01.jpg', 'frames/s02.jpg', 'frames/s03.jpg']
    assert out['refs'][0]['image'] == 'frames/ref_hero.jpg'


def test_plan_jobs_skips_existing_and_attaches_refs(sb, tmp_path):
    sb = with_paths(sb)
    (tmp_path / 'frames').mkdir()
    (tmp_path / 'frames' / 's01.jpg').write_bytes(b'x')
    ref_jobs, shot_jobs = plan_jobs(sb, tmp_path)
    assert [j['key'] for j in ref_jobs] == ['ref_hero']
    assert [j['key'] for j in shot_jobs] == ['s02', 's03']
    assert shot_jobs[0]['refs'] == [tmp_path / 'frames' / 'ref_hero.jpg']


def test_plan_jobs_only_and_force(sb, tmp_path):
    sb = with_paths(sb)
    (tmp_path / 'frames').mkdir()
    (tmp_path / 'frames' / 's01.jpg').write_bytes(b'x')
    refs, shots = plan_jobs(sb, tmp_path, only={'s01'})
    assert refs == [] and [j['key'] for j in shots] == ['s01']
    refs, shots = plan_jobs(sb, tmp_path, force=True)
    assert len(refs) == 1 and len(shots) == 3


def _existing(sb, tmp_path):
    sb = with_paths(sb)
    (tmp_path / 'frames').mkdir()
    for name in ['ref_hero', 's01', 's02', 's03']:
        (tmp_path / 'frames' / f'{name}.jpg').write_bytes(b'x')
    return sb


def test_plan_jobs_redoes_frame_when_prompt_changed(sb, tmp_path):
    sb = _existing(sb, tmp_path)
    _, shots = plan_jobs(sb, tmp_path, force=True)
    record = {j['key']: j['sig'] for j in shots}
    sb['shots'][1]['frame_prompt'] = '女孩把咖啡瓶塞进包里'
    _, shots = plan_jobs(sb, tmp_path, record=record)
    assert [j['key'] for j in shots] == ['s02']


def test_plan_jobs_keeps_frames_without_record(sb, tmp_path):
    sb = _existing(sb, tmp_path)
    assert plan_jobs(sb, tmp_path, record={}) == ([], [])


def test_shot_redone_when_its_ref_prompt_changed(sb, tmp_path):
    sb = _existing(sb, tmp_path)
    refs, shots = plan_jobs(sb, tmp_path, force=True)
    record = {j['key']: j['sig'] for j in refs + shots}
    sb['refs'][0]['prompt'] = '一个陶瓷咖啡瓶'
    refs, shots = plan_jobs(sb, tmp_path, record=record)
    assert [j['key'] for j in refs] == ['ref_hero']
    assert [j['key'] for j in shots] == ['s02', 's03']   # s01 没挂设定


def test_record_round_trip(tmp_path):
    frames.save_record(tmp_path, {'s01': 'abc'})
    assert frames.load_record(tmp_path) == {'s01': 'abc'}
    assert frames.load_record(tmp_path / 'nowhere') == {}




def test_run_all_collects_failures(tmp_path):
    jobs = [{'key': 's01', 'out': tmp_path / 'a'}, {'key': 's02', 'out': tmp_path / 'b'}]

    def fake(job, size):
        return None if job['key'] == 's01' else '额度不足'

    assert run_all(jobs, '1024x1024', 2, runner=fake) == {'s02': '额度不足'}


def test_to_jpeg_crops_to_requested_ratio(tmp_path):
    src = tmp_path / 'wrong.png'
    Image.new('RGB', (1536, 1024), 'red').save(src)   # 上游回了 3:2
    to_jpeg(src, tmp_path / 'x.jpg', '1536x864')
    with Image.open(tmp_path / 'x.jpg') as im:
        assert im.size == (1280, 720)


def test_to_jpeg_crops_tall_image_for_vertical(tmp_path):
    src = tmp_path / 'wrong.png'
    Image.new('RGB', (1536, 1536), 'red').save(src)
    to_jpeg(src, tmp_path / 'x.jpg', '864x1536')
    with Image.open(tmp_path / 'x.jpg') as im:
        w, h = im.size
        assert h == 1280 and abs(w / h - 864 / 1536) < 0.01


def test_to_jpeg_downscales(tmp_path):
    src = tmp_path / 'big.png'
    Image.new('RGB', (1792, 752), 'red').save(src)
    to_jpeg(src, tmp_path / 'f' / 'x.jpg')
    with Image.open(tmp_path / 'f' / 'x.jpg') as im:
        assert max(im.size) == 1280 and im.format == 'JPEG'


# ---- 审查后补的用例 ----

def test_signature_changes_with_aspect(sb, tmp_path):
    sb = _existing(sb, tmp_path)
    refs, shots = plan_jobs(sb, tmp_path, force=True)
    record = {j['key']: j['sig'] for j in refs + shots}
    sb['project']['aspect'] = '9:16'
    refs, shots = plan_jobs(sb, tmp_path, record=record)
    assert len(refs) == 1 and len(shots) == 3


def test_shots_blocked_when_their_ref_failed_or_missing(sb, tmp_path):
    sb = with_paths(sb)
    _, shots = plan_jobs(sb, tmp_path, force=True)
    runnable, blocked = frames.split_blocked(shots, {'ref_hero'})
    assert [j['key'] for j in runnable] == ['s01']
    assert set(blocked) == {'s02', 's03'}
    runnable, blocked = frames.split_blocked(shots, set())   # 设定图文件根本不存在
    assert [j['key'] for j in runnable] == ['s01']


def test_run_all_reports_each_success(tmp_path):
    jobs = [{'key': 's01', 'out': tmp_path / 'a'}, {'key': 's02', 'out': tmp_path / 'b'}]
    done = []

    def fake(job, size):
        return None if job['key'] == 's01' else '失败'

    run_all(jobs, '1024x1024', 2, runner=fake, on_done=lambda j: done.append(j['key']))
    assert done == ['s01']




def test_with_paths_does_not_add_missing_refs_key(sb):
    del sb['refs']
    for s in sb['shots']:
        s['refs'] = []
    assert 'refs' not in with_paths(sb)


def test_main_rejects_invalid_storyboard(sb, tmp_path, capsys):
    import json
    sb['project']['aspect'] = '21:9'
    p = tmp_path / 'storyboard.json'
    p.write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    assert frames.main([str(p)]) == 1
    assert '不支持' in capsys.readouterr().out


# ---- 可配置的出图后端 ----

import base64
import json

import image_backends as ib


def test_image_config_defaults_and_env():
    c = ib.image_config({})
    assert (c['backend'], c['base'], c['model'], c['quality'], c['sizes']) == \
        ('openai', 'https://api.openai.com', 'gpt-image-1', 'low', 'standard')
    c = ib.image_config({'IMAGE_API_BASE': 'https://ai-api.kkidc.com/', 'IMAGE_API_KEY': 'k',
                             'IMAGE_MODEL': 'gpt-image-2', 'IMAGE_SIZES': 'exact', 'IMAGE_PRICE': '0.3'})
    assert (c['base'], c['key'], c['model'], c['sizes'], c['price']) == \
        ('https://ai-api.kkidc.com', 'k', 'gpt-image-2', 'exact', 0.3)
    assert ib.image_config({'OPENAI_API_KEY': 'o'})['key'] == 'o'


def test_request_size_standard_vs_exact():
    assert ib.request_size('16:9', 'standard') == '1536x1024'
    assert ib.request_size('2.39:1', 'standard') == '1536x1024'
    assert ib.request_size('9:16', 'standard') == '1024x1536'
    assert ib.request_size('16:9', 'exact') == '1536x864'


def test_config_problems():
    assert 'IMAGE_API_KEY' in ib.config_problem(ib.image_config({}))
    assert ib.config_problem(ib.image_config({'IMAGE_API_KEY': 'k'})) is None
    assert 'IMAGE_CMD' in ib.config_problem(ib.image_config({'IMAGE_BACKEND': 'command'}))
    ok = ib.image_config({'IMAGE_BACKEND': 'command', 'IMAGE_CMD': 'mj {prompt} {out}'})
    assert ib.config_problem(ok) is None
    assert '不支持' in ib.config_problem(ib.image_config({'IMAGE_BACKEND': 'dalle'}))


def test_build_command_substitutes_placeholders_without_shell(tmp_path):
    ref = tmp_path / 'ref.jpg'
    ref.write_bytes(b'x')
    job = {'prompt': '-一个女孩；rm -rf /', 'refs': [ref, tmp_path / 'missing.jpg']}
    args = ib.build_command('mj-gen --prompt {prompt} --ar {aspect} --refs {refs} -o {out}',
                                job, '1536x1024', '16:9', tmp_path / 'o.png')
    assert args == ['mj-gen', '--prompt', '-一个女孩；rm -rf /', '--ar', '16:9', '--refs', str(ref),
                    '-o', str(tmp_path / 'o.png')]


class FakeResp:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self.body


def _fake_api(monkeypatch, payload):
    calls = []

    def fake_urlopen(req, timeout):
        calls.append(req)
        return FakeResp(json.dumps(payload).encode())

    monkeypatch.setattr(ib.urllib.request, 'urlopen', fake_urlopen)
    return calls


def test_openai_generation_writes_b64_image(tmp_path, monkeypatch):
    calls = _fake_api(monkeypatch, {'data': [{'b64_json': base64.b64encode(b'PNGDATA').decode()}]})
    cfg = ib.image_config({'IMAGE_API_KEY': 'k'})
    assert ib.openai_image({'prompt': '女孩', 'refs': []}, '1536x1024', cfg, tmp_path / 'o.png') is None
    assert (tmp_path / 'o.png').read_bytes() == b'PNGDATA'
    assert calls[0].full_url == 'https://api.openai.com/v1/images/generations'
    body = json.loads(calls[0].data)
    assert (body['model'], body['size'], body['quality'], body['prompt']) == ('gpt-image-1', '1536x1024', 'low', '女孩')
    assert calls[0].get_header('Authorization') == 'Bearer k'


def test_openai_with_refs_uses_edits_multipart(tmp_path, monkeypatch):
    ref = tmp_path / 'ref.jpg'
    ref.write_bytes(b'JPGBYTES')
    calls = _fake_api(monkeypatch, {'data': [{'b64_json': base64.b64encode(b'X').decode()}]})
    cfg = ib.image_config({'IMAGE_API_KEY': 'k'})
    assert ib.openai_image({'prompt': '女孩', 'refs': [ref]}, '1536x1024', cfg, tmp_path / 'o.png') is None
    assert calls[0].full_url.endswith('/v1/images/edits')
    assert calls[0].get_header('Content-type').startswith('multipart/form-data; boundary=')
    assert b'JPGBYTES' in calls[0].data and b'name="image[]"' in calls[0].data
    assert '女孩'.encode() in calls[0].data


def test_openai_error_body_is_reported(tmp_path, monkeypatch):
    _fake_api(monkeypatch, {'error': {'message': 'quota exceeded'}})
    cfg = ib.image_config({'IMAGE_API_KEY': 'k'})
    err = ib.openai_image({'prompt': 'p', 'refs': []}, '1024x1024', cfg, tmp_path / 'o.png')
    assert 'quota exceeded' in err


def test_signature_includes_model(sb, tmp_path):
    sb = with_paths(sb)
    a = plan_jobs(sb, tmp_path, force=True, cfg=ib.image_config({'IMAGE_MODEL': 'gpt-image-1'}))[1]
    b = plan_jobs(sb, tmp_path, force=True, cfg=ib.image_config({'IMAGE_MODEL': 'gpt-image-2'}))[1]
    assert a[0]['sig'] != b[0]['sig']
