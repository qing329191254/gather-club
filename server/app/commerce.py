"""订单成交后的销量 / 会员桌数统计。"""

from __future__ import annotations

import calendar
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from .models import AppUser, GatherProduct, NyeStore, Order, PointLedger
from .utils import dumps, loads

TABLE_ORDER_TYPES = ("room", "nye", "recommend", "gather")
TABLE_COUNTED_STATUSES = ("paid", "completed")

# 签到里程碑奖励（与小程序签到页一致）
CHECKIN_MILESTONES = (
    (5, 2, "签到5天奖励"),
    (15, 15, "签到15天奖励"),
    (25, 25, "签到25天奖励"),
)


def add_points(db: Session, user: AppUser, title: str, value: int) -> int:
    """增减积分并记流水；value 可为负（兑换）。返回变动后余额。"""
    if not user or not value:
        return int(getattr(user, "points", 0) or 0) if user else 0
    user.points = max(0, int(user.points or 0) + int(value))
    db.add(PointLedger(user_id=user.id, title=title, value=int(value)))
    return user.points


def order_earn_points(amount: float, vip_level: str = "V0", first_order: bool = False) -> int:
    """消费积分：默认 0.5 倍；V3 为 1 倍；首单固定 0.5 倍。"""
    amt = max(0.0, float(amount or 0))
    if amt <= 0:
        return 0
    level = (vip_level or "V0").upper()
    rate = 0.5 if first_order or level != "V3" else 1.0
    return max(0, int(round(amt * rate)))


def award_order_points(db: Session, order: Order, user: Optional[AppUser]) -> int:
    """支付成功发放消费积分。"""
    if not user or not order:
        return 0
    # 避免重复发放
    extra = loads(order.extra or "{}", {}) or {}
    if extra.get("pointsAwarded"):
        return int(extra.get("pointsAwarded") or 0)
    paid_before = (
        db.query(Order)
        .filter(
            Order.user_id == user.id,
            Order.id != order.id,
            Order.status.in_(TABLE_COUNTED_STATUSES),
        )
        .count()
    )
    gained = order_earn_points(order.amount or order.price or 0, user.vip_level or "V0", paid_before == 0)
    if gained > 0:
        type_label = {
            "room": "包房预约",
            "nye": "年夜饭",
            "recommend": "订酒店",
            "gather": "去哪聚",
        }.get(order.type or "", "订单")
        add_points(db, user, f"消费获得-{type_label}", gained)
        extra["pointsAwarded"] = gained
        order.extra = dumps(extra)
    return gained


def award_checkin_milestones(db: Session, user: AppUser, year: int, month: int, signed_days: int) -> list[int]:
    """按当月累计签到天数发放里程碑奖励（每档每月只发一次）。"""
    awarded = []
    if not user:
        return awarded
    prefix = f"{year}-{month:02d}"
    full_days = calendar.monthrange(year, month)[1]
    milestones = list(CHECKIN_MILESTONES)
    if signed_days >= full_days:
        milestones.append((full_days, 30, "整月满签奖励"))
    for need, pts, title in milestones:
        if signed_days < need:
            continue
        month_title = f"{title}({prefix})"
        exists = (
            db.query(PointLedger)
            .filter(PointLedger.user_id == user.id, PointLedger.title == month_title)
            .first()
        )
        if exists:
            continue
        add_points(db, user, month_title, pts)
        awarded.append(pts)
    return awarded


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
