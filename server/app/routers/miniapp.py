from datetime import datetime, timedelta
from typing import Optional
import calendar

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..cms_data import (
    AGREEMENTS,
    HOBBY_OPTIONS,
    MEMBER_CONFIG,
    PRIVACY_COLLECT,
    PRIVACY_SHARE,
    RECOMMEND_BANNERS,
)
from ..commerce import (
    add_points,
    award_checkin_milestones,
    award_order_points,
    bump_sold_on_paid,
    display_sold_text,
    find_nye_store,
    get_checkin_config,
    get_loyalty_config,
    hold_room_slot,
    mark_refund_pending,
    nye_packages_for,
    nye_recent_buy,
    nye_starting_price,
    order_earn_points,
    release_room_if_needed,
    release_stale_room_holds,
    reverse_order_points,
    reverse_sold_on_refund,
    room_date_is_past,
    sync_user_vip,
    table_count,
)
from ..database import get_db
from ..models import (
    Address,
    AppUser,
    Banner,
    CheckinRecord,
    Coupon,
    GatherProduct,
    GatherRegion,
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
from ..utils import (
    STATUS_TEXT,
    dumps,
    ensure_coupon_verify_code,
    ensure_order_verify_code,
    get_config,
    loads,
    mark_coupon_expired,
    month_cn,
    normalize_page,
    now_cn,
    page_payload,
    today_cn,
)
from ..wx import code2session, phone_from_code, phone_from_encrypted, resolve_demo_openid, wx_configured

router = APIRouter(prefix="/api/v1", tags=["miniapp"])


def _client_openid(
    x_openid: str = "",
    x_wx_openid: str = "",
    openid: str = "",
) -> str:
    """正式环境只认云托管注入的 X-WX-OPENID，忽略客户端自带的 X-Openid / query。"""
    trusted = (x_wx_openid or "").strip()
    if wx_configured():
        if trusted and trusted != "anonymous":
            return trusted
        return ""
    if trusted and trusted != "anonymous":
        return trusted
    header = (x_openid or "").strip()
    if header and header != "anonymous":
        return header
    q = (openid or "").strip()
    if q and q != "anonymous":
        return q
    return ""


def _require_openid(
    x_openid: str = "",
    x_wx_openid: str = "",
    openid: str = "",
) -> str:
    oid = _client_openid(x_openid, x_wx_openid, openid)
    if not oid or oid == "anonymous":
        raise HTTPException(status_code=401, detail="请先登录")
    return oid


def _user_by_openid(db: Session, openid: str) -> Optional[AppUser]:
    if not openid:
        return None
    return db.query(AppUser).filter(AppUser.openid == openid).first()


def _ensure_user(db: Session, openid: str, nickname: str = "微信用户", avatar: str = "", phone: str = "") -> AppUser:
    user = _user_by_openid(db, openid)
    if user:
        if getattr(user, "cancelled", False):
            # 已注销账号不可复活；应走新 openid 注册
            raise HTTPException(status_code=403, detail="账号已注销")
        return user
    welcome = int(get_loyalty_config(db).get("welcomePoints") or 0)
    user = AppUser(
        openid=openid,
        nickname=nickname or "微信用户",
        avatar=avatar or "",
        phone=phone or "",
        points=max(0, welcome),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    if welcome > 0:
        db.add(PointLedger(user_id=user.id, title="新用户礼包", value=welcome))
        db.commit()
        db.refresh(user)
    return user


def _table_count(db: Session, user_id: int) -> int:
    return table_count(db, user_id)


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
        sync_user_vip(db, user)
        db.commit()
        out["vipLevel"] = user.vip_level
        out["vip"] = f"{user.vip_level}会员"
        out["tableCount"] = _table_count(db, user.id)
    return out


def _product_out(row: GatherProduct, db: Optional[Session] = None) -> dict:
    """关联年夜饭门店时，封面/店名/起价/销量与专题门店共享；仅套餐价在门店内各不相同。"""
    cover = row.cover or ""
    title = row.title or ""
    tag = row.tag or ""
    price = float(row.price or 0)
    origin_price = float(row.origin_price or 0)
    sold_count = int(getattr(row, "sold_count", 0) or 0)
    detail_id = (getattr(row, "detail_id", None) or "").strip()
    if db is not None and detail_id:
        store = find_nye_store(db, detail_id, enabled_only=True)
        if store:
            cover = store.cover or cover
            title = store.name or title
            price = nye_starting_price(store)
            origin_price = float(store.origin_price or 0) or origin_price
            sold_count = int(getattr(store, "sold_count", 0) or 0)
            if not tag.strip():
                tag = store.tag or ""
    return {
        "id": row.id,
        "tab": row.tab,
        "region": getattr(row, "region", "") or "",
        "detailId": row.detail_id,
        "cover": cover,
        "title": title,
        "tag": tag,
        "tags": loads(row.tags, []),
        "soldText": display_sold_text(sold_count, row.sold_text),
        "soldCount": sold_count,
        "price": price,
        "originPrice": origin_price,
    }


def _nye_packages_for(row: NyeStore) -> list:
    return nye_packages_for(row)


def _nye_out(row: NyeStore, db: Optional[Session] = None) -> dict:
    recent = nye_recent_buy(db, row) if db is not None else (loads(row.recent_buy, {}) or {})
    linked = (getattr(row, "store_id", None) or "").strip() or row.id
    return {
        "id": row.id,
        "storeId": linked,
        "name": row.name,
        "cover": row.cover,
        "price": nye_starting_price(row),
        "originPrice": row.origin_price,
        "tag": row.tag,
        "address": row.address,
        "route": row.route,
        "lat": row.lat,
        "lng": row.lng,
        "banners": loads(row.banners, []),
        "detailImages": loads(row.detail_images, []),
        "recentBuy": recent,
        "soldCount": int(getattr(row, "sold_count", 0) or 0),
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
        "statusText": "待发货" if row.type == "mall" and row.status == "paid" else row.status_text,
        "contactName": row.contact_name,
        "contactPhone": row.contact_phone,
        "people": row.people,
        "remark": row.remark,
        "roomDate": row.room_date,
        "roomSlot": row.room_slot,
        "verifyCode": ""
        if row.type == "mall"
        else ((row.verify_code or "") if row.status == "paid" else ""),
        "extra": loads(row.extra or "{}", {}) or {},
        "createdAt": row.created_at.isoformat() if row.created_at else None,
    }


def _mark_order_paid(db: Session, order: Order, extra_patch: Optional[dict] = None) -> Order:
    already_paid = order.status in ("paid", "completed")
    order.status = "paid"
    order.status_text = STATUS_TEXT.get("paid", "待核销")
    extra = loads(order.extra or "{}", {})
    if extra_patch:
        extra.update(extra_patch)
    order.extra = dumps(extra)
    ensure_order_verify_code(db, order)
    if not already_paid:
        user = db.query(AppUser).filter(AppUser.id == order.user_id).first() if order.user_id else None
        bump_sold_on_paid(db, order, user)
        award_order_points(db, order, user)
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


def _release_room_slot(db: Session, order: Order) -> None:
    release_room_if_needed(db, order)


def _hold_room_slot(db: Session, order: Order) -> bool:
    return hold_room_slot(db, order)


def _release_stale_room_holds(db: Session) -> None:
    release_stale_room_holds(db)


def _resolve_order_price(db: Session, payload: OrderCreateIn) -> tuple[float, float, str, str, str]:
    """Return (unit_price, amount, title, cover, spec) from catalog. Ignores client amounts for paid types."""
    qty = max(1, int(payload.quantity or 1))
    if qty > 20:
        raise HTTPException(status_code=400, detail="数量超出范围")
    otype = (payload.type or "").strip()
    if otype == "room":
        qty = 1

    if otype == "room":
        if not ((payload.store_id or "").strip() and (payload.room_date or "").strip() and (payload.room_slot or "").strip()):
            raise HTTPException(status_code=400, detail="请选择门店、日期和时段")
        unit = float(get_loyalty_config(db).get("roomPrice") or 0)
        title = payload.title or "包房预约"
        cover = payload.cover or ""
        spec = payload.spec or ""
        if unit <= 0:
            raise HTTPException(status_code=400, detail="包房预约需支付，请先在后台设置包房单价")
        return unit, round(unit * qty, 2), title, cover, spec

    if otype == "gather":
        raise HTTPException(status_code=400, detail="去哪聚已改为专题套餐预订，请从门店详情下单")

    if otype == "recommend":
        try:
            rid = int(payload.store_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="酒店无效")
        row = (
            db.query(RecommendItem)
            .filter(RecommendItem.id == rid, RecommendItem.enabled.is_(True))
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="酒店不存在")
        unit = float(row.price or 0)
        if unit <= 0:
            raise HTTPException(status_code=400, detail="酒店价格异常")
        return unit, round(unit * qty, 2), row.name, row.cover or "", payload.spec or "订酒店"

    if otype == "nye":
        store = find_nye_store(db, payload.store_id or "", enabled_only=True)
        if not store:
            raise HTTPException(status_code=404, detail="门店不存在或已下架")
        packages = _nye_packages_for(store)
        pkg = None
        pid = str(payload.package_id or "").strip()
        if pid:
            for p in packages:
                if str(p.get("id")) == pid and not p.get("disabled"):
                    pkg = p
                    break
            if not pkg:
                raise HTTPException(status_code=400, detail="套餐不存在或已下架")
        elif payload.spec:
            for p in packages:
                name = str(p.get("name") or "")
                if name and str(payload.spec).startswith(name) and not p.get("disabled"):
                    pkg = p
                    break
        if not pkg:
            enabled = [p for p in packages if not p.get("disabled")]
            pkg = enabled[0] if enabled else None
        if not pkg:
            raise HTTPException(status_code=400, detail="暂无可用套餐")
        unit = float(pkg.get("price") or 0)
        if unit <= 0:
            raise HTTPException(status_code=400, detail="套餐价格异常")
        title = f"{store.name}-年夜饭"
        cover = pkg.get("cover") or store.cover or ""
        spec = str(pkg.get("name") or "")
        if (payload.room_date or "").strip():
            spec = f"{spec} · {payload.room_date.strip()}" if spec else payload.room_date.strip()
        return unit, round(unit * qty, 2), title, cover, spec

    raise HTTPException(status_code=400, detail="订单类型无效")


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
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = _client_openid(x_openid, x_wx_openid, openid)
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

    if user.phone and user.phone == phone:
        return {"openid": user.openid, "user": _user_out(user, db), "message": "手机号已绑定"}
    # 登录时第一次写入不算「修改」；已有号码后再换，只允许一次
    if user.phone and user.phone_edited:
        raise HTTPException(status_code=400, detail="手机号仅可修改一次")

    had_phone = bool(user.phone)
    user.phone = phone
    if had_phone:
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
    regions = (
        db.query(GatherRegion)
        .filter(GatherRegion.enabled.is_(True))
        .order_by(GatherRegion.sort.asc(), GatherRegion.id.asc())
        .all()
    )
    products = (
        db.query(GatherProduct)
        .filter(GatherProduct.enabled.is_(True))
        .order_by(GatherProduct.sort.asc(), GatherProduct.id.asc())
        .all()
    )
    region_list = [{"id": r.id, "name": r.name} for r in regions]
    if not any(r["id"] == "all" for r in region_list):
        region_list.insert(0, {"id": "all", "name": "全部"})
    return {
        "tabs": [
            {"key": t.key, "name": t.name, "showSold": t.show_sold}
            for t in tabs
        ],
        "regions": region_list,
        "products": [_product_out(p, db) for p in products],
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
                "price": nye_starting_price(r),
                "originPrice": r.origin_price,
            }
            for r in rows
        ]
    }


