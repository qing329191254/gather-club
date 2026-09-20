from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import create_access_token, get_current_admin, verify_password
from ..models import (
    AdminUser,
    AppUser,
    Banner,
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
    VideoLive,
)
from ..schemas import (
    BannerIn,
    CouponIn,
    GatherProductIn,
    GatherTabIn,
    LoginRequest,
    MallGoodsIn,
    NyeStoreIn,
    OkResponse,
    OrderStatusIn,
    PointsAdjustIn,
    RecommendItemIn,
    RoomSlotIn,
    StoreIn,
    TokenResponse,
)
from ..storage import storage_configured, upload_file
from ..utils import STATUS_TEXT, dumps, get_config, loads, normalize_page, page_payload, set_config

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return TokenResponse(access_token=create_access_token(user.username), username=user.username)


@router.post("/upload")
async def admin_upload(
    file: UploadFile = File(...),
    folder: str = Form(default="uploads"),
    _: AdminUser = Depends(get_current_admin),
):
    if not storage_configured():
        raise HTTPException(
            status_code=500,
            detail="未配置对象存储：请设置 WX_APPID、WX_SECRET、WX_CLOUD_ENV",
        )
    return await upload_file(file, folder=folder or "uploads")


@router.get("/me")
def me(admin: AdminUser = Depends(get_current_admin)):
    return {"username": admin.username, "id": admin.id}


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    return {
        "stores": db.query(Store).count(),
        "users": db.query(AppUser).count(),
        "orders": db.query(Order).count(),
        "pendingOrders": db.query(Order).filter(Order.status == "pending").count(),
        "mallGoods": db.query(MallGoods).count(),
        "coupons": db.query(Coupon).count(),
    }


