"""微信云托管对象存储：通过开放接口上传，返回可访问 URL；失败时回退本地 static/uploads。"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
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

# server/static/uploads
UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "static" / "uploads"


def storage_configured() -> bool:
    s = get_settings()
    if not (s.wx_cloud_env or "").strip():
        return False
    if wx_configured():
        return True
    return any(Path(p).is_file() for p in CLOUDBASE_TOKEN_PATHS)


def public_url_for_path(path: str) -> str:
    """把对象路径转成公网访问地址（需存储权限为所有用户可读）。"""
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
    """cloud://fileID 尽量转成 https；失败则用 path 拼 CDN。"""
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


def _read_cloudbase_token() -> str:
    for p in CLOUDBASE_TOKEN_PATHS:
        try:
            raw = Path(p).read_text(encoding="utf-8").strip()
            if raw:
                return raw
        except OSError:
            continue
    return ""


async def _wx_api_token() -> tuple[str, str]:
    """返回 (token, query_param_name)。优先容器内云托管令牌。"""
    cloud_token = _read_cloudbase_token()
    if cloud_token:
        return cloud_token, "cloudbase_access_token"
    token = await get_access_token()
    return token, "access_token"


async def prepare_upload(path: str) -> dict:
    """向微信申请上传凭证。"""
    if not storage_configured():
        raise HTTPException(status_code=500, detail="未配置云托管对象存储环境变量")
    settings = get_settings()
    token, token_key = await _wx_api_token()
    url = f"https://api.weixin.qq.com/tcb/uploadfile?{token_key}={token}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, json={"env": settings.wx_cloud_env, "path": path})
        try:
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=502,
                detail=f"申请上传凭证失败: 微信接口返回非 JSON ({resp.status_code})",
            ) from exc
    errcode = int(data.get("errcode") or 0)
    if errcode:
        raise HTTPException(
            status_code=400,
            detail=f"申请上传凭证失败: {data.get('errmsg') or errcode}",
        )
    return data


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


async def upload_bytes_cloud(content: bytes, filename: str, folder: str = "uploads") -> dict:
    """服务端直传云托管对象存储。"""
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

    # COS 要求字段顺序固定，file 必须在最后
    name = Path(filename).name or "file.jpg"
    ctype = _guess_content_type(name)
    files = [
        ("key", (None, path)),
        ("Signature", (None, meta.get("authorization") or "")),
        ("x-cos-security-token", (None, meta.get("token") or "")),
        ("x-cos-meta-fileid", (None, meta.get("cos_file_id") or meta.get("file_id") or "")),
        ("file", (name, content, ctype)),
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(upload_url, files=files)

    if resp.status_code >= 400:
        raise HTTPException(
            status_code=400,
            detail=f"上传到对象存储失败: HTTP {resp.status_code} {resp.text[:200]}",
        )

    file_id = meta.get("file_id") or ""
    url = file_id_to_url(file_id, path)
    if not url:
        url = public_url_for_path(path)
    return {"url": url, "fileId": file_id, "path": path, "storage": "cloud"}


def upload_bytes_local(content: bytes, filename: str, folder: str = "uploads", base_url: str = "") -> dict:
    """本地落盘到 static/uploads，返回可访问路径。"""
    if not content:
        raise HTTPException(status_code=400, detail="空文件")
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件不能超过 8MB")

    folder = (folder or "uploads").strip("/").replace("..", "")
    day = datetime.utcnow().strftime("%Y%m%d")
    rel = f"{folder}/{day}/{uuid.uuid4().hex}{_safe_ext(filename)}"
    dest = UPLOAD_ROOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)

    settings = get_settings()
    public = (getattr(settings, "public_base_url", "") or base_url or "").rstrip("/")
    url = f"{public}/uploads/{rel}" if public else f"/uploads/{rel}"
    return {"url": url, "fileId": "", "path": rel, "storage": "local"}


async def upload_bytes(content: bytes, filename: str, folder: str = "uploads", base_url: str = "") -> dict:
    """优先云存储，失败或未配置时回退本地。"""
    if storage_configured():
        try:
            return await upload_bytes_cloud(content, filename, folder=folder)
        except HTTPException as exc:
            logger.warning("cloud upload failed, fallback local: %s", exc.detail)
        except Exception as exc:  # noqa: BLE001
            logger.exception("cloud upload error, fallback local: %s", exc)
    return upload_bytes_local(content, filename, folder=folder, base_url=base_url)


async def upload_file(file: UploadFile, folder: str = "uploads", base_url: str = "") -> dict:
    content = await file.read()
    return await upload_bytes(content, file.filename or "file.jpg", folder=folder, base_url=base_url)


async def resolve_file_urls(file_ids: list[str], max_age: int = 86400) -> dict[str, str]:
    """批量把 cloud:// fileId 换成临时/可用下载链接。"""
    ids = [f for f in file_ids if f and str(f).startswith("cloud://")]
    if not ids:
        return {}
    if not storage_configured():
        return {fid: file_id_to_url(fid) for fid in ids}

    settings = get_settings()
    token, token_key = await _wx_api_token()
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
