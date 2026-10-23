import video_backends as vb


def _cfg(**over):
    base = {'backend': 'chat', 'base': 'https://gw.example.com', 'key': 'k',
            'model': 'vid-1', 'dry_run': True, 'cmd': '', 'gw_id': '', 'gw_secret': '',
            'gw_endpoint': 'director/4.0', 'price': None}
    base.update(over)
    return base


class FakeHttp:
    """按顺序返回预设响应,记录请求。"""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, headers=None, payload=None, timeout=0):
        self.calls.append(('POST', url, headers, payload))
        return self.responses.pop(0) if self.responses else {}

    def get(self, url, headers=None, timeout=0):
        self.calls.append(('GET', url, headers, None))
        return self.responses.pop(0) if self.responses else {}


def test_config_default_backend_chat_and_dry_run():
    cfg = vb.video_config({})
    assert cfg['backend'] == 'chat'
    assert cfg['dry_run'] is True
    assert cfg['model'] == ''


def test_config_problem_missing_key_for_chat():
    assert 'VIDEO_API_KEY' in vb.config_problem(_cfg(key=''))
    assert vb.config_problem(_cfg(key='k')) is None
    assert 'VIDEO_BACKEND' in vb.config_problem(_cfg(backend='nope'))
    assert '{prompt}' in vb.config_problem(_cfg(backend='command', cmd='echo'))


def test_dry_run_never_touches_network():
    http = FakeHttp([])
    r = vb.generate_video('夜雾山门', cfg=_cfg(), http=http)
    assert http.calls == []
    assert r['dry_run'] is True and r['url']


def test_chat_backend_extracts_url_cjk_safe():
    http = FakeHttp([{'choices': [{'message': {'content': '成片:https://cdn.example.com/a.mp4。请查收'}}]}])
    r = vb.generate_video('夜雾山门', cfg=_cfg(dry_run=False), http=http)
    assert r['url'] == 'https://cdn.example.com/a.mp4'
    method, url, headers, payload = http.calls[0]
    assert url.endswith('/v1/chat/completions')
    assert payload['model'] == 'vid-1'


def test_task_backend_submits_string_seconds_and_ratio_then_polls():
    http = FakeHttp([
        {'task_id': 't1', 'status': 'queued'},
        {'status': 'in_progress', 'metadata': {'url': ''}},
        {'status': 'completed', 'metadata': {'url': 'https://cdn.example.com/v.mp4'}},
    ])
    r = vb.generate_video('夜雾山门', ratio='9:16', duration=5,
                          cfg=_cfg(backend='task', dry_run=False), http=http, poll_interval=0)
    assert r['url'] == 'https://cdn.example.com/v.mp4'
    _, submit_url, _, payload = http.calls[0]
    assert submit_url.endswith('/v1/video/generations')
    assert payload['seconds'] == '5' and payload['ratio'] == '9:16'
    assert http.calls[1][1].endswith('/videos/t1')


def test_task_backend_failure_surfaces_reason():
    http = FakeHttp([{'task_id': 't2'}, {'status': 'failed', 'error': {'message': '内容不合规'}}])
    r = vb.generate_video('x', cfg=_cfg(backend='task', dry_run=False), http=http, poll_interval=0)
    assert '内容不合规' in r['error']


def test_structured_backend_maps_movement_and_clamps_duration():
    http = FakeHttp([
        {'request_id': 'r1', 'status': 'queued'},
        {'status': 'completed', 'video': {'url': 'https://gw/v.mp4'}},
    ])
    r = vb.generate_video('夜雾山门', duration=35, movement='推镜头',
                          cfg=_cfg(backend='structured', dry_run=False,
                                   gw_id='i', gw_secret='s'), http=http, poll_interval=0)
    assert r['url'] == 'https://gw/v.mp4'
    _, url, headers, payload = http.calls[0]
    assert url.endswith('/director/4.0')
    assert headers['Authorization'] == 'Key i:s'
    assert payload['camera_movement'] == 'dolly-in'
    assert payload['duration'] == 30 and payload['clamped'] == '35→30'


def test_structured_unknown_movement_omits_field():
    http = FakeHttp([{'request_id': 'r2'}, {'status': 'completed', 'video': {'url': 'u'}}])
    vb.generate_video('x', movement='自由飘逸', cfg=_cfg(backend='structured', dry_run=False,
                       gw_id='i', gw_secret='s'), http=http, poll_interval=0)
    payload = http.calls[0][3]
    assert 'camera_movement' not in payload


def test_structured_missing_credentials():
    http = FakeHttp([])
    r = vb.generate_video('x', cfg=_cfg(backend='structured', dry_run=False), http=http)
    assert http.calls == []
    assert 'VIDEO_GW_ID' in r['error']


def test_camera_enum_complete():
    assert len(vb.CAMERA_MOVEMENTS) == 33
    assert vb.to_movement('推镜头') == 'dolly-in'
    assert vb.to_movement('子弹时间') == 'bullet-time'
    assert vb.to_movement('crane-up') == 'crane-up'
    assert vb.to_movement('不存在') is None


def test_backend_id_changes_with_model():
    assert vb.backend_id(_cfg()) != vb.backend_id(_cfg(model='vid-2'))
