from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    AppUser,
    Banner,
    CheckinRecord,
    GatherProduct,
    GatherTab,
    MallGoods,
    NyeStore,
    Order,
    PointLedger,
    RoomSlot,
    Store,
    UserCoupon,
)
from ..schemas import OrderCreateIn, OkResponse, WxLoginIn
from ..utils import STATUS_TEXT, get_config, loads

router = APIRouter(prefix="/api/v1", tags=["miniapp"])


def _user_by_openid(db: Session, openid: str) -> Optional[AppUser]:
    if not openid:
        return None
    return db.query(AppUser).filter(AppUser.openid == openid).first()


def _ensure_user(db: Session, openid: str, nickname: str = "微信用户", avatar: str = "", phone: str = "") -> AppUser:
    user = _user_by_openid(db, openid)
    if user:
        return user
    user = AppUser(openid=openid, nickname=nickname or "微信用户", avatar=avatar or "", phone=phone or "", points=12)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _product_out(row: GatherProduct) -> dict:
    return {
        "id": row.id,
        "tab": row.tab,
        "detailId": row.detail_id,
        "cover": row.cover,
        "title": row.title,
        "tag": row.tag,
        "tags": loads(row.tags, []),
        "soldText": row.sold_text,
        "price": row.price,
        "originPrice": row.origin_price,
    }


def _nye_out(row: NyeStore) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "cover": row.cover,
        "price": row.price,
        "originPrice": row.origin_price,
        "tag": row.tag,
        "address": row.address,
        "route": row.route,
        "lat": row.lat,
        "lng": row.lng,
        "banners": loads(row.banners, []),
        "detailImages": loads(row.detail_images, []),
        "recentBuy": loads(row.recent_buy, {}),
        "openStart": row.open_start,
        "openEnd": row.open_end,
    }


def _order_out(row: Order) -> dict:
    return {
        "id": row.id,
        "type": row.type,
        "storeId": row.store_id,
        "storeName": row.store_name,
        "title": row.title,
        "spec": row.spec,
        "cover": row.cover,
        "quantity": row.quantity,
        "price": row.price,
        "amount": row.amount,
        "status": row.status,
        "statusText": row.status_text,
        "contactName": row.contact_name,
        "contactPhone": row.contact_phone,
        "people": row.people,
        "remark": row.remark,
        "roomDate": row.room_date,
        "roomSlot": row.room_slot,
        "createdAt": row.created_at.isoformat() if row.created_at else None,
    }


def _slot_info(db: Session, store_id: str, date: str, slot: str) -> dict:
    site = get_config(db, "site", {}) or {}
    capacity_map = site.get("roomCapacity") or {"lunch": 4, "dinner": 8}
    row = (
        db.query(RoomSlot)
        .filter(RoomSlot.store_id == store_id, RoomSlot.date == date, RoomSlot.slot == slot)
        .first()
    )
    if not row:
        capacity = int(capacity_map.get(slot, 4))
        booked = 0
    else:
        capacity = row.capacity
        booked = row.booked
    remain = max(0, capacity - booked)
    full = remain <= 0
    return {
        "storeId": store_id,
        "date": date,
        "slot": slot,
        "capacity": capacity,
        "booked": booked,
        "remain": remain,
        "full": full,
        "statusText": "已满" if full else (f"仅剩{remain}间" if remain <= 2 else f"剩余{remain}间"),
    }


@router.get("/health")
def health():
    return {"ok": True, "service": "gather-club"}


@router.post("/auth/wx-login")
def wx_login(payload: WxLoginIn, db: Session = Depends(get_db)):
    # 云托管正式环境可换成 code2session；本地/演示用 code 或固定 openid
    openid = payload.code.strip() if payload.code else f"demo_{int(datetime.utcnow().timestamp())}"
    if len(openid) < 8:
        openid = f"demo_{openid or 'guest'}"
    user = _ensure_user(db, openid, payload.nickname, payload.avatar, payload.phone)
    if payload.nickname:
        user.nickname = payload.nickname
    if payload.avatar:
        user.avatar = payload.avatar
    if payload.phone:
        user.phone = payload.phone
    db.commit()
    db.refresh(user)
    return {
        "openid": user.openid,
        "user": {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "phone": user.phone,
            "points": user.points,
            "vipLevel": user.vip_level,
            "vip": f"{user.vip_level}会员",
        },
    }


