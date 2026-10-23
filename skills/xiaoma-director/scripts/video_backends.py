"""视频生成后端：把分镜直接生成视频片段。

配置全部来自环境变量（见 README「配置视频模型」）：
  VIDEO_BACKEND    chat（默认，OpenAI 兼容接口，URL 在回复文本里）| task（任务型网关：提交后轮询）
                  | structured（结构化网关：Key 鉴权 + 导演参数枚举）| command（自己的封装命令）
  VIDEO_API_BASE   网关地址，默认 https://api.openai.com
  VIDEO_API_KEY    密钥，没设时读 OPENAI_API_KEY
  VIDEO_MODEL      模型名（chat / task 后端用）
  VIDEO_DRY_RUN    默认 1：只产出提示词不联网；设 0 才真出片
  VIDEO_CMD        command 后端命令模板，占位符 {prompt} {out} {ratio} {duration}
  VIDEO_GW_ID / VIDEO_GW_SECRET / VIDEO_GW_ENDPOINT   structured 后端的 Key 鉴权与端点 id
  VIDEO_PRICE      每秒价格，只用来预估费用

所有后端统一入口 generate_video()，返回 {'url': ...} 或 {'error': ...}，不抛网络异常。
"""
import json
import re
import shlex
import subprocess
import urllib.error
import urllib.request

BACKENDS = ('chat', 'task', 'structured', 'command')
URL_RE = re.compile(r'https?://[^\s"\'<>\u3000-\u303f\uff00-\uffef\u4e00-\u9fff]+')
TIMEOUT = 600
POLL_INTERVAL = 8

# 结构化网关的官方运镜枚举（33 值）与中文词条映射；映射表只收语义明确的常用词，
# 分镜里写了别的运镜就不传该字段，让端点自动导演。
CAMERA_MOVEMENTS = (
    'snorricam', 'robot-arm', 'tilt-up', 'rack-focus', 'tilt-down', 'pov', 'pan-left', 'crane-up',
    'pan-right', 'crane-down', 'side-tracking', 'pedestal-up', 'pedestal-down', 'handheld',
    'tracking', 'drone-orbit', 'dolly-zoom', 'aerial-pullback', 'static-shot', 'bullet-time',
    'whip-pan', 'slow-zoom-in', 'arc-left', 'slow-zoom-out', 'arc-right', 'truck-right',
    'dolly-in', 'truck-left', 'dolly-out', 'slider-right', 'crush-zoom', 'slider-left',
    'helicopter-shot',
)
_ZH_MOVEMENTS = {
    '推镜头': 'dolly-in', '推': 'dolly-in', '缓推': 'slow-zoom-in', '急推': 'crush-zoom',
    '拉镜头': 'dolly-out', '拉': 'dolly-out', '缓拉': 'slow-zoom-out',
    '变焦推': 'dolly-zoom', '甩': 'whip-pan', '甩镜头': 'whip-pan',
    '摇': 'pan-right', '左摇': 'pan-left', '右摇': 'pan-right', '上摇': 'tilt-up', '下摇': 'tilt-down',
    '移': 'truck-right', '左移': 'truck-left', '右移': 'truck-right',
    '滑轨': 'slider-right', '跟': 'tracking', '跟镜头': 'tracking', '侧跟': 'side-tracking',
    '环绕': 'drone-orbit', '弧线': 'arc-right', '左弧': 'arc-left', '右弧': 'arc-right',
    '摇臂升': 'crane-up', '摇臂降': 'crane-down', '升': 'pedestal-up', '降': 'pedestal-down',
    '手持': 'handheld', '绑身': 'snorricam', '机械臂': 'robot-arm',
    '子弹时间': 'bullet-time', '穿越机': 'drone-orbit', '航拍后拉': 'aerial-pullback',
    '直升机': 'helicopter-shot', '移焦': 'rack-focus', '第一视角': 'pov',
    '固定': 'static-shot', '静止': 'static-shot',
}


