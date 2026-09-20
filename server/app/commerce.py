"""订单成交后的销量 / 会员桌数统计。"""

from __future__ import annotations

import calendar
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from .models import AppUser, GatherProduct, NyeStore, Order, PointLedger, RoomSlot
from .utils import dumps, get_config, loads, today_cn

TABLE_ORDER_TYPES = ("room", "nye", "recommend", "gather")
TABLE_COUNTED_STATUSES = ("paid", "completed")


def get_checkin_config(db: Session) -> dict:
    from .cms_data import CHECKIN_CONFIG

    raw = get_config(db, "checkin") or {}
    if not isinstance(raw, dict):
        raw = {}
    daily = int(raw.get("dailyPoints") if raw.get("dailyPoints") is not None else CHECKIN_CONFIG["dailyPoints"])
    makeup = int(raw.get("makeupPoints") if raw.get("makeupPoints") is not None else daily)
    full_bonus = int(
        raw.get("fullMonthBonus")
        if raw.get("fullMonthBonus") is not None
        else CHECKIN_CONFIG["fullMonthBonus"]
    )
    rules = str(raw.get("rules") or CHECKIN_CONFIG["rules"] or "").strip()
    items = raw.get("milestones")
    if not isinstance(items, list) or not items:
        items = CHECKIN_CONFIG["milestones"]
    milestones = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            days = int(item.get("days") or 0)
            pts = int(item.get("points") or 0)
        except (TypeError, ValueError):
            continue
        if days <= 0 or pts < 0:
            continue
        label = str(item.get("label") or f"签到{days}天").strip() or f"签到{days}天"
        milestones.append({"days": days, "points": pts, "label": label})
    milestones.sort(key=lambda x: x["days"])
    return {
        "dailyPoints": max(0, daily),
        "makeupPoints": max(0, makeup),
        "fullMonthBonus": max(0, full_bonus),
        "milestones": milestones,
        "rules": rules
        or "每日签到可领取积分，当月累计签到可解锁额外奖励。漏签可用补签机会补回，每日仅一次。",
    }


def get_loyalty_config(db: Optional[Session] = None) -> dict:
    from .cms_data import LOYALTY_CONFIG

    raw = (get_config(db, "loyalty") or {}) if db is not None else {}
    if not isinstance(raw, dict):
        raw = {}
    base = dict(LOYALTY_CONFIG)
    vip = dict(base.get("vipTables") or {})
    if isinstance(raw.get("vipTables"), dict):
        for k, v in raw["vipTables"].items():
            try:
                vip[str(k).upper()] = int(v)
            except (TypeError, ValueError):
                pass
    return {
        "welcomePoints": int(raw.get("welcomePoints") if raw.get("welcomePoints") is not None else base["welcomePoints"]),
        "earnRateDefault": float(
            raw.get("earnRateDefault") if raw.get("earnRateDefault") is not None else base["earnRateDefault"]
        ),
        "earnRateV3": float(raw.get("earnRateV3") if raw.get("earnRateV3") is not None else base["earnRateV3"]),
        "firstOrderRate": float(
            raw.get("firstOrderRate") if raw.get("firstOrderRate") is not None else base["firstOrderRate"]
        ),
        "birthdayMultiplier": float(
            raw.get("birthdayMultiplier")
            if raw.get("birthdayMultiplier") is not None
            else base["birthdayMultiplier"]
        ),
        "vipTables": {
            "V1": int(vip.get("V1") or 1),
            "V2": int(vip.get("V2") or 2),
            "V3": int(vip.get("V3") or 5),
        },
        "roomPrice": float(raw.get("roomPrice") if raw.get("roomPrice") is not None else base["roomPrice"]),
    }


def add_points(db: Session, user: AppUser, title: str, value: int) -> int:
    if not user or not value:
        return int(getattr(user, "points", 0) or 0) if user else 0
    user.points = max(0, int(user.points or 0) + int(value))
    db.add(PointLedger(user_id=user.id, title=title, value=int(value)))
    return user.points


def _birthday_month_match(birthday: str) -> bool:
    raw = (birthday or "").strip()
    if len(raw) < 7:
        return False
    try:
        return int(raw[5:7]) == int(today_cn()[5:7])
    except (TypeError, ValueError):
        return False


def order_earn_points(
    amount: float,
    vip_level: str = "V0",
    first_order: bool = False,
    birthday: str = "",
    db: Optional[Session] = None,
) -> int:
    amt = max(0.0, float(amount or 0))
    if amt <= 0:
        return 0
    cfg = get_loyalty_config(db)
    level = (vip_level or "V0").upper()
    if first_order:
        rate = float(cfg["firstOrderRate"])
    elif level == "V3":
        rate = float(cfg["earnRateV3"])
    else:
        rate = float(cfg["earnRateDefault"])
    if _birthday_month_match(birthday) and float(cfg["birthdayMultiplier"]) > 1:
        rate *= float(cfg["birthdayMultiplier"])
    return max(0, int(round(amt * rate)))


def award_order_points(db: Session, order: Order, user: Optional[AppUser]) -> int:
    if not user or not order:
        return 0
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
    gained = order_earn_points(
        order.amount or order.price or 0,
        user.vip_level or "V0",
        paid_before == 0,
        getattr(user, "birthday", "") or "",
        db,
    )
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


