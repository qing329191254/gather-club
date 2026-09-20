"""把站点/会员/视频号所需图片从本地 static 上传到云存储，并回写配置。"""

from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from .cms_data import MEMBER_CONFIG
from .storage import storage_configured, upload_bytes
from .utils import get_config, set_config
from .wx import wx_configured

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = BASE_DIR / "static"

# 站点配置 / 视频号 / 会员配置需要保留品牌素材的路径
BRAND_PATHS = [
    "icons/brand.png",
    "icons/avatar-default.png",
    "icons/vip-style-v0.png",
    "icons/vip-style-v1.png",
    "icons/vip-style-v2.png",
    "icons/vip-style-v3.png",
    "icons/benefit/birthday.png",
    "icons/benefit/coupon.png",
    "icons/benefit/gift.png",
    "icons/benefit/room.png",
    "icons/benefit/seat.png",
    "icons/benefit/steward.png",
    "icons/benefit/store.png",
    "icons/benefit/waiver.png",
    "common/steward-qr.png",
    "member/bg-v0.jpg",
    "member/bg-v1.jpg",
    "member/bg-v2.jpg",
    "member/bg-v3.jpg",
    "member/card-v0.jpg",
    "member/card-v1.jpg",
    "member/card-v2.jpg",
    "member/card-v3.jpg",
    "banners/video-cover.png",
]


def _local_file(rel: str) -> Path | None:
    clean = rel.lstrip("/").replace("\\", "/")
    if clean.startswith("static/"):
        clean = clean[len("static/") :]
    path = STATIC_ROOT / clean
    return path if path.is_file() else None


def _is_local_static(url: Any) -> bool:
    if not isinstance(url, str):
        return False
    u = url.strip()
    return u.startswith("/static/") or (u.startswith("static/") )


async def _upload_rel(rel: str, cache: dict[str, str]) -> str:
    key = rel.lstrip("/").replace("\\", "/")
    if key.startswith("static/"):
        key = key[len("static/") :]
    if key in cache:
        return cache[key]
    path = _local_file(key)
    if not path:
        logger.warning("asset missing: %s", key)
        return f"/static/{key}"
    data = path.read_bytes()
    folder = "brand/" + "/".join(Path(key).parts[:-1])
    result = await upload_bytes(data, path.name, folder=folder.strip("/") or "brand")
    url = result.get("url") or ""
    if url:
        cache[key] = url
    return url or f"/static/{key}"


def _rewrite_string(value: str, cache: dict[str, str], mapping: dict[str, str]) -> str:
    if not _is_local_static(value):
        return value
    rel = value.strip().lstrip("/")
    if rel.startswith("static/"):
        rel = rel[len("static/") :]
    if rel in mapping:
        return mapping[rel]
    if rel in cache:
        return cache[rel]
    return value


def _rewrite_tree(node: Any, cache: dict[str, str], mapping: dict[str, str]) -> Any:
    if isinstance(node, dict):
        return {k: _rewrite_tree(v, cache, mapping) for k, v in node.items()}
    if isinstance(node, list):
        return [_rewrite_tree(v, cache, mapping) for v in node]
    if isinstance(node, str):
        return _rewrite_string(node, cache, mapping)
    return node


async def bootstrap_brand_assets(db: Session, force: bool = False) -> dict:
    """
    上传品牌相关静态图到 COS，并回写 site / video / member 配置。
    已是 https 云地址的字段默认保留；force=True 时按本地文件重新上传覆盖。
    """
    if not (wx_configured() and storage_configured()):
        return {"ok": False, "reason": "未配置 WX_APPID/WX_SECRET/WX_CLOUD_ENV，跳过上传"}

    cache: dict[str, str] = dict(get_config(db, "asset_map") or {})
    mapping: dict[str, str] = {}
    uploaded = 0
    for rel in BRAND_PATHS:
        if (not force) and cache.get(rel) and str(cache[rel]).startswith("http"):
            mapping[rel] = cache[rel]
            continue
        try:
            url = await _upload_rel(rel, cache)
            if url.startswith("http"):
                mapping[rel] = url
                uploaded += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception("upload failed %s: %s", rel, exc)

    set_config(db, "asset_map", cache)

    # site
    site = dict(get_config(db, "site") or {})
    site_defaults = {
        "logo": "",
        "stewardQr": "",
        "hotline": site.get("hotline") or "4001919179",
        "stewardTitle": site.get("stewardTitle") or "添加管家企业微信",
        "stewardTip": site.get("stewardTip") or "长按二维码添加管家微信",
    }
    for k, default in site_defaults.items():
        cur = site.get(k) or default
        if force or _is_local_static(cur) or not cur:
            rel = (default if _is_local_static(default) else cur).replace("/static/", "").lstrip("/")
            if rel in mapping:
                site[k] = mapping[rel]
            elif _is_local_static(cur):
                site[k] = _rewrite_string(cur, cache, mapping)
        else:
            site[k] = cur
    if "roomCapacity" not in site:
        site["roomCapacity"] = {"lunch": 4, "dinner": 8}
    set_config(db, "site", site)

    # video
    video = dict(get_config(db, "video") or {})
    video.setdefault("name", "天天俱乐部")
    video.setdefault("intro", "天天俱乐部！天天都有局！")
    for field, default in (
        ("avatar", ""),
        ("cover", ""),
    ):
        cur = video.get(field) or default
        if force or _is_local_static(cur) or not cur:
            rel = default.replace("/static/", "")
            video[field] = mapping.get(rel) or _rewrite_string(cur, cache, mapping)
    set_config(db, "video", video)

    # member：以模板为底，合并已有配置后替换静态路径
    member = deepcopy(MEMBER_CONFIG)
    existing = get_config(db, "member") or {}
    if isinstance(existing, dict) and existing.get("levels"):
        member = deepcopy(existing)
    member = _rewrite_tree(member, cache, mapping)
    set_config(db, "member", member)

    return {
        "ok": True,
        "uploaded": uploaded,
        "mapped": len(mapping),
        "site_logo": site.get("logo"),
        "video_avatar": video.get("avatar"),
    }
