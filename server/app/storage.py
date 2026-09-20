"""微信云托管对象存储：服务端直传云存储（不落本地盘）。"""

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
    return bool((s.wx_cloud_env or "").strip())


def public_url_for_path(path: str) -> str:
    settings = get_settings()
    clean = path.lstrip("/")
    domain = (settings.cos_cdn_domain or "").strip().rstrip("/")
    if not domain:
        bucket = (settings.cos_bucket or "").strip()
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


def _strip(s: str) -> str:
    return (s or "").strip().strip('"').strip("'")


async def diagnose_storage() -> dict:
    """后台可调用的诊断信息（不含密钥）。"""
    s = get_settings()
    appid = _strip(s.wx_appid)
    secret = _strip(s.wx_secret)
    env = _strip(s.wx_cloud_env)
    cloud_token = bool(_read_cloudbase_token())
    token_ok = False
    token_err = ""
    if appid and secret:
        try:
            await get_access_token()
            token_ok = True
        except HTTPException as exc:
            token_err = str(exc.detail)
        except Exception as exc:  # noqa: BLE001
            token_err = str(exc)
    return {
        "wx_cloud_env": env or "(空)",
        "wx_appid_set": bool(appid),
        "wx_appid_suffix": appid[-6:] if len(appid) >= 6 else appid,
        "wx_secret_set": bool(secret),
        "wx_secret_len": len(secret),
        "cos_cdn_domain": _strip(s.cos_cdn_domain) or "(空)",
        "cloudbase_token_mounted": cloud_token,
        "access_token_ok": token_ok,
        "access_token_error": token_err,
        "hint": (
            "正常只需 WX_APPID+WX_SECRET，不必开开放接口服务。"
            "若 access_token_ok=false，请核对 Secret 是否与小程序后台一致、有无空格/引号，并确认云托管已重新发布最新版本。"
        ),
    }


async def _prepare_upload_attempts(env: str, path: str) -> list[tuple[str, dict]]:
    """构造申请上传凭证的方式：优先 AppSecret（与常见后台做法一致，无需开放接口服务）。"""
    attempts: list[tuple[str, dict]] = []
    body = {"env": env, "path": path}

    # 1) 经典做法：AppSecret → access_token（不需要开开放接口服务 / 白名单）
    if wx_configured():
        try:
            token = await get_access_token()
            attempts.append(
                (
                    "access_token",
                    {
                        "url": f"https://api.weixin.qq.com/tcb/uploadfile?access_token={token}",
                        "json": body,
                    },
                )
            )
        except HTTPException as exc:
            raise HTTPException(
                status_code=500,
                detail=f"获取 access_token 失败（请核对 WX_APPID / WX_SECRET）: {exc.detail}",
            ) from exc

    # 2) 容器挂载云调用令牌（可选；需控制台白名单 /tcb/uploadfile）
    cloud = _read_cloudbase_token()
    if cloud:
        attempts.append(
            (
                "cloudbase_access_token",
                {
                    "url": f"https://api.weixin.qq.com/tcb/uploadfile?cloudbase_access_token={cloud}",
                    "json": body,
                },
            )
        )

    # 3) 开放接口服务免 token（仅在云托管开了该能力时才有用，放最后）
    attempts.append(
        (
            "openapi_http",
            {"url": "http://api.weixin.qq.com/tcb/uploadfile", "json": body},
        )
    )
    return attempts