@router.get("/nye/{nye_id}")
def nye_detail(nye_id: str, db: Session = Depends(get_db)):
    row = find_nye_store(db, nye_id, enabled_only=True)
    if not row:
        raise HTTPException(status_code=404, detail="该门店暂未开放预约")
    detail = _nye_out(row, db)
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
    if isinstance(doc, dict):
        out = dict(doc)
        out["blocks"] = out.get("blocks") or []
        return out
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


@router.get("/loyalty/config")
def loyalty_config(db: Session = Depends(get_db)):
    return get_loyalty_config(db)


@router.get("/hobby/options")
def hobby_options(db: Session = Depends(get_db)):
    data = get_config(db, "hobby_options") or HOBBY_OPTIONS
    items = data.get("items") if isinstance(data, dict) else []
    out = []
    for i, raw in enumerate(items or []):
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or "").strip()
        if not name:
            continue
        if raw.get("enabled") is False:
            continue
        out.append(
            {
                "name": name,
                "color": str(raw.get("color") or "#e85a4a").strip() or "#e85a4a",
                "sort": int(raw.get("sort") or i + 1),
            }
        )
    out.sort(key=lambda x: (x["sort"], x["name"]))
    return {"items": out}


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

    _release_stale_room_holds(db)
    today = today_cn()
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
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    status: str = Query(default=""),
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
):
    page, page_size, offset = normalize_page(page, page_size)
    oid = _require_openid(x_openid, x_wx_openid, openid)
    _release_stale_room_holds(db)
    q = db.query(Order).filter(Order.openid == oid)
    st = (status or "").strip()
    if st:
        if st == "closed":
            # 小程序「已关闭」：已取消、待退款、已退款
            q = q.filter(Order.status.in_(("cancelled", "refund_pending", "refunded")))
        else:
            q = q.filter(Order.status == st)
    q = q.order_by(Order.created_at.desc())
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    dirty = False
    for r in rows:
        if r.status == "paid" and not (r.verify_code or "").strip():
            ensure_order_verify_code(db, r)
            dirty = True
    if dirty:
        db.commit()
    return page_payload([_order_out(r) for r in rows], total, page, page_size)


