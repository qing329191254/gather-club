from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..cms_data import (
    AGREEMENTS,
    MEMBER_CONFIG,
    PRIVACY_COLLECT,
    PRIVACY_SHARE,
    RECOMMEND_BANNERS,
    default_nye_packages,
)
from ..database import get_db
from ..models import (
    Address,
    AppUser,
    Banner,
    CheckinRecord,
    Coupon,
    GatherProduct,
    GatherTab,
    MallGoods,
    NyeStore,
    Order,
    PointLedger,
    RecommendItem,
    RoomSlot,
    Store,
    UserCoupon,
    VideoFollow,
    VideoLive,
    VideoReserve,
)
from ..pay import (
    build_jsapi_payment,
    notify_fail_xml,
    notify_ok_xml,
    parse_notify,
    pay_configured,
    unified_order,
)
from ..schemas import OrderCreateIn, OkResponse, WxLoginIn, WxPhoneIn
from ..utils import STATUS_TEXT, dumps, get_config, loads, normalize_page, page_payload
from ..wx import code2session, phone_from_code, phone_from_encrypted, resolve_demo_openid, wx_configured

router = APIRouter(prefix="/api/v1", tags=["miniapp"])

TABLE_ORDER_TYPES = ("room", "nye", "recommend", "gather")


def _user_by_openid(db: Session, openid: str) -> Optional[AppUser]:
    if not openid:
        return None
    return db.query(AppUser).filter(AppUser.openid == openid).first()


def _ensure_user(db: Session, openid: str, nickname: str = "微信用户", avatar: str = "", phone: str = "") -> AppUser:
    user = _user_by_openid(db, openid)
    if user:
        if getattr(user, "cancelled", False):
            user.cancelled = False
            user.nickname = nickname or "微信用户"
            db.commit()
            db.refresh(user)
        return user
    user = AppUser(openid=openid, nickname=nickname or "微信用户", avatar=avatar or "", phone=phone or "", points=12)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _table_count(db: Session, user_id: int) -> int:
    return (
        db.query(Order)
        .filter(
            Order.user_id == user_id,
            Order.status == "paid",
            Order.type.in_(TABLE_ORDER_TYPES),
        )
        .count()
    )


def _user_out(user: AppUser, db: Optional[Session] = None) -> dict:
    out = {
        "id": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "phone": user.phone,
        "birthday": getattr(user, "birthday", "") or "",
        "hobby": getattr(user, "hobby", "") or "",
        "phoneEdited": bool(getattr(user, "phone_edited", False)),
        "points": user.points,
        "vipLevel": user.vip_level,
        "vip": f"{user.vip_level}会员",
    }
    if db is not None:
        out["tableCount"] = _table_count(db, user.id)
    return out


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


def _nye_packages_for(row: NyeStore) -> list:
    stored = loads(getattr(row, "packages", None) or "[]", [])
    if stored:
        return stored
    return default_nye_packages(row.price or 2388, row.cover or "")


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


def _mark_order_paid(db: Session, order: Order, extra_patch: Optional[dict] = None) -> Order:
    order.status = "paid"
    order.status_text = "待核销"
    extra = loads(order.extra or "{}", {})
    if extra_patch:
        extra.update(extra_patch)
    order.extra = dumps(extra)
    db.commit()
    db.refresh(order)
    return order


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
async def wx_login(payload: WxLoginIn, db: Session = Depends(get_db)):
    if wx_configured():
        session = await code2session(payload.code)
    else:
        session = resolve_demo_openid(payload.code)

    openid = session["openid"]
    user = _ensure_user(db, openid, payload.nickname, payload.avatar, payload.phone)
    if session.get("session_key"):
        user.session_key = session["session_key"]
    if session.get("unionid"):
        user.unionid = session["unionid"]
    if payload.nickname:
        user.nickname = payload.nickname
    if payload.avatar:
        user.avatar = payload.avatar
    # 明文手机号仅演示环境可直接写入；正式环境走 /auth/bind-phone
    if payload.phone and not wx_configured():
        user.phone = payload.phone
    db.commit()
    db.refresh(user)
    return {"openid": user.openid, "user": _user_out(user, db)}


