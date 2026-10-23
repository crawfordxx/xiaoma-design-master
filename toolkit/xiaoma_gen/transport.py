"""极简 HTTP 传输层（标准库 urllib，无第三方依赖）。"""
from __future__ import annotations

import json
import urllib.error
import urllib.request


def _request(url: str, headers: dict, data: bytes | None, timeout: int) -> tuple[int, str]:
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def http_post(url: str, headers: dict, body: dict, timeout: int = 600) -> tuple[int, str]:
    headers = {"Content-Type": "application/json", "Accept-Encoding": "identity", **headers}
    return _request(url, headers, json.dumps(body, ensure_ascii=False).encode("utf-8"), timeout)


def http_get(url: str, headers: dict, timeout: int = 60) -> tuple[int, str]:
    headers = {"Accept-Encoding": "identity", **headers}
    return _request(url, headers, None, timeout)