@router.post("/orders")
def create_order(
    payload: OrderCreateIn,
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    db: Session = Depends(get_db),
):
    openid = _require_openid(x_openid, x_wx_openid, payload.openid)
    user = _ensure_user(db, openid)
    order_id = f"o{int(datetime.utcnow().timestamp() * 1000)}"
    qty = max(1, int(payload.quantity or 1))
    if (payload.type or "").strip() == "room":
        qty = 1
    unit_price, amount, title, cover, spec = _resolve_order_price(db, payload)
    room_date = (payload.room_date or "").strip()
    room_slot = (payload.room_slot or "").strip()
    if room_date or room_slot:
        if not room_date or not room_slot:
            raise HTTPException(status_code=400, detail="请选择用餐日期和时段")
        if room_slot not in ("lunch", "dinner"):
            raise HTTPException(status_code=400, detail="用餐时段无效")
        if room_date < today_cn():
            raise HTTPException(status_code=400, detail="用餐日期已过，请重新选择")

    extra = {}
    order_store_id = payload.store_id
    if (payload.type or "") == "nye":
        nye = find_nye_store(db, payload.store_id or "", enabled_only=True)
        if nye:
            order_store_id = nye.id
            linked = (getattr(nye, "store_id", None) or "").strip() or nye.id
            if payload.room_date and payload.room_slot:
                extra["roomStoreId"] = linked
    slot_key = extra.get("roomStoreId") or order_store_id
    if payload.room_date and payload.room_slot and slot_key:
        _release_stale_room_holds(db)
        info = _slot_info(db, slot_key, payload.room_date, payload.room_slot)
        if info["full"] or info["remain"] < 1:
            raise HTTPException(status_code=400, detail="该时段包房已满，请换日期或时段")
        # 先只校验，支付发起时才占库存，避免未付款就把同一家店的包房订走
        extra["roomHeld"] = False

    order = Order(
        id=order_id,
        user_id=user.id,
        openid=openid,
        type=payload.type,
        store_id=order_store_id,
        store_name=payload.store_name,
        title=title,
        spec=spec,
        cover=cover,
        quantity=qty,
        price=unit_price,
        amount=amount,
        status="pending",
        status_text=STATUS_TEXT["pending"],
        contact_name=payload.contact_name,
        contact_phone=payload.contact_phone,
        people=payload.people,
        remark=payload.remark,
        room_date=room_date,
        room_slot=room_slot,
        extra=dumps(extra),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return _order_out(order)


@router.post("/orders/{order_id}/pay")
async def pay_order(
    order_id: str,
    request: Request,
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = _require_openid(x_openid, x_wx_openid, openid)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.openid and order.openid != oid:
        raise HTTPException(status_code=403, detail="无权支付该订单")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="订单状态不可支付")

    _release_stale_room_holds(db)
    db.refresh(order)
    if order.status != "pending":
        if room_date_is_past(order):
            raise HTTPException(status_code=400, detail="用餐日期已过，请重新下单")
        raise HTTPException(status_code=400, detail="订单已关闭，请重新下单")
    if room_date_is_past(order):
        release_room_if_needed(db, order)
        order.status = "cancelled"
        order.status_text = STATUS_TEXT["cancelled"]
        db.commit()
        raise HTTPException(status_code=400, detail="用餐日期已过，请重新下单")

    amount = float(order.amount or order.price or 0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="需支付后才能预约" if order.type == "room" else "订单金额异常，无法支付")

    just_held = False
    try:
        if order.room_date and order.room_slot and order.store_id:
            just_held = _hold_room_slot(db, order)
            db.commit()
        if not pay_configured():
            raise HTTPException(status_code=503, detail="支付暂未开通，请稍后重试")

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
    except Exception:
        if just_held:
            _release_room_slot(db, order)
            db.commit()
        raise


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
    if not order or order.status in ("paid", "completed", "refunded", "refund_pending"):
        return Response(content=notify_ok_xml(), media_type="application/xml")
    _release_stale_room_holds(db)
    db.refresh(order)
    if order.status not in ("pending", "cancelled"):
        return Response(content=notify_ok_xml(), media_type="application/xml")
    expected = int(round(float(order.amount or order.price or 0) * 100))
    try:
        paid_fee = int(data.get("total_fee") or 0)
    except (TypeError, ValueError):
        paid_fee = 0
    if expected > 0 and paid_fee != expected:
        return Response(content=notify_fail_xml("FEE"), media_type="application/xml")
    patch = {
        "transaction_id": data.get("transaction_id") or "",
        "prepay_id": loads(order.extra or "{}", {}).get("prepay_id"),
    }
    if room_date_is_past(order):
        mark_refund_pending(db, order, "用餐日期已过", patch)
        return Response(content=notify_ok_xml(), media_type="application/xml")
    try:
        if order.room_date and order.room_slot and order.store_id:
            _hold_room_slot(db, order)
        _mark_order_paid(db, order, patch)
    except HTTPException:
        mark_refund_pending(db, order, "该时段包房已满", patch)
    return Response(content=notify_ok_xml(), media_type="application/xml")


@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: str,
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = _require_openid(x_openid, x_wx_openid, openid)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.openid and order.openid != oid:
        raise HTTPException(status_code=403, detail="无权取消该订单")
    # 用户侧仅允许取消待支付；已支付请走后台
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="订单状态不可取消")
    _release_room_slot(db, order)
    extra = loads(order.extra or "{}", {}) or {}
    uc_id = int(extra.get("couponId") or 0)
    if uc_id:
        uc = db.query(UserCoupon).filter(UserCoupon.id == uc_id, UserCoupon.user_id == order.user_id).first()
        if uc and uc.status == "used":
            uc.status = "unused"
    order.status = "cancelled"
    order.status_text = STATUS_TEXT["cancelled"]
    db.commit()
    return _order_out(order)