def to_movement(zh):
    """中文运镜词条 → 官方枚举；不认识返回 None（调用方应省略该字段）。"""
    if not zh:
        return None
    zh = zh.strip()
    if zh in CAMERA_MOVEMENTS:
        return zh
    return _ZH_MOVEMENTS.get(zh)


def video_config(env):
    return {
        'backend': env.get('VIDEO_BACKEND', 'chat'),
        'base': env.get('VIDEO_API_BASE', 'https://api.openai.com').rstrip('/'),
        'key': env.get('VIDEO_API_KEY') or env.get('OPENAI_API_KEY', ''),
        'model': env.get('VIDEO_MODEL', ''),
        'dry_run': env.get('VIDEO_DRY_RUN', '1') != '0',
        'cmd': env.get('VIDEO_CMD', ''),
        'gw_id': env.get('VIDEO_GW_ID', ''),
        'gw_secret': env.get('VIDEO_GW_SECRET', ''),
        'gw_endpoint': env.get('VIDEO_GW_ENDPOINT', ''),
        'price': _price(env),
    }


def _price(env):
    try:
        return float(env['VIDEO_PRICE']) if env.get('VIDEO_PRICE') else None
    except ValueError:
        return None


def config_problem(cfg):
    if cfg['backend'] not in BACKENDS:
        return f"不支持的 VIDEO_BACKEND：{cfg['backend']}（可选 {'、'.join(BACKENDS)}）"
    if cfg['backend'] in ('chat', 'task'):
        if not cfg['key']:
            return '需要设置 VIDEO_API_KEY（或 OPENAI_API_KEY），见 README「配置视频模型」'
        if not cfg['model']:
            return 'chat / task 后端需要设置 VIDEO_MODEL'
    if cfg['backend'] == 'command' and not ('{prompt}' in cfg['cmd'] and '{out}' in cfg['cmd']):
        return 'command 后端需要设置 VIDEO_CMD，并且包含 {prompt} 和 {out} 两个占位符'
    if cfg['backend'] == 'structured':
        if not (cfg['gw_id'] and cfg['gw_secret']):
            return 'structured 后端需要设置 VIDEO_GW_ID 和 VIDEO_GW_SECRET'
        if not cfg['gw_endpoint']:
            return 'structured 后端需要设置 VIDEO_GW_ENDPOINT（端点 id）'
    return None


def backend_id(cfg):
    """写进视频签名：换了模型或命令，旧片段要重出。"""
    if cfg['backend'] == 'chat':
        return f"chat:{cfg['model']}"
    if cfg['backend'] == 'task':
        return f"task:{cfg['model']}"
    if cfg['backend'] == 'structured':
        return f"structured:{cfg['gw_endpoint']}"
    return 'command:' + cfg['cmd']


class _UrllibHttp:
    """默认 HTTP 实现，测试里注入 FakeHttp 替换。"""

    def _open(self, req, timeout):
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))

    def post(self, url, headers=None, payload=None, timeout=TIMEOUT):
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method='POST')
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        req.add_header('Content-Type', 'application/json')
        return self._open(req, timeout)

    def get(self, url, headers=None, timeout=TIMEOUT):
        req = urllib.request.Request(url, method='GET')
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        return self._open(req, timeout)


def generate_video(prompt, *, ratio='16:9', duration=5, movement=None, cfg=None, http=None,
                   env=None, poll_interval=POLL_INTERVAL):
    """统一入口。dry-run（默认）只回提示词摘要，不联网。"""
    cfg = cfg or video_config(env or {})
    if cfg['dry_run']:
        return {'url': f'dry-run:{prompt[:60]}', 'dry_run': True}
    problem = config_problem(cfg)
    if problem:
        return {'error': problem}
    http = http or _UrllibHttp()
    try:
        if cfg['backend'] == 'chat':
            return _chat(prompt, cfg, http)
        if cfg['backend'] == 'task':
            return _task(prompt, ratio, duration, cfg, http, poll_interval)
        if cfg['backend'] == 'structured':
            return _structured(prompt, ratio, duration, movement, cfg, http, poll_interval)
        return _command(prompt, ratio, duration, cfg)
    except urllib.error.URLError as e:
        return {'error': f'网络失败：{e}'}
    except Exception as e:  # noqa: BLE001 —— 后端响应形状不可控，统一兜成 error
        return {'error': f'后端异常：{e}'}