@router.post("/auth/bind-phone")
async def bind_phone(
    payload: WxPhoneIn,
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid
    if payload.loginCode:
        if wx_configured():
            session = await code2session(payload.loginCode)
        else:
            session = resolve_demo_openid(payload.loginCode)
        oid = session["openid"]
        user = _ensure_user(db, oid)
        if session.get("session_key"):
            user.session_key = session["session_key"]
        if session.get("unionid"):
            user.unionid = session["unionid"]
        db.commit()
        db.refresh(user)
    else:
        if not oid:
            raise HTTPException(status_code=400, detail="缺少 openid，请先登录")
        user = _ensure_user(db, oid)

    if getattr(user, "cancelled", False):
        raise HTTPException(status_code=400, detail="账号已注销")
    if user.phone_edited and user.phone:
        return {"openid": user.openid, "user": _user_out(user, db), "message": "手机号已绑定"}

    if payload.code:
        if not wx_configured():
            raise HTTPException(status_code=400, detail="未配置 WX_APPID / WX_SECRET，无法换取手机号")
        phone = await phone_from_code(payload.code)
    elif payload.encryptedData and payload.iv:
        if not user.session_key:
            raise HTTPException(status_code=400, detail="会话已过期，请重新登录后再授权手机号")
        phone = phone_from_encrypted(user.session_key, payload.encryptedData, payload.iv)
    else:
        raise HTTPException(status_code=400, detail="缺少手机号授权数据")

    if user.phone and user.phone != phone and user.phone_edited:
        raise HTTPException(status_code=400, detail="手机号仅可修改一次")

    user.phone = phone
    user.phone_edited = True
    db.commit()
    db.refresh(user)
    return {"openid": user.openid, "user": _user_out(user, db), "message": "绑定成功"}


@router.get("/site")
def site_config(db: Session = Depends(get_db)):
    return get_config(db, "site", {}) or {}


@router.get("/stores")
def list_stores(db: Session = Depends(get_db)):
    stores = (
        db.query(Store)
        .filter(Store.enabled.is_(True))
        .order_by(Store.sort.asc(), Store.id.asc())
        .all()
    )
    return {
        "list": [
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
        ]
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
    detail["packages"] = _nye_packages_for(row)
    return detail


@router.get("/recommend")
def recommend_list(db: Session = Depends(get_db)):
    cfg = get_config(db, "recommend", {}) or {}
    banners = cfg.get("banners") or RECOMMEND_BANNERS
    rows = (
        db.query(RecommendItem)
        .filter(RecommendItem.enabled.is_(True))
        .order_by(RecommendItem.sort.asc(), RecommendItem.id.asc())
        .all()
    )
    return {
        "banners": banners,
        "list": [
            {"id": r.id, "name": r.name, "cover": r.cover, "price": r.price, "sort": r.sort}
            for r in rows
        ],
    }


@router.get("/gather/product/{product_id}")
def gather_product_detail(product_id: str, db: Session = Depends(get_db)):
    row = (
        db.query(GatherProduct)
        .filter(GatherProduct.id == product_id, GatherProduct.enabled.is_(True))
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="商品不存在")
    return _product_out(row)


@router.get("/agreements")
def agreements_all(db: Session = Depends(get_db)):
    data = get_config(db, "agreements") or AGREEMENTS
    return data


@router.get("/agreements/{agree_type}")
def agreement_one(agree_type: str, db: Session = Depends(get_db)):
    data = get_config(db, "agreements") or AGREEMENTS
    doc = (data or {}).get(agree_type)
    if not doc:
        raise HTTPException(status_code=404, detail="协议不存在")
    return doc


@router.get("/privacy/collect")
def privacy_collect(db: Session = Depends(get_db)):
    return get_config(db, "privacy_collect") or PRIVACY_COLLECT


@router.get("/privacy/share")
def privacy_share(db: Session = Depends(get_db)):
    return get_config(db, "privacy_share") or PRIVACY_SHARE


@router.get("/member/config")
def member_config(db: Session = Depends(get_db)):
    return get_config(db, "member") or MEMBER_CONFIG


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
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
):
    page, page_size, offset = normalize_page(page, page_size)
    oid = x_openid or openid
    q = db.query(Order).order_by(Order.created_at.desc())
    if oid:
        q = q.filter(Order.openid == oid)
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    return page_payload([_order_out(r) for r in rows], total, page, page_size)


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
async def pay_order(order_id: str, request: Request, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="订单状态不可支付")

    amount = float(order.amount or order.price or 0)
    # 金额为 0（如包房预约）或未配置商户号：直接 mock 标记已支付
    if amount <= 0 or not pay_configured():
        _mark_order_paid(db, order, {"mockPaid": True})
        return {**_order_out(order), "needPay": False}

    total_fee = int(round(amount * 100))
    client_ip = request.client.host if request.client else "127.0.0.1"
    result = await unified_order(
        openid=order.openid,
        out_trade_no=order.id,
        body=order.title or "天天俱乐部订单",
        total_fee=total_fee,
        client_ip=client_ip,
    )
    prepay_id = result["prepay_id"]
    extra = loads(order.extra or "{}", {})
    extra["prepay_id"] = prepay_id
    order.extra = dumps(extra)
    db.commit()
    payment = build_jsapi_payment(prepay_id)
    return {**_order_out(order), "needPay": True, "payment": payment}


@router.post("/pay/notify")
async def pay_notify(request: Request, db: Session = Depends(get_db)):
    body = (await request.body()).decode("utf-8", errors="ignore")
    try:
        data = parse_notify(body)
    except HTTPException:
        return Response(content=notify_fail_xml("SIGN"), media_type="application/xml")
    if data.get("return_code") != "SUCCESS" or data.get("result_code") != "SUCCESS":
        return Response(content=notify_fail_xml("RESULT"), media_type="application/xml")
    out_trade_no = data.get("out_trade_no") or ""
    order = db.query(Order).filter(Order.id == out_trade_no).first()
    if order and order.status == "pending":
        _mark_order_paid(
            db,
            order,
            {
                "transaction_id": data.get("transaction_id") or "",
                "prepay_id": loads(order.extra or "{}", {}).get("prepay_id"),
            },
        )
    return Response(content=notify_ok_xml(), media_type="application/xml")


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


@router.post("/mall/redeem")
def mall_redeem(
    payload: dict = Body(default={}),
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid or "anonymous"
    user = _ensure_user(db, oid)
    goods_id = int(payload.get("goodsId") or payload.get("goods_id") or 0)
    row = db.query(MallGoods).filter(MallGoods.id == goods_id, MallGoods.enabled.is_(True)).first()
    if not row:
        raise HTTPException(status_code=404, detail="商品不存在")
    if row.stock <= 0:
        raise HTTPException(status_code=400, detail="库存不足")
    if user.points < row.cost:
        raise HTTPException(status_code=400, detail="积分不足")
    user.points -= row.cost
    row.stock -= 1
    db.add(PointLedger(user_id=user.id, title=f"兑换-{row.name}", value=-row.cost))
    order = Order(
        id=f"mall{int(datetime.utcnow().timestamp() * 1000)}",
        user_id=user.id,
        openid=oid,
        type="mall",
        store_name="积分商城",
        title=row.title or row.name,
        spec=f"{row.cost}积分",
        cover=row.cover,
        quantity=1,
        price=0,
        amount=0,
        status="paid",
        status_text="待核销",
    )
    db.add(order)
    db.commit()
    db.refresh(user)
    return {
        "ok": True,
        "balance": user.points,
        "orderId": order.id,
        "message": "兑换成功",
    }


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
    return _profile_out(user, db)


def _profile_out(user: AppUser, db: Optional[Session] = None) -> dict:
    out = {
        "id": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "phone": user.phone,
        "birthday": getattr(user, "birthday", "") or "",
        "hobby": getattr(user, "hobby", "") or "",
        "phoneEdited": bool(getattr(user, "phone_edited", False)),
        "points": user.points,
        "vipLevel": user.vip_level,
        "vip": f"{user.vip_level}会员",
        "cancelled": bool(getattr(user, "cancelled", False)),
        "tableCount": 0,
    }
    if db is not None:
        out["tableCount"] = _table_count(db, user.id)
    return out


@router.put("/user/profile")
def update_profile(
    payload: dict = Body(default={}),
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid
    if not oid:
        raise HTTPException(status_code=400, detail="缺少 openid")
    user = _ensure_user(db, oid)
    if getattr(user, "cancelled", False):
        raise HTTPException(status_code=400, detail="账号已注销")
    if "nickname" in payload and payload["nickname"] is not None:
        user.nickname = str(payload["nickname"]).strip() or user.nickname
    if "avatar" in payload and payload["avatar"] is not None:
        user.avatar = str(payload["avatar"])
    if "birthday" in payload and payload["birthday"] is not None:
        user.birthday = str(payload["birthday"])
    if "hobby" in payload and payload["hobby"] is not None:
        user.hobby = str(payload["hobby"])
    if "phone" in payload and payload["phone"]:
        phone = str(payload["phone"]).strip()
        # 正式环境：仅允许回写已绑定的同一号码，改号必须走 /auth/bind-phone
        if wx_configured():
            if phone != (user.phone or ""):
                raise HTTPException(status_code=400, detail="请通过微信授权绑定手机号")
        else:
            if user.phone_edited and phone != user.phone:
                raise HTTPException(status_code=400, detail="手机号仅可修改一次")
            if phone != user.phone:
                user.phone = phone
                user.phone_edited = True
    db.commit()
    db.refresh(user)
    return _profile_out(user, db)


@router.post("/user/cancel")
def cancel_account(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid
    if not oid:
        raise HTTPException(status_code=400, detail="缺少 openid")
    user = _ensure_user(db, oid)
    user.cancelled = True
    user.nickname = "已注销用户"
    user.avatar = ""
    user.phone = ""
    db.commit()
    return OkResponse(message="账号已注销")


@router.get("/user/addresses")
def list_addresses(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, x_openid or openid or "anonymous")
    rows = (
        db.query(Address)
        .filter(Address.user_id == user.id)
        .order_by(Address.is_default.desc(), Address.id.desc())
        .all()
    )
    return {"list": [_address_out(r) for r in rows]}


def _address_out(row: Address) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "phone": row.phone,
        "region": row.region,
        "province": row.province,
        "city": row.city,
        "district": row.district,
        "detail": row.detail,
        "isDefault": row.is_default,
    }


@router.post("/user/addresses")
def create_address(
    payload: dict = Body(default={}),
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, x_openid or openid or "anonymous")
    is_default = bool(payload.get("isDefault") or payload.get("is_default"))
    if is_default:
        db.query(Address).filter(Address.user_id == user.id).update({"is_default": False})
    elif db.query(Address).filter(Address.user_id == user.id).count() == 0:
        is_default = True
    row = Address(
        user_id=user.id,
        name=str(payload.get("name") or ""),
        phone=str(payload.get("phone") or ""),
        region=str(payload.get("region") or ""),
        province=str(payload.get("province") or ""),
        city=str(payload.get("city") or ""),
        district=str(payload.get("district") or ""),
        detail=str(payload.get("detail") or ""),
        is_default=is_default,
    )
    if not row.region:
        row.region = "".join([row.province, row.city, row.district])
    db.add(row)
    db.commit()
    db.refresh(row)
    return _address_out(row)


@router.put("/user/addresses/{address_id}")
def update_address(
    address_id: int,
    payload: dict = Body(default={}),
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, x_openid or openid or "anonymous")
    row = db.query(Address).filter(Address.id == address_id, Address.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="地址不存在")
    is_default = payload.get("isDefault", payload.get("is_default", row.is_default))
    if is_default:
        db.query(Address).filter(Address.user_id == user.id).update({"is_default": False})
    row.name = str(payload.get("name", row.name) or "")
    row.phone = str(payload.get("phone", row.phone) or "")
    row.province = str(payload.get("province", row.province) or "")
    row.city = str(payload.get("city", row.city) or "")
    row.district = str(payload.get("district", row.district) or "")
    row.detail = str(payload.get("detail", row.detail) or "")
    row.region = str(payload.get("region") or "".join([row.province, row.city, row.district]))
    row.is_default = bool(is_default)
    db.commit()
    db.refresh(row)
    return _address_out(row)


@router.delete("/user/addresses/{address_id}")
def delete_address(
    address_id: int,
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, x_openid or openid or "anonymous")
    row = db.query(Address).filter(Address.id == address_id, Address.user_id == user.id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


@router.post("/user/addresses/{address_id}/default")
def set_default_address(
    address_id: int,
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, x_openid or openid or "anonymous")
    row = db.query(Address).filter(Address.id == address_id, Address.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="地址不存在")
    db.query(Address).filter(Address.user_id == user.id).update({"is_default": False})
    row.is_default = True
    db.commit()
    return _address_out(row)


@router.post("/user/coupons/claim")
def claim_coupon(
    payload: dict = Body(default={}),
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, x_openid or openid or "anonymous")
    coupon_id = payload.get("couponId") or payload.get("coupon_id")
    month_key = payload.get("month") or datetime.utcnow().strftime("%Y-%m")
    # 会员月券：默认领第一张启用优惠券，每月一次
    if coupon_id:
        coupon = db.query(Coupon).filter(Coupon.id == int(coupon_id), Coupon.enabled.is_(True)).first()
    else:
        coupon = db.query(Coupon).filter(Coupon.enabled.is_(True)).order_by(Coupon.id.asc()).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="暂无可领优惠券")
    exists = (
        db.query(UserCoupon)
        .filter(
            UserCoupon.user_id == user.id,
            UserCoupon.coupon_id == coupon.id,
            UserCoupon.expire == month_key,
        )
        .first()
    )
    if exists:
        return OkResponse(ok=False, message="本月已领取", data={"claimed": True})
    if coupon.total and coupon.claimed >= coupon.total:
        raise HTTPException(status_code=400, detail="优惠券已领完")
    row = UserCoupon(
        user_id=user.id,
        coupon_id=coupon.id,
        name=coupon.name,
        amount=coupon.amount,
        condition=coupon.condition,
        expire=month_key,
        status="unused",
    )
    coupon.claimed += 1
    db.add(row)
    db.commit()
    return OkResponse(
        message="领取成功",
        data={"id": row.id, "name": row.name, "amount": row.amount, "month": month_key},
    )


@router.get("/mall/records")
def mall_records(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
):
    page, page_size, offset = normalize_page(page, page_size)
    user = _ensure_user(db, x_openid or openid or "anonymous")
    q = (
        db.query(Order)
        .filter(Order.user_id == user.id, Order.type == "mall")
        .order_by(Order.created_at.desc())
    )
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    return page_payload(
        [
            {
                "id": r.id,
                "name": r.title,
                "cover": r.cover,
                "cost": int("".join(ch for ch in (r.spec or "") if ch.isdigit()) or 0),
                "time": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
                "status": r.status,
                "statusText": r.status_text,
            }
            for r in rows
        ],
        total,
        page,
        page_size,
    )


@router.get("/orders/{order_id}")
def order_detail(
    order_id: str,
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = x_openid or openid
    row = db.query(Order).filter(Order.id == order_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="订单不存在")
    if oid and row.openid and row.openid != oid:
        raise HTTPException(status_code=403, detail="无权查看")
    return _order_out(row)


@router.get("/user/points")
def user_points(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
):
    page, page_size, offset = normalize_page(page, page_size)
    oid = x_openid or openid
    user = _ensure_user(db, oid or "anonymous")
    q = (
        db.query(PointLedger)
        .filter(PointLedger.user_id == user.id)
        .order_by(PointLedger.created_at.desc())
    )
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    payload = page_payload(
        [
            {
                "id": r.id,
                "title": r.title,
                "value": r.value,
                "time": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
            }
            for r in rows
        ],
        total,
        page,
        page_size,
    )
    payload["balance"] = user.points
    return payload


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


def _live_out(row: VideoLive, reserved: bool = False) -> dict:
    return {
        "id": row.id,
        "status": row.status,
        "time": row.time_text,
        "line1": row.line1,
        "line2": row.line2,
        "points": row.points,
        "avatar": row.avatar,
        "noticeId": row.notice_id,
        "reserved": reserved,
    }


@router.get("/video")
def video_home(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    profile = get_config(db, "video", {}) or {}
    rows = (
        db.query(VideoLive)
        .filter(VideoLive.enabled.is_(True))
        .order_by(VideoLive.sort.asc(), VideoLive.id.asc())
        .all()
    )
    reserved_ids = set()
    followed = False
    oid = x_openid or openid
    if oid:
        user = _user_by_openid(db, oid)
        if user:
            followed = db.query(VideoFollow).filter(VideoFollow.user_id == user.id).first() is not None
            reserved_ids = {
                r.live_id
                for r in db.query(VideoReserve).filter(VideoReserve.user_id == user.id).all()
            }
    living = None
    lives = []
    for row in rows:
        item = _live_out(row, row.id in reserved_ids)
        if row.status == "living" and living is None:
            living = item
        else:
            lives.append(item)
    return {"profile": profile, "living": living, "lives": lives, "followed": followed}


@router.post("/video/follow")
def video_follow(
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, x_openid or openid or "anonymous")
    exists = db.query(VideoFollow).filter(VideoFollow.user_id == user.id).first()
    if not exists:
        db.add(VideoFollow(user_id=user.id))
        db.commit()
    profile = get_config(db, "video", {}) or {}
    return {
        "ok": True,
        "followed": True,
        "finderUserName": profile.get("finderUserName") or "",
        "message": "已记录关注",
    }


@router.post("/video/reserve")
def video_reserve(
    payload: dict = Body(default={}),
    x_openid: str = Header(default="", alias="X-Openid"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, x_openid or openid or "anonymous")
    live_id = int(payload.get("liveId") or payload.get("live_id") or 0)
    live = db.query(VideoLive).filter(VideoLive.id == live_id, VideoLive.enabled.is_(True)).first()
    if not live:
        raise HTTPException(status_code=404, detail="直播不存在")
    exists = (
        db.query(VideoReserve)
        .filter(VideoReserve.user_id == user.id, VideoReserve.live_id == live.id)
        .first()
    )
    if exists:
        return OkResponse(ok=True, message="已预约", data={"points": 0, "balance": user.points, "reserved": True})
    gained = live.points or 0
    db.add(VideoReserve(user_id=user.id, live_id=live.id, points=gained))
    if gained:
        user.points += gained
        db.add(PointLedger(user_id=user.id, title="预约直播", value=gained))
    db.commit()
    db.refresh(user)
    profile = get_config(db, "video", {}) or {}
    return OkResponse(
        message="预约成功",
        data={
            "points": gained,
            "balance": user.points,
            "reserved": True,
            "finderUserName": profile.get("finderUserName") or "",
            "noticeId": live.notice_id or "",
        },
    )


@router.post("/video/watch")
def video_watch(
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
):
    profile = get_config(db, "video", {}) or {}
    finder = profile.get("finderUserName") or ""
    live_id = int(payload.get("liveId") or payload.get("live_id") or 0)
    live = db.query(VideoLive).filter(VideoLive.id == live_id).first() if live_id else None
    return {
        "ok": True,
        "finderUserName": finder,
        "noticeId": (live.notice_id if live else "") or "",
        "ready": bool(finder),
        "message": "视频号尚未过审，直播间稍后开放" if not finder else "ok",
    }