@router.post("/mall/redeem")
def mall_redeem(
    payload: dict = Body(default={}),
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = _require_openid(x_openid, x_wx_openid, openid)
    user = _ensure_user(db, oid)
    goods_id = int(payload.get("goodsId") or payload.get("goods_id") or 0)
    address_id = int(payload.get("addressId") or payload.get("address_id") or 0)
    user = db.query(AppUser).filter(AppUser.id == user.id).with_for_update().first()
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    row = (
        db.query(MallGoods)
        .filter(MallGoods.id == goods_id, MallGoods.enabled.is_(True))
        .with_for_update()
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="商品不存在")
    if row.stock <= 0:
        raise HTTPException(status_code=400, detail="库存不足")
    if user.points < row.cost:
        raise HTTPException(status_code=400, detail="积分不足")
    if not address_id:
        raise HTTPException(status_code=400, detail="请选择收货地址")
    addr = db.query(Address).filter(Address.id == address_id, Address.user_id == user.id).first()
    if not addr:
        raise HTTPException(status_code=400, detail="收货地址无效")
    region = addr.region or f"{addr.province or ''}{addr.city or ''}{addr.district or ''}".strip()
    row.stock -= 1
    add_points(db, user, f"积分兑换-{row.name}", -row.cost)
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
        status_text="待发货",
        contact_name=addr.name or "",
        contact_phone=addr.phone or "",
        remark=f"{region} {addr.detail or ''}".strip(),
        extra=dumps(
            {
                "addressId": addr.id,
                "address": {
                    "name": addr.name,
                    "phone": addr.phone,
                    "region": region,
                    "detail": addr.detail,
                },
                "redeemCode": "",
            }
        ),
    )
    db.add(order)
    db.commit()
    db.refresh(user)
    extra = loads(order.extra or "{}", {}) or {}
    return {
        "ok": True,
        "balance": user.points,
        "orderId": order.id,
        "redeemCode": extra.get("redeemCode") or "",
        "message": "兑换成功",
    }


