"""出图后端：OpenAI 兼容的图片接口（GPT Image 及各类兼容网关），或用户自己的出图命令（如 Midjourney 的封装脚本）。

配置全部来自环境变量（见 README「配置出图模型」）：
  IMAGE_BACKEND   openai（默认）| command
  IMAGE_API_BASE  OpenAI 兼容接口地址，默认 https://api.openai.com
  IMAGE_API_KEY   密钥，没设时读 OPENAI_API_KEY
  IMAGE_MODEL     默认 gpt-image-1
  IMAGE_QUALITY   默认 low（分镜草图够用，也最省钱）
  IMAGE_SIZES     standard（默认，只请求 1024x1024 / 1536x1024 / 1024x1536）| exact（按画幅请求精确尺寸，网关支持时构图更准）
  IMAGE_CMD       command 后端的命令模板，占位符 {prompt} {size} {aspect} {out} {refs}
  IMAGE_PRICE     每张图的价格，只用来预估费用，可不填
"""
import base64
import json
import shlex
import subprocess
import urllib.error
import urllib.request
import uuid
from functools import reduce
from pathlib import Path

from sbcommon import ASPECT_SIZES

BACKENDS = ('openai', 'command')
# 官方 gpt-image 只收这三种尺寸；画幅不同的图出来后再按画幅居中裁切
STANDARD_SIZES = {'16:9': '1536x1024', '9:16': '1024x1536', '1:1': '1024x1024',
                  '4:3': '1536x1024', '2.39:1': '1536x1024'}
TIMEOUT = 900


def _price(env):
    try:
        return float(env['IMAGE_PRICE']) if env.get('IMAGE_PRICE') else None
    except ValueError:
        return None


def image_config(env):
    """从环境变量读出图配置。"""
    return {
        'backend': env.get('IMAGE_BACKEND', 'openai'),
        'base': env.get('IMAGE_API_BASE', 'https://api.openai.com').rstrip('/'),
        'key': env.get('IMAGE_API_KEY') or env.get('OPENAI_API_KEY', ''),
        'model': env.get('IMAGE_MODEL', 'gpt-image-1'),
        'quality': env.get('IMAGE_QUALITY', 'low'),
        'sizes': env.get('IMAGE_SIZES', 'standard'),
        'cmd': env.get('IMAGE_CMD', ''),
        'price': _price(env),
    }


def request_size(aspect, mode):
    return ASPECT_SIZES[aspect] if mode == 'exact' else STANDARD_SIZES[aspect]


def backend_id(cfg):
    """写进出图签名：换了模型或出图命令，旧图要重出。"""
    return cfg['model'] if cfg['backend'] == 'openai' else 'command:' + cfg['cmd']


def config_problem(cfg):
    """配置有问题时返回提示，没问题返回 None。"""
    if cfg['backend'] not in BACKENDS:
        return f"不支持的 IMAGE_BACKEND：{cfg['backend']}（可选 {'、'.join(BACKENDS)}）"
    if cfg['backend'] == 'openai' and not cfg['key']:
        return '需要设置 IMAGE_API_KEY（或 OPENAI_API_KEY），见 README「配置出图模型」'
    if cfg['backend'] == 'command' and not ('{prompt}' in cfg['cmd'] and '{out}' in cfg['cmd']):
        return 'command 后端需要设置 IMAGE_CMD，并且包含 {prompt} 和 {out} 两个占位符'
    if cfg['sizes'] not in ('standard', 'exact'):
        return 'IMAGE_SIZES 只能是 standard 或 exact'
    return None


def build_command(template, job, size, aspect, out):
    """先把命令模板拆成参数，再逐个替换占位符；不经过 shell，提示词里写什么都不会被当成命令执行。"""
    refs = ','.join(str(p) for p in job['refs'] if Path(p).is_file())
    values = {'{prompt}': job['prompt'], '{size}': size, '{aspect}': aspect, '{out}': str(out), '{refs}': refs}
    return [reduce(lambda arg, kv: arg.replace(*kv), values.items(), arg) for arg in shlex.split(template)]


def command_image(job, size, aspect, cfg, out):
    """调用户的出图命令，命令要把图写到 {out}。成功返回 None，失败返回错误信息。"""
    args = build_command(cfg['cmd'], job, size, aspect, out)
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT)
    except FileNotFoundError:
        return f'找不到出图命令：{args[0]}'
    except subprocess.TimeoutExpired:
        return f'超时（{TIMEOUT}s）'
    if r.returncode != 0:
        return (r.stderr or r.stdout).strip()[-300:] or f'退出码 {r.returncode}'
    return None


def _multipart(fields, files):
    boundary = uuid.uuid4().hex
    text = [f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
            for k, v in fields.items()]
    images = [f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="{p.name}"\r\n'
              f'Content-Type: {"image/png" if p.suffix.lower() == ".png" else "image/jpeg"}\r\n\r\n'.encode()
              + p.read_bytes() + b'\r\n' for p in files]
    return b''.join(text + images + [f'--{boundary}--\r\n'.encode()]), f'multipart/form-data; boundary={boundary}'


def _request(url, key, data, ctype):
    """发请求，返回 (响应 JSON, 错误信息)。"""
    req = urllib.request.Request(url, data=data, headers={'Authorization': f'Bearer {key}', 'Content-Type': ctype})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, f'HTTP {e.code}：{e.read().decode("utf-8", "replace")[:300]}'
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        return None, f'请求失败：{e}'


def _save_first_image(resp, out):
    if not isinstance(resp, dict) or resp.get('error'):
        detail = resp.get('error') if isinstance(resp, dict) else resp
        return f'接口报错：{json.dumps(detail, ensure_ascii=False)[:300]}'
    items = resp.get('data') or []
    item = items[0] if items and isinstance(items[0], dict) else {}
    if item.get('b64_json'):
        Path(out).write_bytes(base64.b64decode(item['b64_json']))
        return None
    if item.get('url'):
        with urllib.request.urlopen(item['url'], timeout=TIMEOUT) as r:
            Path(out).write_bytes(r.read())
        return None
    return f'响应里没有图片：{json.dumps(resp, ensure_ascii=False)[:300]}'


def openai_image(job, size, cfg, out):
    """调 OpenAI 兼容的图片接口：没有参考图走 generations，有参考图走 edits。成功返回 None。"""
    fields = {'model': cfg['model'], 'prompt': job['prompt'], 'size': size, 'quality': cfg['quality'], 'n': 1}
    refs = [Path(p) for p in job['refs'] if Path(p).is_file()]
    if refs:
        body, ctype = _multipart({k: str(v) for k, v in fields.items()}, refs)
        resp, err = _request(f"{cfg['base']}/v1/images/edits", cfg['key'], body, ctype)
    else:
        resp, err = _request(f"{cfg['base']}/v1/images/generations", cfg['key'],
                             json.dumps(fields, ensure_ascii=False).encode(), 'application/json')
    return err or _save_first_image(resp, out)