async def prepare_upload(path: str) -> dict:
    settings = get_settings()
    env = _strip(settings.wx_cloud_env)
    if not env:
        raise HTTPException(status_code=500, detail="未配置 WX_CLOUD_ENV")

    attempts = await _prepare_upload_attempts(env, path)
    if not attempts:
        raise HTTPException(
            status_code=500,
            detail="无法申请上传凭证：请配置 WX_APPID+WX_SECRET，或开启云托管开放接口服务并白名单 /tcb/uploadfile",
        )

    errors: list[str] = []
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for name, req in attempts:
            try:
                resp = await client.post(req["url"], json=req["json"])
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{name}: 网络异常 {exc}")
                continue
            try:
                data = resp.json()
            except Exception:  # noqa: BLE001
                errors.append(f"{name}: HTTP {resp.status_code} 非 JSON {(resp.text or '')[:120]}")
                continue
            errcode = int(data.get("errcode") or 0)
            if errcode == 0 and data.get("url"):
                logger.info("upload credential ok via %s", name)
                return data
            msg = str(data.get("errmsg") or data.get("errcode") or resp.status_code)
            errors.append(f"{name}: {msg}")
            logger.warning("upload credential failed via %s: %s", name, msg)

    detail = "；".join(errors)
    if any("unauthorized" in e.lower() for e in errors) or any("502" in e for e in errors):
        detail += "。请到云托管控制台 → 云调用 → 开启「开放接口服务」，权限配置添加 /tcb/uploadfile，然后重新发布服务版本"
    raise HTTPException(status_code=400, detail=f"申请上传凭证失败: {detail}")


async def upload_bytes(content: bytes, filename: str, folder: str = "uploads") -> dict:
    if not content:
        raise HTTPException(status_code=400, detail="空文件")
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件不能超过 8MB")

    folder = (folder or "uploads").strip("/").replace("..", "")
    day = datetime.utcnow().strftime("%Y%m%d")
    path = f"{folder}/{day}/{uuid.uuid4().hex}{_safe_ext(filename)}"

    try:
        meta = await prepare_upload(path)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("prepare_upload crashed")
        raise HTTPException(status_code=500, detail=f"申请上传凭证异常: {exc}") from exc

    upload_url = meta.get("url") or ""
    cos_file_id = meta.get("cos_file_id") or ""
    authorization = meta.get("authorization") or ""
    token = meta.get("token") or ""
    if not upload_url or not cos_file_id or not authorization or not token:
        raise HTTPException(
            status_code=400,
            detail=f"上传凭证字段不完整: url/cos_file_id/authorization/token",
        )

    name = Path(filename).name or "file.jpg"
    ctype = _guess_content_type(name)
    files = [
        ("key", (None, path)),
        ("Signature", (None, authorization)),
        ("x-cos-security-token", (None, token)),
        ("x-cos-meta-fileid", (None, cos_file_id)),
        ("file", (name, content, ctype)),
    ]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(upload_url, files=files)
    except Exception as exc:  # noqa: BLE001
        logger.exception("cos upload crashed")
        raise HTTPException(status_code=500, detail=f"上传 COS 异常: {exc}") from exc

    if resp.status_code >= 400:
        raise HTTPException(
            status_code=400,
            detail=f"上传到对象存储失败: HTTP {resp.status_code} {(resp.text or '')[:200]}",
        )

    file_id = meta.get("file_id") or ""
    url = file_id_to_url(file_id, path) or public_url_for_path(path)
    if not url:
        raise HTTPException(status_code=500, detail="上传成功但未生成访问地址，请检查 COS_CDN_DOMAIN")
    return {"url": url, "fileId": file_id, "path": path}


async def upload_file(file: UploadFile, folder: str = "uploads") -> dict:
    content = await file.read()
    return await upload_bytes(content, file.filename or "file.jpg", folder=folder)


async def resolve_file_urls(file_ids: list[str], max_age: int = 86400) -> dict[str, str]:
    ids = [f for f in file_ids if f and str(f).startswith("cloud://")]
    if not ids:
        return {}
    settings = get_settings()
    env = _strip(settings.wx_cloud_env)
    token = ""
    token_key = "access_token"
    if wx_configured():
        try:
            token = await get_access_token()
        except HTTPException:
            token = ""
    if not token:
        token = _read_cloudbase_token()
        token_key = "cloudbase_access_token"
    if not token or not env:
        return {fid: file_id_to_url(fid) for fid in ids}

    url = f"https://api.weixin.qq.com/tcb/batchdownloadfile?{token_key}={token}"
    payload = {"env": env, "file_list": [{"fileid": fid, "max_age": max_age} for fid in ids]}
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