def _profile_reward_config(db: Session) -> dict:
    raw = get_config(db, "profile_reward", {}) or {}
    if not isinstance(raw, dict):
        raw = {}
    try:
        points = int(raw.get("points") or 0)
    except (TypeError, ValueError):
        points = 0
    return {"enabled": bool(raw.get("enabled")), "points": max(0, points)}


def _profile_complete(user: AppUser) -> bool:
    nick = (user.nickname or "").strip()
    if not nick or nick == "微信用户":
        return False
    if not (user.birthday or "").strip():
        return False
    if not (user.phone or "").strip():
        return False
    if not (user.hobby or "").strip():
        return False
    return True


def _grant_profile_reward(db: Session, user: AppUser) -> int:
    if getattr(user, "profile_rewarded", False):
        return 0
    cfg = _profile_reward_config(db)
    if not cfg["enabled"] or cfg["points"] <= 0 or not _profile_complete(user):
        return 0
    add_points(db, user, "完善个人资料", cfg["points"])
    user.profile_rewarded = True
    db.commit()
    db.refresh(user)
    return cfg["points"]


@router.get("/profile-reward")
def profile_reward_public(db: Session = Depends(get_db)):
    return _profile_reward_config(db)


@router.get("/user/profile")
def user_profile(
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
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
        "profileRewarded": bool(getattr(user, "profile_rewarded", False)),
        "tableCount": 0,
    }
    if db is not None:
        sync_user_vip(db, user)
        db.commit()
        out["vipLevel"] = user.vip_level
        out["vip"] = f"{user.vip_level}会员"
        out["tableCount"] = _table_count(db, user.id)
    return out


