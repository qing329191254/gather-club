"""订单成交后的销量 / 会员桌数统计。"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from .models import AppUser, GatherProduct, NyeStore, Order
from .utils import dumps, loads

TABLE_ORDER_TYPES = ("room", "nye", "recommend", "gather")
TABLE_COUNTED_STATUSES = ("paid", "completed")


def format_sold_text(count: int) -> str:
    n = max(0, int(count or 0))
    if n <= 0:
        return ""
    if n >= 10000:
        wan = n / 10000
        if abs(wan - round(wan)) < 1e-9:
            return f"{int(round(wan))}万+人已购"
        text = f"{wan:.1f}".rstrip("0").rstrip(".")
        return f"{text}万+人已购"
    return f"{n}人已购"


def display_sold_text(sold_count: int, sold_text: str = "") -> str:
    """手动设置了已购文案则用手动文案；否则按真实销量生成。"""
    custom = (sold_text or "").strip()
    if custom:
        return custom
    return format_sold_text(sold_count)


def table_count(db: Session, user_id: int, days: int = 365) -> int:
    if not user_id:
        return 0
    since = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(Order)
        .filter(
            Order.user_id == user_id,
            Order.status.in_(TABLE_COUNTED_STATUSES),
            Order.type.in_(TABLE_ORDER_TYPES),
            Order.created_at >= since,
        )
        .count()
    )


def vip_level_from_tables(n: int) -> str:
    if n >= 5:
        return "V3"
    if n >= 2:
        return "V2"
    if n >= 1:
        return "V1"
    return "V0"


def sync_user_vip(db: Session, user: AppUser) -> str:
    level = vip_level_from_tables(table_count(db, user.id))
    if (user.vip_level or "").upper() != level:
        user.vip_level = level
    return level


def mask_nickname(name: str) -> str:
    raw = (name or "微信用户").strip() or "微信用户"
    head = raw[0]
    return f"{head}********)"


def _relative_buy_text(created_at: Optional[datetime], qty: int) -> str:
    qty = max(1, int(qty or 1))
    if not created_at:
        return f"刚刚买了{qty}件"
    delta = datetime.utcnow() - created_at
    seconds = max(0, int(delta.total_seconds()))
    if seconds < 3600:
        mins = max(1, seconds // 60)
        return f"{mins}分钟前买了{qty}件"
    if seconds < 86400:
        hours = max(1, seconds // 3600)
        return f"{hours}小时前买了{qty}件"
    days = max(1, seconds // 86400)
    return f"{days}天前买了{qty}件"


def nye_recent_buy(db: Session, store: NyeStore) -> dict:
    """年夜饭详情「近一周买过」：按实付订单实时生成，无订单时回退到后台配置。"""
    since = datetime.utcnow() - timedelta(days=7)
    q = (
        db.query(Order)
        .filter(
            Order.type == "nye",
            Order.store_id == store.id,
            Order.status.in_(TABLE_COUNTED_STATUSES),
            Order.created_at >= since,
        )
        .order_by(Order.created_at.desc())
    )
    week_n = q.count()
    last = q.first()
    fallback = loads(getattr(store, "recent_buy", None) or "{}", {}) or {}
    if not last:
        if fallback:
            return fallback
        return {
            "countText": "近一周0人买过",
            "avatar": "/static/icons/avatar-default.png",
            "name": "微信用户",
            "timeText": "",
        }

    user = db.query(AppUser).filter(AppUser.id == last.user_id).first()
    avatar = (user.avatar if user and user.avatar else "") or "/static/icons/avatar-default.png"
    name = mask_nickname(user.nickname if user else "")
    return {
        "countText": f"近一周{week_n}人买过",
        "avatar": avatar,
        "name": name,
        "timeText": _relative_buy_text(last.created_at, last.quantity),
    }


def bump_sold_on_paid(db: Session, order: Order, user: Optional[AppUser] = None) -> None:
    """支付成功后累加商品销量，并刷新会员等级。"""
    qty = max(1, int(order.quantity or 1))
    if order.type == "gather" and order.store_id:
        product = db.query(GatherProduct).filter(GatherProduct.id == order.store_id).first()
        if product:
            product.sold_count = int(getattr(product, "sold_count", 0) or 0) + qty
    elif order.type == "nye" and order.store_id:
        store = db.query(NyeStore).filter(NyeStore.id == order.store_id).first()
        if store:
            store.sold_count = int(getattr(store, "sold_count", 0) or 0) + qty
            # 同步一份到 recent_buy，便于后台查看；小程序侧仍实时计算
            store.recent_buy = dumps(nye_recent_buy(db, store))

    uid = order.user_id or (user.id if user else 0)
    if user is None and uid:
        user = db.query(AppUser).filter(AppUser.id == uid).first()
    if user:
        sync_user_vip(db, user)
