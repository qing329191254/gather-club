import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from .models import SiteConfig

CN_TZ = timezone(timedelta(hours=8))


def now_cn() -> datetime:
    return datetime.now(CN_TZ)


def today_cn() -> str:
    return now_cn().strftime("%Y-%m-%d")


def month_cn() -> str:
    return now_cn().strftime("%Y-%m")


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def loads(raw: str | None, default: Any = None) -> Any:
    if raw is None or raw == "":
        return default if default is not None else {}
    try:
        data = json.loads(raw)
    except Exception:
        return default if default is not None else {}
    if data is None:
        return default if default is not None else {}
    return data


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
    "paid": "待核销",
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


def alloc_verify_code(db: Session) -> str:
    """8 位数字核销码，订单与到店券全局不重复。"""
    import secrets

    from .models import Order, UserCoupon

    for _ in range(40):
        code = f"{secrets.randbelow(90000000) + 10000000}"
        taken_order = db.query(Order.id).filter(Order.verify_code == code).first()
        taken_coupon = db.query(UserCoupon.id).filter(UserCoupon.verify_code == code).first()
        if not taken_order and not taken_coupon:
            return code
    raise RuntimeError("核销码生成失败")


def ensure_order_verify_code(db: Session, order) -> str:
    code = (getattr(order, "verify_code", "") or "").strip()
    if code:
        return code
    if getattr(order, "status", "") != "paid":
        return ""
    order.verify_code = alloc_verify_code(db)
    return order.verify_code


def ensure_coupon_verify_code(db: Session, row) -> str:
    code = (getattr(row, "verify_code", "") or "").strip()
    if code:
        return code
    if getattr(row, "status", "") != "unused":
        return ""
    row.verify_code = alloc_verify_code(db)
    return row.verify_code