@router.put("/user/profile")
def update_profile(
    payload: dict = Body(default={}),
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
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
    granted = _grant_profile_reward(db, user)
    out = _profile_out(user, db)
    out["profileRewardGranted"] = granted
    return out


@router.post("/user/cancel")
def cancel_account(
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = _require_openid(x_openid, x_wx_openid, openid)
    user = _user_by_openid(db, oid)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 作废优惠券、清空地址与积分，并释放 openid 以便重新注册
    db.query(UserCoupon).filter(UserCoupon.user_id == user.id, UserCoupon.status == "unused").update(
        {"status": "expired"}, synchronize_session=False
    )
    db.query(Address).filter(Address.user_id == user.id).delete(synchronize_session=False)
    if user.points:
        add_points(db, user, "账号注销清零", -int(user.points or 0))
    user.cancelled = True
    user.nickname = "已注销用户"
    user.avatar = ""
    user.phone = ""
    user.birthday = ""
    user.hobby = ""
    user.session_key = ""
    user.openid = f"cancelled_{user.id}_{int(datetime.utcnow().timestamp())}"
    db.commit()
    return OkResponse(message="账号已注销")


@router.get("/user/addresses")
def list_addresses(
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
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
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
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
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
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
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
    row = db.query(Address).filter(Address.id == address_id, Address.user_id == user.id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


@router.post("/user/addresses/{address_id}/default")
def set_default_address(
    address_id: int,
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
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
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
    user = db.query(AppUser).filter(AppUser.id == user.id).with_for_update().first()
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    coupon_id = payload.get("couponId") or payload.get("coupon_id")
    # 月份一律服务端按上海时区计算，忽略客户端伪造
    month_key = month_cn()
    try:
        if coupon_id:
            coupon = db.query(Coupon).filter(Coupon.id == int(coupon_id), Coupon.enabled.is_(True)).first()
        else:
            coupon = db.query(Coupon).filter(Coupon.enabled.is_(True)).order_by(Coupon.id.asc()).first()
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="优惠券无效")
    if not coupon:
        raise HTTPException(status_code=404, detail="暂无可领优惠券")
    coupon = db.query(Coupon).filter(Coupon.id == coupon.id).with_for_update().first()
    if not coupon or not coupon.enabled:
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
    db.flush()
    ensure_coupon_verify_code(db, row)
    db.commit()
    return OkResponse(
        message="领取成功",
        data={"id": row.id, "name": row.name, "amount": row.amount, "month": month_key},
    )


@router.get("/mall/records")
def mall_records(
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
):
    page, page_size, offset = normalize_page(page, page_size)
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
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
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = _require_openid(x_openid, x_wx_openid, openid)
    row = db.query(Order).filter(Order.id == order_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="订单不存在")
    if row.openid and row.openid != oid:
        raise HTTPException(status_code=403, detail="无权查看")
    if row.status == "paid" and not (row.verify_code or "").strip():
        ensure_order_verify_code(db, row)
        db.commit()
    return _order_out(row)


@router.get("/user/points")
def user_points(
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
):
    page, page_size, offset = normalize_page(page, page_size)
    oid = _require_openid(x_openid, x_wx_openid, openid)
    user = _ensure_user(db, oid)
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
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = _require_openid(x_openid, x_wx_openid, openid)
    user = _ensure_user(db, oid)
    rows = db.query(UserCoupon).filter(UserCoupon.user_id == user.id).order_by(UserCoupon.id.desc()).all()
    dirty = False
    for r in rows:
        if mark_coupon_expired(r):
            dirty = True
            continue
        if r.status == "unused" and not (r.verify_code or "").strip():
            ensure_coupon_verify_code(db, r)
            dirty = True
    if dirty:
        db.commit()
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
                "verifyCode": (r.verify_code or "") if r.status == "unused" else "",
            }
        )
    return grouped


@router.post("/checkin")
def checkin(
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    makeup: bool = Query(False),
    db: Session = Depends(get_db),
):
    oid = _require_openid(x_openid, x_wx_openid, openid)
    user = _ensure_user(db, oid)
    today = today_cn()
    cfg = get_checkin_config(db)
    points = int(cfg["makeupPoints"] if makeup else cfg["dailyPoints"])

    if makeup:
        # 每日仅一次补签：填补近 7 天内最近一个未签日期
        day_start_utc = (now_cn().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=8)).replace(
            tzinfo=None
        )
        already = (
            db.query(PointLedger)
            .filter(
                PointLedger.user_id == user.id,
                PointLedger.title == "补签",
                PointLedger.created_at >= day_start_utc,
            )
            .first()
        )
        if already:
            return OkResponse(
                ok=False, message="今日已补签", data={"points": 0, "balance": user.points}
            )
        target = None
        for delta in range(1, 8):
            d = (now_cn() - timedelta(days=delta)).strftime("%Y-%m-%d")
            exists_day = (
                db.query(CheckinRecord)
                .filter(CheckinRecord.user_id == user.id, CheckinRecord.date == d)
                .first()
            )
            if not exists_day:
                target = d
                break
        if not target:
            return OkResponse(
                ok=False, message="暂无可补签日期", data={"points": 0, "balance": user.points}
            )
        db.add(CheckinRecord(user_id=user.id, date=target, points=points, is_makeup=True))
        if points > 0:
            add_points(db, user, "补签", points)
        y, m = int(today[:4]), int(today[5:7])
        signed = (
            db.query(CheckinRecord)
            .filter(CheckinRecord.user_id == user.id, CheckinRecord.date.like(f"{y}-{m:02d}%"))
            .count()
        )
        award_checkin_milestones(db, user, y, m, signed)
        db.commit()
        db.refresh(user)
        return OkResponse(ok=True, message="补签成功", data={"points": points, "balance": user.points})

    exists = (
        db.query(CheckinRecord)
        .filter(CheckinRecord.user_id == user.id, CheckinRecord.date == today)
        .first()
    )
    if exists:
        return OkResponse(ok=False, message="今日已签到", data={"points": 0, "balance": user.points})
    db.add(CheckinRecord(user_id=user.id, date=today, points=points, is_makeup=False))
    if points > 0:
        add_points(db, user, "每日签到", points)
    y, m = int(today[:4]), int(today[5:7])
    signed = (
        db.query(CheckinRecord)
        .filter(CheckinRecord.user_id == user.id, CheckinRecord.date.like(f"{y}-{m:02d}%"))
        .count()
    )
    award_checkin_milestones(db, user, y, m, signed)
    db.commit()
    db.refresh(user)
    return OkResponse(ok=True, message="签到成功", data={"points": points, "balance": user.points})


@router.get("/checkin/month")
def checkin_month(
    year: int = Query(...),
    month: int = Query(...),
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    oid = _require_openid(x_openid, x_wx_openid, openid)
    user = _ensure_user(db, oid)
    prefix = f"{year}-{month:02d}"
    rows = (
        db.query(CheckinRecord)
        .filter(CheckinRecord.user_id == user.id, CheckinRecord.date.like(f"{prefix}%"))
        .all()
    )
    cfg = get_checkin_config(db)
    full_days = calendar.monthrange(year, month)[1]
    milestones = [
        {"label": m["label"], "points": m["points"], "days": m["days"]} for m in cfg["milestones"]
    ]
    if cfg["fullMonthBonus"] > 0:
        milestones.append(
            {"label": "整月满签", "points": cfg["fullMonthBonus"], "days": full_days}
        )
    # 补签资格：近 7 天内最近漏签日 + 今日是否已补签
    day_start_utc = (now_cn().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=8)).replace(
        tzinfo=None
    )
    makeup_claimed = (
        db.query(PointLedger)
        .filter(
            PointLedger.user_id == user.id,
            PointLedger.title == "补签",
            PointLedger.created_at >= day_start_utc,
        )
        .first()
        is not None
    )
    makeup_target = None
    for delta in range(1, 8):
        d = (now_cn() - timedelta(days=delta)).strftime("%Y-%m-%d")
        exists_day = (
            db.query(CheckinRecord)
            .filter(CheckinRecord.user_id == user.id, CheckinRecord.date == d)
            .first()
        )
        if not exists_day:
            makeup_target = d
            break
    return {
        "dates": [r.date for r in rows],
        "signedDays": len(rows),
        "monthPoints": sum(r.points for r in rows),
        "config": {
            "dailyPoints": cfg["dailyPoints"],
            "makeupPoints": cfg["makeupPoints"],
            "fullMonthBonus": cfg["fullMonthBonus"],
            "milestones": milestones,
            "rules": cfg["rules"],
        },
        "makeup": {
            "claimedToday": makeup_claimed,
            "available": bool(makeup_target) and not makeup_claimed,
            "targetDate": makeup_target or "",
        },
    }


@router.get("/video")
def video_home(
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    profile = _normalize_video_profile(get_config(db, "video", {}) or {})
    followed = False
    reserved_notice_ids: list[str] = []
    oid = _client_openid(x_openid, x_wx_openid, openid)
    if oid:
        user = _user_by_openid(db, oid)
        if user:
            followed = db.query(VideoFollow).filter(VideoFollow.user_id == user.id).first() is not None
            reserved_ids = {
                r.live_id
                for r in db.query(VideoReserve).filter(VideoReserve.user_id == user.id).all()
            }
            if reserved_ids:
                reserved_notice_ids = [
                    row.notice_id
                    for row in db.query(VideoLive)
                    .filter(VideoLive.id.in_(reserved_ids), VideoLive.notice_id != "")
                    .all()
                    if row.notice_id
                ]
    return {
        "profile": profile,
        "followed": followed,
        "reservedNoticeIds": reserved_notice_ids,
        "living": None,
        "lives": [],
    }


@router.post("/video/follow")
def video_follow(
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
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


def _default_video_reserve_points(db: Session) -> int:
    profile = get_config(db, "video", {}) or {}
    raw = profile.get("defaultReservePoints")
    try:
        points = int(raw)
        if points >= 0:
            return points
    except (TypeError, ValueError):
        pass
    return 10


def _normalize_video_profile(profile: dict) -> dict:
    data = dict(profile or {})
    raw = data.get("defaultReservePoints")
    try:
        points = int(raw)
        if points < 0:
            points = 10
    except (TypeError, ValueError):
        points = 10
    data["defaultReservePoints"] = points
    return data


def _resolve_video_live(db: Session, payload: dict) -> VideoLive:
    notice_id = str(payload.get("noticeId") or payload.get("notice_id") or "").strip()
    if not notice_id:
        raise HTTPException(status_code=400, detail="缺少直播预告")
    live = db.query(VideoLive).filter(VideoLive.notice_id == notice_id).first()
    if live:
        return live
    points = _default_video_reserve_points(db)
    live = VideoLive(
        status="scheduled",
        time_text=str(payload.get("time") or "")[:64],
        line1=str(payload.get("line1") or "视频号直播")[:128],
        line2=str(payload.get("line2") or "")[:128],
        points=points,
        avatar=str(payload.get("avatar") or "")[:512],
        notice_id=notice_id,
        sort=0,
        enabled=True,
    )
    db.add(live)
    db.flush()
    return live


@router.post("/video/reserve")
def video_reserve(
    payload: dict = Body(default={}),
    x_openid: str = Header(default="", alias="X-Openid"),
    x_wx_openid: str = Header(default="", alias="X-WX-OPENID"),
    openid: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = _ensure_user(db, _require_openid(x_openid, x_wx_openid, openid))
    live = _resolve_video_live(db, payload or {})
    exists = (
        db.query(VideoReserve)
        .filter(VideoReserve.user_id == user.id, VideoReserve.live_id == live.id)
        .first()
    )
    if exists:
        profile = get_config(db, "video", {}) or {}
        return OkResponse(
            ok=True,
            message="已预约",
            data={
                "points": 0,
                "balance": user.points,
                "reserved": True,
                "finderUserName": profile.get("finderUserName") or "",
                "noticeId": live.notice_id or "",
            },
        )
    gained = live.points or 0
    db.add(VideoReserve(user_id=user.id, live_id=live.id, points=gained))
    if gained:
        add_points(db, user, "预约直播", gained)
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
    raw_live_id = (payload or {}).get("liveId")
    if raw_live_id is None:
        raw_live_id = (payload or {}).get("live_id")
    try:
        live_id = int(raw_live_id or 0)
    except (TypeError, ValueError):
        live_id = 0
    live = db.query(VideoLive).filter(VideoLive.id == live_id).first() if live_id else None
    return {
        "ok": True,
        "finderUserName": finder,
        "noticeId": (live.notice_id if live else "") or "",
        "ready": bool(finder),
        "message": "视频号尚未过审，直播间稍后开放" if not finder else "ok",
    }