@router.get("/home")
def home(db: Session = Depends(get_db)):
    banners = (
        db.query(Banner)
        .filter(Banner.enabled.is_(True))
        .order_by(Banner.sort.asc(), Banner.id.asc())
        .all()
    )
    stores = (
        db.query(Store)
        .filter(Store.enabled.is_(True))
        .order_by(Store.sort.asc(), Store.id.asc())
        .all()
    )
    site = get_config(db, "site", {}) or {}
    return {
        "banners": [{"id": b.id, "image": b.image, "link": b.link} for b in banners],
        "stores": [
            {
                "id": s.id,
                "name": s.name,
                "cover": s.cover,
                "address": s.address,
                "route": s.route,
                "phone": s.phone,
                "lat": s.lat,
                "lng": s.lng,
            }
            for s in stores
        ],
        "site": site,
    }


@router.get("/gather")
def gather(db: Session = Depends(get_db)):
    tabs = (
        db.query(GatherTab)
        .filter(GatherTab.enabled.is_(True))
        .order_by(GatherTab.sort.asc(), GatherTab.id.asc())
        .all()
    )
    products = (
        db.query(GatherProduct)
        .filter(GatherProduct.enabled.is_(True))
        .order_by(GatherProduct.sort.asc(), GatherProduct.id.asc())
        .all()
    )
    return {
        "tabs": [
            {"key": t.key, "name": t.name, "showSold": t.show_sold}
            for t in tabs
        ],
        "products": [_product_out(p) for p in products],
    }


@router.get("/nye")
def nye_list(db: Session = Depends(get_db)):
    rows = (
        db.query(NyeStore)
        .filter(NyeStore.enabled.is_(True))
        .order_by(NyeStore.sort.asc(), NyeStore.id.asc())
        .all()
    )
    return {
        "list": [
            {
                "id": r.id,
                "name": r.name,
                "cover": r.cover,
                "price": r.price,
                "originPrice": r.origin_price,
            }
            for r in rows
        ]
    }


@router.get("/nye/{nye_id}")
def nye_detail(nye_id: str, db: Session = Depends(get_db)):
    row = db.query(NyeStore).filter(NyeStore.id == nye_id, NyeStore.enabled.is_(True)).first()
    if not row:
        raise HTTPException(status_code=404, detail="门店不存在")
    detail = _nye_out(row)
    price = detail["price"] or 2388
    cover = detail["cover"]
    detail["packages"] = [
        {"id": 1, "name": "喜气羊羊宴 (10-12人) 午市大厅", "meal": "喜气羊羊宴", "time": "10:00-14:00", "price": price, "people": 12, "cover": cover, "disabled": False},
        {"id": 2, "name": "喜气羊羊宴 (10-12人) 晚市大厅", "meal": "喜气羊羊宴", "time": "17:00-21:00", "price": price + 200, "people": 12, "cover": cover, "disabled": False},
        {"id": 3, "name": "喜气羊羊宴 (8-10人) 午市包厢", "meal": "喜气羊羊宴", "time": "10:00-14:00", "price": price + 300, "people": 10, "cover": "/static/nye/shibo.jpg", "disabled": False},
        {"id": 4, "name": "团圆家宴 (8-10人) 晚市大厅", "meal": "团圆家宴", "time": "17:00-21:00", "price": price + 100, "people": 10, "cover": "/static/nye/yaxin.jpg", "disabled": False},
        {"id": 5, "name": "团圆家宴 (6-8人) 午市包厢", "meal": "团圆家宴", "time": "10:00-14:00", "price": price - 400, "people": 8, "cover": "/static/nye/yaxin.jpg", "disabled": False},
        {"id": 6, "name": "名羊四海宴 (12-14人) 午市大厅", "meal": "名羊四海宴", "time": "10:00-14:00", "price": price + 1100, "people": 14, "cover": "/static/nye/xinzhuang.jpg", "disabled": False},
        {"id": 7, "name": "名羊四海宴 (16人) 晚市大厅", "meal": "名羊四海宴", "time": "17:00-21:00", "price": price + 2100, "people": 16, "cover": "/static/nye/xinzhuang.jpg", "disabled": True},
        {"id": 8, "name": "名羊四海宴 (16人) 晚市包厢", "meal": "名羊四海宴", "time": "17:00-21:00", "price": price + 2100, "people": 16, "cover": "/static/nye/xinzhuang.jpg", "disabled": True},
    ]
    return detail


