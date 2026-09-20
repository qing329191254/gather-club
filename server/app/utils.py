import json
import re
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


def coupon_is_expired(expire: str, now: datetime | None = None) -> bool:
    """月份键 YYYY-MM 在当月最后一天 23:59:59 后失效；纯文案有效期不自动过期。"""
    raw = (expire or "").strip()
    current = now or now_cn()
    month = re.fullmatch(r"(\d{4})-(\d{2})", raw)
    if month:
        year, mon = int(month.group(1)), int(month.group(2))
        if not 1 <= mon <= 12:
            return False
        if mon == 12:
            end = datetime(year + 1, 1, 1, tzinfo=CN_TZ)
        else:
            end = datetime(year, mon + 1, 1, tzinfo=CN_TZ)
        return current >= end
    day = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", raw)
    if day:
        return current.strftime("%Y-%m-%d") > raw
    stamped = re.fullmatch(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})", raw)
    if stamped:
        try:
            end = datetime.strptime(
                f"{stamped.group(1)} {stamped.group(2)}", "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=CN_TZ)
        except ValueError:
            return False
        return current > end
    return False


def mark_coupon_expired(row) -> bool:
    if getattr(row, "status", "") != "unused":
        return False
    if not coupon_is_expired(getattr(row, "expire", "") or ""):
        return False
    row.status = "expired"
    return True


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
    "refund_pending": "待退款",
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