def reverse_order_points(db: Session, order: Order, user: Optional[AppUser]) -> int:
    if not user or not order:
        return 0
    extra = loads(order.extra or "{}", {}) or {}
    gained = int(extra.get("pointsAwarded") or 0)
    if gained <= 0 or extra.get("pointsReversed"):
        return 0
    add_points(db, user, "退款扣回-消费积分", -gained)
    extra["pointsReversed"] = True
    order.extra = dumps(extra)
    return gained


def reverse_sold_on_refund(db: Session, order: Order) -> None:
    extra = loads(order.extra or "{}", {}) or {}
    if extra.get("soldReversed") or not extra.get("soldBumped"):
        return
    qty = max(1, int(order.quantity or 1))
    if order.type == "gather" and order.store_id:
        product = db.query(GatherProduct).filter(GatherProduct.id == order.store_id).first()
        if product:
            product.sold_count = max(0, int(getattr(product, "sold_count", 0) or 0) - qty)
    elif order.type == "nye" and order.store_id:
        store = db.query(NyeStore).filter(NyeStore.id == order.store_id).first()
        if store:
            store.sold_count = max(0, int(getattr(store, "sold_count", 0) or 0) - qty)
    extra["soldReversed"] = True
    order.extra = dumps(extra)


def release_room_if_needed(db: Session, order: Order) -> None:
    if not (order.room_date and order.room_slot and order.store_id):
        return
    extra = loads(order.extra or "{}", {}) or {}
    if extra.get("roomReleased"):
        return
    slot = (
        db.query(RoomSlot)
        .filter(
            RoomSlot.store_id == order.store_id,
            RoomSlot.date == order.room_date,
            RoomSlot.slot == order.room_slot,
        )
        .first()
    )
    if slot and slot.booked > 0:
        slot.booked -= 1
    extra["roomReleased"] = True
    order.extra = dumps(extra)


def award_checkin_milestones(db: Session, user: AppUser, year: int, month: int, signed_days: int) -> list[int]:
    awarded = []
    if not user:
        return awarded
    cfg = get_checkin_config(db)
    prefix = f"{year}-{month:02d}"
    full_days = calendar.monthrange(year, month)[1]
    milestones = [(m["days"], m["points"], f"{m['label']}奖励") for m in cfg["milestones"]]
    if cfg["fullMonthBonus"] > 0 and signed_days >= full_days:
        milestones.append((full_days, cfg["fullMonthBonus"], "整月满签奖励"))
    for need, pts, title in milestones:
        if signed_days < need or pts <= 0:
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


def vip_level_from_tables(n: int, db: Optional[Session] = None) -> str:
    cfg = get_loyalty_config(db)
    t = cfg["vipTables"]
    if n >= int(t.get("V3") or 5):
        return "V3"
    if n >= int(t.get("V2") or 2):
        return "V2"
    if n >= int(t.get("V1") or 1):
        return "V1"
    return "V0"


def sync_user_vip(db: Session, user: AppUser) -> str:
    if not user:
        return "V0"
    if getattr(user, "vip_manual", False):
        return (user.vip_level or "V0").upper()
    level = vip_level_from_tables(table_count(db, user.id), db)
    if (user.vip_level or "").upper() != level:
        user.vip_level = level
    return level


def mask_nickname(name: str) -> str:
    raw = (name or "微信用户").strip() or "微信用户"
    return f"{raw[0]}********"


def _relative_buy_text(created_at: Optional[datetime], qty: int) -> str:
    qty = max(1, int(qty or 1))
    if not created_at:
        return f"刚刚买了{qty}件"
    delta = datetime.utcnow() - created_at
    seconds = max(0, int(delta.total_seconds()))
    if seconds < 3600:
        return f"{max(1, seconds // 60)}分钟前买了{qty}件"
    if seconds < 86400:
        return f"{max(1, seconds // 3600)}小时前买了{qty}件"
    return f"{max(1, seconds // 86400)}天前买了{qty}件"


def nye_recent_buy(db: Session, store: NyeStore) -> dict:
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
    return {
        "countText": f"近一周{week_n}人买过",
        "avatar": avatar,
        "name": mask_nickname(user.nickname if user else ""),
        "timeText": _relative_buy_text(last.created_at, last.quantity),
    }


def bump_sold_on_paid(db: Session, order: Order, user: Optional[AppUser] = None) -> None:
    extra = loads(order.extra or "{}", {}) or {}
    if extra.get("soldBumped"):
        if user:
            sync_user_vip(db, user)
        return
    qty = max(1, int(order.quantity or 1))
    if order.type == "gather" and order.store_id:
        product = db.query(GatherProduct).filter(GatherProduct.id == order.store_id).first()
        if product:
            product.sold_count = int(getattr(product, "sold_count", 0) or 0) + qty
    elif order.type == "nye" and order.store_id:
        store = db.query(NyeStore).filter(NyeStore.id == order.store_id).first()
        if store:
            store.sold_count = int(getattr(store, "sold_count", 0) or 0) + qty
            store.recent_buy = dumps(nye_recent_buy(db, store))
    extra["soldBumped"] = True
    order.extra = dumps(extra)
    uid = order.user_id or (user.id if user else 0)
    if user is None and uid:
        user = db.query(AppUser).filter(AppUser.id == uid).first()
    if user:
        sync_user_vip(db, user)