@router.get("/mall/goods")
def mall_goods(db: Session = Depends(get_db)):
    rows = (
        db.query(MallGoods)
        .filter(MallGoods.enabled.is_(True))
        .order_by(MallGoods.sort.asc(), MallGoods.id.asc())
        .all()
    )
    site = get_config(db, "site", {}) or {}
    return {
        "rules": site.get("mallRules") or [],
        "list": [
            {
                "id": r.id,
                "name": r.name,
                "title": r.title or r.name,
                "cover": r.cover,
                "cost": r.cost,
                "usage": r.usage,
                "valid": r.valid,
                "stock": r.stock,
            }
            for r in rows
        ],
    }


@router.get("/mall/goods/{goods_id}")
def mall_goods_detail(goods_id: int, db: Session = Depends(get_db)):
    row = db.query(MallGoods).filter(MallGoods.id == goods_id, MallGoods.enabled.is_(True)).first()
    if not row:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {
        "id": row.id,
        "name": row.name,
        "title": row.title or row.name,
        "cover": row.cover,
        "cost": row.cost,
        "usage": row.usage,
        "valid": row.valid,
        "stock": row.stock,
    }


@router.get("/rooms/availability")
def room_availability(
    store_id: str = Query(...),
    date: str = Query(...),
    slot: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    if slot:
        return _slot_info(db, store_id, date, slot)
    lunch = _slot_info(db, store_id, date, "lunch")
    dinner = _slot_info(db, store_id, date, "dinner")
    remain = lunch["remain"] + dinner["remain"]
    return {
        "date": date,
        "lunch": lunch,
        "dinner": dinner,
        "remain": remain,
        "full": lunch["full"] and dinner["full"],
    }


@router.get("/rooms/month")
def room_month(
    store_id: str = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    import calendar

    today = datetime.utcnow().strftime("%Y-%m-%d")
    days = calendar.monthrange(year, month)[1]
    result = {}
    for d in range(1, days + 1):
        date = f"{year}-{month:02d}-{d:02d}"
        lunch = _slot_info(db, store_id, date, "lunch")
        dinner = _slot_info(db, store_id, date, "dinner")
        remain = lunch["remain"] + dinner["remain"]
        past = date < today
        result[date] = {
            "date": date,
            "past": past,
            "lunch": lunch,
            "dinner": dinner,
            "remain": remain,
            "full": (not past) and lunch["full"] and dinner["full"],
            "open": not past,
            "statusText": "" if past else ("已满" if lunch["full"] and dinner["full"] else f"剩{remain}"),
        }
    return result


@router.get("/orders")
def list_orders(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid
    q = db.query(Order).order_by(Order.created_at.desc())
    if oid:
        q = q.filter(Order.openid == oid)
    rows = q.limit(100).all()
    return {"list": [_order_out(r) for r in rows]}


@router.post("/orders")
def create_order(
    payload: OrderCreateIn,
    x_openid: str = Header(default="", alias="X-Openid"),
    db: Session = Depends(get_db),
):
    openid = payload.openid or x_openid or "anonymous"
    user = _ensure_user(db, openid)
    order_id = f"o{int(datetime.utcnow().timestamp() * 1000)}"

    if payload.room_date and payload.room_slot and payload.store_id:
        info = _slot_info(db, payload.store_id, payload.room_date, payload.room_slot)
        if info["full"] or info["remain"] < 1:
            raise HTTPException(status_code=400, detail="该时段包房已满，请换日期或时段")
        row = (
            db.query(RoomSlot)
            .filter(
                RoomSlot.store_id == payload.store_id,
                RoomSlot.date == payload.room_date,
                RoomSlot.slot == payload.room_slot,
            )
            .first()
        )
        if not row:
            row = RoomSlot(
                store_id=payload.store_id,
                date=payload.room_date,
                slot=payload.room_slot,
                capacity=info["capacity"],
                booked=0,
            )
            db.add(row)
            db.flush()
        row.booked += 1

    order = Order(
        id=order_id,
        user_id=user.id,
        openid=openid,
        type=payload.type,
        store_id=payload.store_id,
        store_name=payload.store_name,
        title=payload.title,
        spec=payload.spec,
        cover=payload.cover,
        quantity=payload.quantity,
        price=payload.price,
        amount=payload.amount or payload.price,
        status="pending",
        status_text=STATUS_TEXT["pending"],
        contact_name=payload.contact_name,
        contact_phone=payload.contact_phone,
        people=payload.people,
        remark=payload.remark,
        room_date=payload.room_date,
        room_slot=payload.room_slot,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return _order_out(order)


@router.post("/orders/{order_id}/pay")
def pay_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="订单状态不可支付")
    order.status = "paid"
    order.status_text = STATUS_TEXT["paid"]
    db.commit()
    return _order_out(order)


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status not in ("pending", "paid"):
        raise HTTPException(status_code=400, detail="订单状态不可取消")
    if order.room_date and order.room_slot and order.store_id:
        row = (
            db.query(RoomSlot)
            .filter(
                RoomSlot.store_id == order.store_id,
                RoomSlot.date == order.room_date,
                RoomSlot.slot == order.room_slot,
            )
            .first()
        )
        if row and row.booked > 0:
            row.booked -= 1
    order.status = "cancelled"
    order.status_text = STATUS_TEXT["cancelled"]
    db.commit()
    return _order_out(order)


@router.get("/user/profile")
def user_profile(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid
    if not oid:
        raise HTTPException(status_code=400, detail="缺少 openid")
    user = _ensure_user(db, oid)
    return {
        "id": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "phone": user.phone,
        "points": user.points,
        "vipLevel": user.vip_level,
        "vip": f"{user.vip_level}会员",
    }


@router.get("/user/points")
def user_points(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid
    user = _ensure_user(db, oid or "anonymous")
    rows = (
        db.query(PointLedger)
        .filter(PointLedger.user_id == user.id)
        .order_by(PointLedger.created_at.desc())
        .limit(100)
        .all()
    )
    return {
        "balance": user.points,
        "list": [
            {
                "id": r.id,
                "title": r.title,
                "value": r.value,
                "time": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
            }
            for r in rows
        ],
    }


@router.get("/user/coupons")
def user_coupons(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid
    user = _ensure_user(db, oid or "anonymous")
    rows = db.query(UserCoupon).filter(UserCoupon.user_id == user.id).order_by(UserCoupon.id.desc()).all()
    grouped = {"unused": [], "used": [], "expired": []}
    for r in rows:
        bucket = r.status if r.status in grouped else "unused"
        grouped[bucket].append(
            {
                "id": r.id,
                "name": r.name,
                "amount": r.amount,
                "condition": r.condition,
                "expire": r.expire,
            }
        )
    return grouped


@router.post("/checkin")
def checkin(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    makeup: bool = Query(False),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid
    user = _ensure_user(db, oid or "anonymous")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    exists = (
        db.query(CheckinRecord)
        .filter(CheckinRecord.user_id == user.id, CheckinRecord.date == today)
        .first()
    )
    if exists and not makeup:
        return OkResponse(ok=False, message="今日已签到", data={"points": 0, "balance": user.points})
    points = 2
    if not exists:
        db.add(CheckinRecord(user_id=user.id, date=today, points=points, is_makeup=makeup))
    user.points += points
    db.add(PointLedger(user_id=user.id, title="每日签到" if not makeup else "补签", value=points))
    db.commit()
    db.refresh(user)
    return OkResponse(ok=True, message="签到成功", data={"points": points, "balance": user.points})


@router.get("/checkin/month")
def checkin_month(
    year: int = Query(...),
    month: int = Query(...),
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid
    user = _ensure_user(db, oid or "anonymous")
    prefix = f"{year}-{month:02d}"
    rows = (
        db.query(CheckinRecord)
        .filter(CheckinRecord.user_id == user.id, CheckinRecord.date.like(f"{prefix}%"))
        .all()
    )
    return {
        "dates": [r.date for r in rows],
        "signedDays": len(rows),
        "monthPoints": sum(r.points for r in rows),
    }
