"""微信小程序服务端能力：登录换 openid、换取手机号。"""

from __future__ import annotations

import base64
import json
import time
from typing import Any, Optional

import httpx
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from fastapi import HTTPException

from .config import get_settings

_TOKEN_CACHE: dict[str, Any] = {"token": "", "expires_at": 0.0, "key": ""}

# 云托管容器内常注入 api.weixin.qq.com 自签证书，https + 默认校验会失败；
# 官方也建议容器内用 http 访问该域名。
WX_API_HOST = "http://api.weixin.qq.com"


def wx_api_url(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return WX_API_HOST + path


def wx_http_client(timeout: float = 15.0, **kwargs) -> httpx.AsyncClient:
    """调用微信开放接口的 httpx 客户端（跳过自签证书校验）。"""
    return httpx.AsyncClient(timeout=timeout, verify=False, follow_redirects=True, **kwargs)


def wx_configured() -> bool:
    s = get_settings()
    return bool(s.wx_appid and s.wx_secret)


async def code2session(js_code: str) -> dict[str, str]:
    """用 wx.login 的 code 换 openid / session_key。"""
    if not js_code:
        raise HTTPException(status_code=400, detail="缺少登录 code")
    settings = get_settings()
    if not settings.wx_appid or not settings.wx_secret:
        raise HTTPException(status_code=500, detail="未配置 WX_APPID / WX_SECRET")

    url = wx_api_url("/sns/jscode2session")
    params = {
        "appid": settings.wx_appid,
        "secret": settings.wx_secret,
        "js_code": js_code,
        "grant_type": "authorization_code",
    }
    async with wx_http_client(timeout=10.0) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    errcode = int(data.get("errcode") or 0)
    if errcode:
        raise HTTPException(
            status_code=400,
            detail=f"微信登录失败: {data.get('errmsg') or errcode}",
        )
    openid = data.get("openid") or ""
    if not openid:
        raise HTTPException(status_code=400, detail="微信未返回 openid")
    return {
        "openid": openid,
        "session_key": data.get("session_key") or "",
        "unionid": data.get("unionid") or "",
    }


async def get_access_token() -> str:
    settings = get_settings()
    appid = (settings.wx_appid or "").strip().strip('"').strip("'")
    secret = (settings.wx_secret or "").strip().strip('"').strip("'")
    if not appid or not secret:
        raise HTTPException(status_code=500, detail="未配置 WX_APPID / WX_SECRET")

    now = time.time()
    cache_key = f"{appid}:{secret[:8]}"
    if (
        _TOKEN_CACHE.get("key") == cache_key
        and _TOKEN_CACHE.get("token")
        and _TOKEN_CACHE.get("expires_at", 0) > now + 60
    ):
        return str(_TOKEN_CACHE["token"])

    url = wx_api_url("/cgi-bin/token")
    params = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret,
    }
    async with wx_http_client(timeout=10.0) as client:
        resp = await client.get(url, params=params)
        try:
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=502,
                detail=f"获取 access_token 失败: 微信返回非 JSON HTTP {resp.status_code}",
            ) from exc

    token = data.get("access_token") or ""
    if not token:
        raise HTTPException(
            status_code=400,
            detail=f"获取 access_token 失败: {data.get('errmsg') or data}",
        )
    _TOKEN_CACHE["key"] = cache_key
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["expires_at"] = now + int(data.get("expires_in") or 7200)
    return token


async def phone_from_code(phone_code: str) -> str:
    """新版 getPhoneNumber 返回的 code 换手机号。"""
    if not phone_code:
        raise HTTPException(status_code=400, detail="缺少手机号 code")
    token = await get_access_token()
    url = wx_api_url(f"/wxa/business/getuserphonenumber?access_token={token}")
    async with wx_http_client(timeout=10.0) as client:
        resp = await client.post(url, json={"code": phone_code})
        data = resp.json()

    errcode = int(data.get("errcode") or 0)
    if errcode:
        raise HTTPException(
            status_code=400,
            detail=f"获取手机号失败: {data.get('errmsg') or errcode}",
        )
    info = data.get("phone_info") or {}
    phone = str(info.get("purePhoneNumber") or info.get("phoneNumber") or "").strip()
    if not phone:
        raise HTTPException(status_code=400, detail="微信未返回手机号")
    return phone


def phone_from_encrypted(session_key: str, encrypted_data: str, iv: str) -> str:
    """旧版 encryptedData + iv 解密手机号。"""
    if not session_key or not encrypted_data or not iv:
        raise HTTPException(status_code=400, detail="缺少解密参数")
    try:
        key = base64.b64decode(session_key)
        data = base64.b64decode(encrypted_data)
        iv_b = base64.b64decode(iv)
        decryptor = Cipher(algorithms.AES(key), modes.CBC(iv_b)).decryptor()
        raw = decryptor.update(data) + decryptor.finalize()
        pad = raw[-1]
        if isinstance(pad, str):
            pad = ord(pad)
        text = raw[:-pad].decode("utf-8")
        payload = json.loads(text)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"手机号解密失败: {exc}") from exc

    phone = str(payload.get("purePhoneNumber") or payload.get("phoneNumber") or "").strip()
    if not phone:
        raise HTTPException(status_code=400, detail="解密结果无手机号")
    return phone


def resolve_demo_openid(code: str) -> dict[str, str]:
    """未配置 AppSecret 时的本地演示登录。"""
    openid = code.strip() if code else f"demo_{int(time.time())}"
    if len(openid) < 8:
        openid = f"demo_{openid or 'guest'}"
    return {"openid": openid, "session_key": "", "unionid": ""}
