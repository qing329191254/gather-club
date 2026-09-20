"""微信云托管对象存储：服务端直传，仅走云存储（不落本地盘）。"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import httpx
from fastapi import HTTPException, UploadFile

from .config import get_settings
from .wx import get_access_token, wx_configured

logger = logging.getLogger(__name__)

CLOUDBASE_TOKEN_PATHS = (
    "/.tencentcloudbase/wx/cloudbase_access_token",
    "/.tencentcloudbase/wx/access_token",
)


def storage_configured() -> bool:
    s = get_settings()
    return bool((s.wx_cloud_env or "").strip() and (wx_configured() or _read_cloudbase_token()))


def public_url_for_path(path: str) -> str:
    """对象路径 → 公网 CDN（存储需对所有用户可读）。"""
    settings = get_settings()
    clean = path.lstrip("/")
    domain = (settings.cos_cdn_domain or "").strip().rstrip("/")
    if not domain:
        bucket = settings.cos_bucket or ""
        domain = f"https://{bucket}.tcb.qcloud.la" if bucket else ""
    if not domain:
        return clean
    if not domain.startswith("http"):
        domain = "https://" + domain
    return f"{domain}/{quote(clean, safe='/')}"


def file_id_to_url(file_id: str, path: str = "") -> str:
    if not file_id:
        return public_url_for_path(path) if path else ""
    if file_id.startswith("http://") or file_id.startswith("https://"):
        return file_id
    m = re.match(r"^cloud://[^/]+/(.+)$", file_id)
    if m:
        return public_url_for_path(m.group(1))
    return public_url_for_path(path) if path else file_id


def _safe_ext(filename: str) -> str:
    ext = Path(filename or "").suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".mp4", ".pdf"}:
        return ext
    return ".jpg"


def _guess_content_type(filename: str) -> str:
    ext = _safe_ext(filename)
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".mp4": "video/mp4",
        ".pdf": "application/pdf",
    }.get(ext, "application/octet-stream")


def _read_cloudbase_token() -> str:
    for p in CLOUDBASE_TOKEN_PATHS:
        try:
            raw = Path(p).read_text(encoding="utf-8").strip()
            if raw:
                return raw
        except OSError:
            continue
    return ""


async def _token_candidates() -> list[tuple[str, str]]:
    """
    返回可用令牌列表 [(token, query_key), ...]。
    优先 AppSecret 换取的 access_token（无需白名单）；
    再试容器内 cloudbase_access_token（需在云托管配置 /tcb/uploadfile 白名单）。
    """
    out: list[tuple[str, str]] = []
    if wx_configured():
        try:
            out.append((await get_access_token(), "access_token"))
        except HTTPException as exc:
            logger.warning("get access_token failed: %s", exc.detail)
    cloud = _read_cloudbase_token()
    if cloud:
        out.append((cloud, "cloudbase_access_token"))
    return out


async def prepare_upload(path: str) -> dict:
    """向微信申请上传凭证。"""
    settings = get_settings()
    env = (settings.wx_cloud_env or "").strip()
    if not env:
        raise HTTPException(
            status_code=500,
            detail="未配置 WX_CLOUD_ENV（云托管环境 ID）",
        )

    candidates = await _token_candidates()
    if not candidates:
        raise HTTPException(
            status_code=500,
            detail="无法上传：请在云托管配置 WX_APPID + WX_SECRET，或开启云调用令牌并白名单 /tcb/uploadfile",
        )

    errors: list[str] = []
    async with httpx.AsyncClient(timeout=20.0) as client:
        for token, token_key in candidates:
            url = f"https://api.weixin.qq.com/tcb/uploadfile?{token_key}={token}"
            resp = await client.post(url, json={"env": env, "path": path})
            try:
                data = resp.json()
            except Exception:  # noqa: BLE001
                errors.append(f"{token_key}: 非 JSON ({resp.status_code})")
                continue
            errcode = int(data.get("errcode") or 0)
            if errcode == 0:
                return data
            msg = str(data.get("errmsg") or errcode)
            errors.append(f"{token_key}: {msg}")
            logger.warning("tcb/uploadfile failed via %s: %s", token_key, msg)

    hint = "；".join(errors)
    if any("unauthorized" in e.lower() or "api unauthorized" in e.lower() for e in errors):
        hint += "。若用云托管令牌，请到控制台「云调用 → 微信令牌权限」添加 /tcb/uploadfile"
    raise HTTPException(status_code=400, detail=f"申请上传凭证失败: {hint}")


async def upload_bytes(content: bytes, filename: str, folder: str = "uploads") -> dict:
    """服务端直传云托管对象存储，返回 url / fileId / path。"""
    if not content:
        raise HTTPException(status_code=400, detail="空文件")
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件不能超过 8MB")

    folder = (folder or "uploads").strip("/").replace("..", "")
    day = datetime.utcnow().strftime("%Y%m%d")
    path = f"{folder}/{day}/{uuid.uuid4().hex}{_safe_ext(filename)}"
    meta = await prepare_upload(path)

    upload_url = meta.get("url") or ""
    if not upload_url:
        raise HTTPException(status_code=400, detail="未返回上传地址")

    # COS：字段顺序固定，file 必须最后；文本字段用 (None, value)
    name = Path(filename).name or "file.jpg"
    ctype = _guess_content_type(name)
    cos_file_id = meta.get("cos_file_id") or ""
    if not cos_file_id:
        raise HTTPException(status_code=400, detail="未返回 cos_file_id，无法上传")

    files = [
        ("key", (None, path)),
        ("Signature", (None, meta.get("authorization") or "")),
        ("x-cos-security-token", (None, meta.get("token") or "")),
        ("x-cos-meta-fileid", (None, cos_file_id)),
        ("file", (name, content, ctype)),
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(upload_url, files=files)

    # COS 成功多为 204
    if resp.status_code >= 400:
        raise HTTPException(
            status_code=400,
            detail=f"上传到对象存储失败: HTTP {resp.status_code} {(resp.text or '')[:200]}",
        )

    file_id = meta.get("file_id") or ""
    url = file_id_to_url(file_id, path) or public_url_for_path(path)
    if not url:
        raise HTTPException(status_code=500, detail="上传成功但未能生成访问地址，请检查 COS_CDN_DOMAIN")
    return {"url": url, "fileId": file_id, "path": path}


async def upload_file(file: UploadFile, folder: str = "uploads") -> dict:
    content = await file.read()
    return await upload_bytes(content, file.filename or "file.jpg", folder=folder)


async def resolve_file_urls(file_ids: list[str], max_age: int = 86400) -> dict[str, str]:
    ids = [f for f in file_ids if f and str(f).startswith("cloud://")]
    if not ids:
        return {}
    if not storage_configured():
        return {fid: file_id_to_url(fid) for fid in ids}

    settings = get_settings()
    candidates = await _token_candidates()
    if not candidates:
        return {fid: file_id_to_url(fid) for fid in ids}

    token, token_key = candidates[0]
    url = f"https://api.weixin.qq.com/tcb/batchdownloadfile?{token_key}={token}"
    payload = {
        "env": settings.wx_cloud_env,
        "file_list": [{"fileid": fid, "max_age": max_age} for fid in ids],
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, json=payload)
        data = resp.json()
    if int(data.get("errcode") or 0):
        return {fid: file_id_to_url(fid) for fid in ids}

    out: dict[str, str] = {}
    for item in data.get("file_list") or []:
        fid = item.get("fileid") or ""
        download = item.get("download_url") or ""
        if fid and download:
            out[fid] = download
        elif fid:
            out[fid] = file_id_to_url(fid)
    return out
