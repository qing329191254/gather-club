import json
from typing import Any

from sqlalchemy.orm import Session

from .models import SiteConfig


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def loads(raw: str | None, default: Any = None) -> Any:
    if raw is None or raw == "":
        return default if default is not None else {}
    try:
        return json.loads(raw)
    except Exception:
        return default if default is not None else {}


def get_config(db: Session, key: str, default: Any = None) -> Any:
    row = db.query(SiteConfig).filter(SiteConfig.key == key).first()
    if not row:
        return default
    return loads(row.value, default)


def set_config(db: Session, key: str, value: Any) -> SiteConfig:
    row = db.query(SiteConfig).filter(SiteConfig.key == key).first()
    raw = dumps(value)
    if row:
        row.value = raw
    else:
        row = SiteConfig(key=key, value=raw)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


STATUS_TEXT = {
    "pending": "待支付",
    "paid": "已支付",
    "cancelled": "已取消",
    "completed": "已完成",
    "refunded": "已退款",
}


def normalize_page(page: int | None = 1, page_size: int | None = 20, max_size: int = 100) -> tuple[int, int, int]:
    page = max(1, int(page or 1))
    page_size = min(max_size, max(1, int(page_size or 20)))
    offset = (page - 1) * page_size
    return page, page_size, offset


def page_payload(items: list, total: int, page: int, page_size: int) -> dict:
    return {
        "list": items,
        "total": int(total or 0),
        "page": page,
        "page_size": page_size,
        "has_more": page * page_size < int(total or 0),
    }