def _chat(prompt, cfg, http):
    data = http.post(f'{cfg["base"]}/v1/chat/completions',
                     headers={'Authorization': f'Bearer {cfg["key"]}'},
                     payload={'model': cfg['model'], 'messages': [{'role': 'user', 'content': prompt}]})
    text = (data.get('choices') or [{}])[0].get('message', {}).get('content', '') or ''
    url = URL_RE.search(text)
    if not url:
        return {'error': f'回复里没找到视频 URL：{text[:120]}'}
    return {'url': url.group(0)}


def _task(prompt, ratio, duration, cfg, http, poll_interval=POLL_INTERVAL):
    data = http.post(f'{cfg["base"]}/v1/video/generations',
                     headers={'Authorization': f'Bearer {cfg["key"]}'},
                     payload={'model': cfg['model'], 'prompt': prompt,
                              'seconds': str(int(duration)), 'ratio': ratio})
    task_id = data.get('task_id') or data.get('id')
    if not task_id:
        return {'error': f'提交响应缺 task_id：{json.dumps(data)[:160]}'}
    import time
    while True:
        st = http.get(f'{cfg["base"]}/v1/videos/{task_id}',
                      headers={'Authorization': f'Bearer {cfg["key"]}'})
        status = str(st.get('status', '')).lower()
        url = (st.get('metadata') or {}).get('url') or st.get('url') or ''
        if status in ('completed', 'succeeded') and url:
            return {'url': url}
        if status == 'failed':
            why = (st.get('error') or {}).get('message') or st.get('fail_reason') or json.dumps(st)[:120]
            return {'error': f'生成失败：{why}'}
        time.sleep(poll_interval)


def _structured(prompt, ratio, duration, movement, cfg, http, poll_interval=POLL_INTERVAL):
    import time
    body = {'prompt': prompt, 'aspect_ratio': ratio}
    body.update(_clamp_duration(duration))
    mv = to_movement(movement)
    if mv:
        body['camera_movement'] = mv
    headers = {'Authorization': f'Key {cfg["gw_id"]}:{cfg["gw_secret"]}'}
    submitted = http.post(f'{cfg["base"]}/{cfg["gw_endpoint"]}', headers=headers, payload=body)
    request_id = submitted.get('request_id')
    if not request_id:
        return {'error': f'提交响应缺 request_id：{json.dumps(submitted)[:160]}'}
    while True:
        st = http.get(f'{cfg["base"]}/requests/{request_id}/status', headers=headers)
        status = str(st.get('status', '')).lower()
        if status == 'completed':
            url = (st.get('video') or {}).get('url') or (st.get('output') or {}).get('url') or ''
            if url:
                return {'url': url}
            return {'error': '任务完成但响应里没有视频 URL'}
        if status in ('failed', 'cancelled', 'canceled'):
            why = (st.get('error') or {}).get('message') or json.dumps(st)[:120]
            return {'error': f'生成失败：{why}'}
        time.sleep(poll_interval)


def _clamp_duration(duration):
    d = max(4, min(30, int(duration)))
    if d != int(duration):
        return {'duration': d, 'clamped': f'{int(duration)}→{d}'}
    return {'duration': d}


def _command(prompt, ratio, duration, cfg):
    out = f'video_{abs(hash(prompt)) % 10**8}.mp4'
    cmd = cfg['cmd'].format(prompt=shlex.quote(prompt), out=out, ratio=ratio, duration=duration)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=TIMEOUT)
    if result.returncode != 0:
        return {'error': f'命令失败：{result.stderr.strip()[:200]}'}
    url = URL_RE.search(result.stdout or '')
    return {'url': url.group(0) if url else out}