# ---- banners ----
@router.get("/banners")
def list_banners(db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    rows = db.query(Banner).order_by(Banner.sort.asc(), Banner.id.asc()).all()
    return [
        {"id": r.id, "image": r.image, "link": r.link, "sort": r.sort, "enabled": r.enabled}
        for r in rows
    ]


@router.post("/banners")
def create_banner(payload: BannerIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = Banner(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, **payload.model_dump()}


@router.put("/banners/{banner_id}")
def update_banner(banner_id: int, payload: BannerIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(Banner).filter(Banner.id == banner_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    db.commit()
    return {"id": row.id, **payload.model_dump()}


@router.delete("/banners/{banner_id}")
def delete_banner(banner_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(Banner).filter(Banner.id == banner_id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


# ---- stores ----
@router.get("/stores")
def list_stores(db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    return db.query(Store).order_by(Store.sort.asc(), Store.id.asc()).all()


@router.post("/stores")
def create_store(payload: StoreIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    data = payload.model_dump()
    store_id = (data.get("id") or "").strip()
    if not store_id:
        store_id = f"store_{int(datetime.utcnow().timestamp())}"
        while db.query(Store).filter(Store.id == store_id).first():
            store_id = f"store_{int(datetime.utcnow().timestamp())}_{datetime.utcnow().microsecond}"
    elif db.query(Store).filter(Store.id == store_id).first():
        raise HTTPException(400, "门店已存在")
    data["id"] = store_id
    row = Store(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/stores/{store_id}")
def update_store(store_id: str, payload: StoreIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(Store).filter(Store.id == store_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    data = payload.model_dump()
    data.pop("id", None)
    for k, v in data.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/stores/{store_id}")
def delete_store(store_id: str, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(Store).filter(Store.id == store_id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


# ---- gather ----
@router.get("/gather/tabs")
def list_gather_tabs(db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    return db.query(GatherTab).order_by(GatherTab.sort.asc(), GatherTab.id.asc()).all()


@router.post("/gather/tabs")
def create_gather_tab(payload: GatherTabIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    if db.query(GatherTab).filter(GatherTab.key == payload.key).first():
        raise HTTPException(400, "分类 key 已存在")
    row = GatherTab(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/gather/tabs/{tab_id}")
def update_gather_tab(tab_id: int, payload: GatherTabIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(GatherTab).filter(GatherTab.id == tab_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/gather/tabs/{tab_id}")
def delete_gather_tab(tab_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(GatherTab).filter(GatherTab.id == tab_id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


@router.get("/gather/products")
def list_gather_products(
    page: int = Query(1),
    page_size: int = Query(20),
    tab: str = Query(""),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    page, page_size, offset = normalize_page(page, page_size)
    q = db.query(GatherProduct).order_by(GatherProduct.sort.asc(), GatherProduct.id.asc())
    if tab:
        q = q.filter(GatherProduct.tab == tab)
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    return page_payload(
        [
            {
                "id": r.id,
                "tab": r.tab,
                "detail_id": r.detail_id,
                "cover": r.cover,
                "title": r.title,
                "tag": r.tag,
                "tags": loads(r.tags, []),
                "sold_text": r.sold_text,
                "price": r.price,
                "origin_price": r.origin_price,
                "sort": r.sort,
                "enabled": r.enabled,
            }
            for r in rows
        ],
        total,
        page,
        page_size,
    )


@router.post("/gather/products")
def create_gather_product(payload: GatherProductIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    if db.query(GatherProduct).filter(GatherProduct.id == payload.id).first():
        raise HTTPException(400, "商品 ID 已存在")
    data = payload.model_dump()
    tags = data.pop("tags", [])
    row = GatherProduct(**data, tags=dumps(tags))
    db.add(row)
    db.commit()
    return payload


@router.put("/gather/products/{product_id}")
def update_gather_product(product_id: str, payload: GatherProductIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(GatherProduct).filter(GatherProduct.id == product_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    data = payload.model_dump()
    tags = data.pop("tags", [])
    data.pop("id", None)
    for k, v in data.items():
        setattr(row, k, v)
    row.tags = dumps(tags)
    db.commit()
    return payload


@router.delete("/gather/products/{product_id}")
def delete_gather_product(product_id: str, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(GatherProduct).filter(GatherProduct.id == product_id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


# ---- nye ----
@router.get("/nye")
def list_nye(db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    rows = db.query(NyeStore).order_by(NyeStore.sort.asc(), NyeStore.id.asc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "cover": r.cover,
            "price": r.price,
            "origin_price": r.origin_price,
            "tag": r.tag,
            "address": r.address,
            "route": r.route,
            "lat": r.lat,
            "lng": r.lng,
            "banners": loads(r.banners, []),
            "detail_images": loads(r.detail_images, []),
            "recent_buy": loads(r.recent_buy, {}),
            "packages": loads(getattr(r, "packages", None) or "[]", []),
            "open_start": r.open_start,
            "open_end": r.open_end,
            "sort": r.sort,
            "enabled": r.enabled,
        }
        for r in rows
    ]


@router.post("/nye")
def create_nye(payload: NyeStoreIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    if db.query(NyeStore).filter(NyeStore.id == payload.id).first():
        raise HTTPException(400, "ID 已存在")
    data = payload.model_dump()
    row = NyeStore(
        id=data["id"],
        name=data["name"],
        cover=data["cover"],
        price=data["price"],
        origin_price=data["origin_price"],
        tag=data["tag"],
        address=data["address"],
        route=data["route"],
        lat=data["lat"],
        lng=data["lng"],
        banners=dumps(data["banners"]),
        detail_images=dumps(data["detail_images"]),
        recent_buy=dumps(data["recent_buy"]),
        packages=dumps(data.get("packages") or []),
        open_start=data["open_start"],
        open_end=data["open_end"],
        sort=data["sort"],
        enabled=data["enabled"],
    )
    db.add(row)
    db.commit()
    return payload


@router.put("/nye/{nye_id}")
def update_nye(nye_id: str, payload: NyeStoreIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(NyeStore).filter(NyeStore.id == nye_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    data = payload.model_dump()
    row.name = data["name"]
    row.cover = data["cover"]
    row.price = data["price"]
    row.origin_price = data["origin_price"]
    row.tag = data["tag"]
    row.address = data["address"]
    row.route = data["route"]
    row.lat = data["lat"]
    row.lng = data["lng"]
    row.banners = dumps(data["banners"])
    row.detail_images = dumps(data["detail_images"])
    row.recent_buy = dumps(data["recent_buy"])
    row.packages = dumps(data.get("packages") or [])
    row.open_start = data["open_start"]
    row.open_end = data["open_end"]
    row.sort = data["sort"]
    row.enabled = data["enabled"]
    db.commit()
    return payload


@router.delete("/nye/{nye_id}")
def delete_nye(nye_id: str, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(NyeStore).filter(NyeStore.id == nye_id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


# ---- recommend ----
def _recommend_out(row: RecommendItem) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "cover": row.cover,
        "price": row.price,
        "sort": row.sort,
        "enabled": row.enabled,
    }


@router.get("/recommend")
def list_recommend(db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    banners = (get_config(db, "recommend", {}) or {}).get("banners") or []
    rows = db.query(RecommendItem).order_by(RecommendItem.sort.asc(), RecommendItem.id.asc()).all()
    return {"banners": banners, "list": [_recommend_out(r) for r in rows]}


@router.put("/recommend/banners")
def update_recommend_banners(
    payload: dict,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    banners = payload.get("banners") or []
    set_config(db, "recommend", {"banners": banners})
    return {"banners": banners}


@router.post("/recommend")
def create_recommend(payload: RecommendItemIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = RecommendItem(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return _recommend_out(row)


@router.put("/recommend/{item_id}")
def update_recommend(
    item_id: int,
    payload: RecommendItemIn,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    row = db.query(RecommendItem).filter(RecommendItem.id == item_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return _recommend_out(row)


@router.delete("/recommend/{item_id}")
def delete_recommend(item_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(RecommendItem).filter(RecommendItem.id == item_id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


# ---- mall ----
@router.get("/mall/goods")
def list_mall(
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    page, page_size, offset = normalize_page(page, page_size)
    q = db.query(MallGoods).order_by(MallGoods.sort.asc(), MallGoods.id.asc())
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    return page_payload(rows, total, page, page_size)


@router.post("/mall/goods")
def create_mall(payload: MallGoodsIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    data = payload.model_dump()
    if not data.get("title"):
        data["title"] = data["name"]
    row = MallGoods(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/mall/goods/{goods_id}")
def update_mall(goods_id: int, payload: MallGoodsIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(MallGoods).filter(MallGoods.id == goods_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    if not row.title:
        row.title = row.name
    db.commit()
    db.refresh(row)
    return row


@router.delete("/mall/goods/{goods_id}")
def delete_mall(goods_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(MallGoods).filter(MallGoods.id == goods_id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


# ---- orders ----
@router.get("/orders")
def list_orders(
    status: Optional[str] = Query(None),
    keyword: str = Query(""),
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    page, page_size, offset = normalize_page(page, page_size)
    q = db.query(Order).order_by(Order.created_at.desc())
    if status:
        q = q.filter(Order.status == status)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            (Order.id.like(like))
            | (Order.store_name.like(like))
            | (Order.contact_phone.like(like))
            | (Order.title.like(like))
        )
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    return page_payload(
        [
            {
                "id": r.id,
                "type": r.type,
                "store_id": r.store_id,
                "store_name": r.store_name,
                "title": r.title,
                "spec": r.spec,
                "cover": r.cover,
                "quantity": r.quantity,
                "price": r.price,
                "amount": r.amount,
                "status": r.status,
                "status_text": r.status_text,
                "contact_name": r.contact_name,
                "contact_phone": r.contact_phone,
                "people": r.people,
                "remark": r.remark,
                "room_date": r.room_date,
                "room_slot": r.room_slot,
                "openid": r.openid,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
        total,
        page,
        page_size,
    )


@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: str,
    payload: OrderStatusIn,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    row = db.query(Order).filter(Order.id == order_id).first()
    if not row:
        raise HTTPException(404, "订单不存在")
    row.status = payload.status
    row.status_text = payload.status_text or STATUS_TEXT.get(payload.status, payload.status)
    db.commit()
    return OkResponse(data={"id": row.id, "status": row.status, "status_text": row.status_text})


# ---- rooms ----
@router.get("/rooms")
def list_rooms(
    store_id: str = Query(""),
    date: str = Query(""),
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    page, page_size, offset = normalize_page(page, page_size)
    q = db.query(RoomSlot).order_by(RoomSlot.date.desc(), RoomSlot.store_id.asc())
    if store_id:
        q = q.filter(RoomSlot.store_id == store_id)
    if date:
        q = q.filter(RoomSlot.date == date)
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    return page_payload(rows, total, page, page_size)


@router.post("/rooms")
def upsert_room(payload: RoomSlotIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = (
        db.query(RoomSlot)
        .filter(
            RoomSlot.store_id == payload.store_id,
            RoomSlot.date == payload.date,
            RoomSlot.slot == payload.slot,
        )
        .first()
    )
    if row:
        row.capacity = payload.capacity
        row.booked = payload.booked
    else:
        row = RoomSlot(**payload.model_dump())
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/rooms/{slot_id}")
def delete_room(slot_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(RoomSlot).filter(RoomSlot.id == slot_id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


# ---- coupons ----
@router.get("/coupons")
def list_coupons(
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    page, page_size, offset = normalize_page(page, page_size)
    q = db.query(Coupon).order_by(Coupon.id.desc())
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    return page_payload(rows, total, page, page_size)


@router.post("/coupons")
def create_coupon(payload: CouponIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = Coupon(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/coupons/{coupon_id}")
def update_coupon(coupon_id: int, payload: CouponIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/coupons/{coupon_id}")
def delete_coupon(coupon_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()


# ---- users ----
@router.get("/users")
def list_users(
    keyword: str = Query(""),
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    page, page_size, offset = normalize_page(page, page_size)
    q = db.query(AppUser).order_by(AppUser.id.desc())
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            (AppUser.nickname.like(like))
            | (AppUser.phone.like(like))
            | (AppUser.openid.like(like))
        )
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    return page_payload(rows, total, page, page_size)


@router.post("/users/{user_id}/points")
def adjust_points(
    user_id: int,
    payload: PointsAdjustIn,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    user.points = max(0, user.points + payload.points)
    db.add(PointLedger(user_id=user.id, title=payload.title or "后台调整", value=payload.points))
    db.commit()
    db.refresh(user)
    return {"id": user.id, "points": user.points}


@router.put("/users/{user_id}/vip")
def update_vip(
    user_id: int,
    vip_level: str = Query(...),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    user.vip_level = vip_level.upper()
    db.commit()
    return {"id": user.id, "vip_level": user.vip_level}


# ---- site config ----
@router.get("/config/{key}")
def get_site_config(key: str, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    return {"key": key, "value": get_config(db, key, {})}


@router.put("/config/{key}")
def put_site_config(
    key: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    value = payload.get("value", payload)
    set_config(db, key, value)
    return {"key": key, "value": value}


def _live_admin(row: VideoLive) -> dict:
    return {
        "id": row.id,
        "status": row.status,
        "time_text": row.time_text,
        "line1": row.line1,
        "line2": row.line2,
        "points": row.points,
        "avatar": row.avatar,
        "notice_id": row.notice_id,
        "sort": row.sort,
        "enabled": row.enabled,
    }


@router.get("/video/lives")
def list_video_lives(db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    rows = db.query(VideoLive).order_by(VideoLive.sort.asc(), VideoLive.id.asc()).all()
    return [_live_admin(r) for r in rows]


@router.post("/video/lives")
def create_video_live(payload: dict, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = VideoLive(
        status=payload.get("status") or "scheduled",
        time_text=payload.get("time_text") or "",
        line1=payload.get("line1") or "",
        line2=payload.get("line2") or "",
        points=int(payload.get("points") or 0),
        avatar=payload.get("avatar") or "",
        notice_id=payload.get("notice_id") or "",
        sort=int(payload.get("sort") or 0),
        enabled=bool(payload.get("enabled", True)),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _live_admin(row)


@router.put("/video/lives/{live_id}")
def update_video_live(live_id: int, payload: dict, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(VideoLive).filter(VideoLive.id == live_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    row.status = payload.get("status") or row.status
    row.time_text = payload.get("time_text", row.time_text) or ""
    row.line1 = payload.get("line1", row.line1) or ""
    row.line2 = payload.get("line2", row.line2) or ""
    row.points = int(payload.get("points", row.points) or 0)
    row.avatar = payload.get("avatar", row.avatar) or ""
    row.notice_id = payload.get("notice_id", row.notice_id) or ""
    row.sort = int(payload.get("sort", row.sort) or 0)
    row.enabled = bool(payload.get("enabled", row.enabled))
    db.commit()
    db.refresh(row)
    return _live_admin(row)


@router.delete("/video/lives/{live_id}")
def delete_video_live(live_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(VideoLive).filter(VideoLive.id == live_id).first()
    if row:
        db.delete(row)
        db.commit()
    return OkResponse()
