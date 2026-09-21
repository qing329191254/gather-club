from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ..cms_data import (
    AGREEMENTS,
    CHECKIN_CONFIG,
    HOBBY_OPTIONS,
    LOYALTY_CONFIG,
    MEMBER_CONFIG,
    PRIVACY_COLLECT,
    PRIVACY_SHARE,
)
from ..commerce import (
    bump_sold_on_paid,
    sync_user_vip,
    table_count,
    add_points,
    award_order_points,
    find_nye_store,
    hold_room_slot,
    nye_starting_price,
    release_room_if_needed,
    release_stale_room_holds,
    reverse_order_points,
    reverse_sold_on_refund,
)
from ..database import get_db
from ..deps import create_access_token, get_current_admin, verify_password
from ..models import (
    Address,
    AdminUser,
    AppUser,
    Banner,
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
    VerifyLog,
)
from ..schemas import (
    BannerIn,
    CouponIn,
    GatherProductIn,
    GatherRegionIn,
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
from ..storage import diagnose_storage, storage_configured, upload_file
from ..utils import (
    STATUS_TEXT,
    dumps,
    ensure_coupon_verify_code,
    ensure_order_verify_code,
    get_config,
    loads,
    mark_coupon_expired,
    normalize_page,
    now_cn,
    page_payload,
    set_config,
    today_cn,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return TokenResponse(access_token=create_access_token(user.username), username=user.username)


@router.get("/storage/status")
async def storage_status(_: AdminUser = Depends(get_current_admin)):
    """上传能力自检（不含密钥明文）。"""
    return await diagnose_storage()


@router.post("/assets/bootstrap")
async def assets_bootstrap(
    force: bool = Query(False),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    """把站点/会员/视频号本地品牌图上传到云存储并回写配置。"""
    from ..asset_bootstrap import bootstrap_brand_assets
    from ..seed import refresh_demo_covers

    refresh_demo_covers(db)
    return await bootstrap_brand_assets(db, force=force)


@router.post("/upload")
async def admin_upload(
    file: UploadFile = File(...),
    folder: str = Form(default="uploads"),
    _: AdminUser = Depends(get_current_admin),
):
    if not storage_configured():
        raise HTTPException(
            status_code=500,
            detail="未配置 WX_CLOUD_ENV。请到云托管环境变量补齐后重新发布",
        )
    try:
        return await upload_file(file, folder=folder or "uploads")
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"上传失败: {exc}") from exc


@router.get("/me")
def me(admin: AdminUser = Depends(get_current_admin)):
    return {"username": admin.username, "id": admin.id}


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    release_stale_room_holds(db)
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


# ---- gather regions ----
@router.get("/gather/regions")
def list_gather_regions(db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    return db.query(GatherRegion).order_by(GatherRegion.sort.asc(), GatherRegion.id.asc()).all()


@router.post("/gather/regions")
def create_gather_region(payload: GatherRegionIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    rid = (payload.id or "").strip()
    if not rid:
        raise HTTPException(400, "请填写地区 ID")
    if db.query(GatherRegion).filter(GatherRegion.id == rid).first():
        raise HTTPException(400, "地区 ID 已存在")
    row = GatherRegion(id=rid, name=payload.name.strip(), sort=payload.sort, enabled=payload.enabled)
    db.add(row)
    db.commit()
    return payload


@router.put("/gather/regions/{region_id}")
def update_gather_region(
    region_id: str, payload: GatherRegionIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)
):
    row = db.query(GatherRegion).filter(GatherRegion.id == region_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    row.name = payload.name.strip()
    row.sort = payload.sort
    row.enabled = payload.enabled
    db.commit()
    return {"id": row.id, "name": row.name, "sort": row.sort, "enabled": row.enabled}


@router.delete("/gather/regions/{region_id}")
def delete_gather_region(region_id: str, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    if region_id == "all":
        raise HTTPException(400, "「全部」不可删除")
    row = db.query(GatherRegion).filter(GatherRegion.id == region_id).first()
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
    items = []
    for r in rows:
        detail_id = (r.detail_id or "").strip()
        cover = r.cover or ""
        title = r.title or ""
        price = float(r.price or 0)
        origin_price = float(r.origin_price or 0)
        sold_count = int(getattr(r, "sold_count", 0) or 0)
        if detail_id:
            store = find_nye_store(db, detail_id)
            if store:
                cover = store.cover or cover
                title = store.name or title
                price = nye_starting_price(store)
                origin_price = float(store.origin_price or 0) or origin_price
                sold_count = int(getattr(store, "sold_count", 0) or 0)
        items.append(
            {
                "id": r.id,
                "tab": r.tab,
                "region": getattr(r, "region", "") or "",
                "detail_id": detail_id,
                "cover": cover,
                "title": title,
                "tag": r.tag,
                "tags": loads(r.tags, []),
                "sold_text": r.sold_text,
                "sold_count": sold_count,
                "price": price,
                "origin_price": origin_price,
                "sort": r.sort,
                "enabled": r.enabled,
            }
        )
    return page_payload(items, total, page, page_size)


def _hydrate_gather_product_from_nye(db: Session, data: dict) -> dict:
    """封面/店名/起价跟宴会专题走；去哪聚只保留入口元数据。"""
    detail_id = (data.get("detail_id") or "").strip()
    if not detail_id:
        raise HTTPException(400, "请选择关联门店（封面、店名、套餐价在宴会专题配置）")
    store = find_nye_store(db, detail_id)
    if not store:
        raise HTTPException(400, "关联门店没有宴会专题，请先在「宴会专题」配置")
    data["detail_id"] = detail_id
    data["title"] = store.name or data.get("title") or detail_id
    data["cover"] = store.cover or data.get("cover") or ""
    data["price"] = nye_starting_price(store)
    data["origin_price"] = float(store.origin_price or 0)
    if not (data.get("tag") or "").strip():
        data["tag"] = store.tag or ""
    return data


@router.post("/gather/products")
def create_gather_product(payload: GatherProductIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    if db.query(GatherProduct).filter(GatherProduct.id == payload.id).first():
        raise HTTPException(400, "商品 ID 已存在")
    data = _hydrate_gather_product_from_nye(db, payload.model_dump())
    tags = data.pop("tags", [])
    row = GatherProduct(**data, tags=dumps(tags))
    db.add(row)
    db.commit()
    return {**data, "tags": tags}


@router.put("/gather/products/{product_id}")
def update_gather_product(product_id: str, payload: GatherProductIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    row = db.query(GatherProduct).filter(GatherProduct.id == product_id).first()
    if not row:
        raise HTTPException(404, "不存在")
    data = _hydrate_gather_product_from_nye(db, payload.model_dump())
    tags = data.pop("tags", [])
    data.pop("id", None)
    for k, v in data.items():
        setattr(row, k, v)
    row.tags = dumps(tags)
    db.commit()
    return {**data, "id": product_id, "tags": tags}


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
            "store_id": (getattr(r, "store_id", None) or "").strip() or r.id,
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


def _bind_nye_store(db: Session, nye_id: str, store_id: Optional[str]) -> str:
    """一家首页门店只对应一张专题详情。旧数据编号本身就是门店编号时允许原样保存。"""
    linked = (store_id or "").strip()
    if not linked:
        raise HTTPException(400, "请选择对应的首页门店")
    if not db.query(Store).filter(Store.id == linked).first() and linked != nye_id:
        raise HTTPException(400, "首页门店不存在")
    other = (
        db.query(NyeStore)
        .filter(NyeStore.store_id == linked, NyeStore.id != nye_id)
        .first()
    )
    if other:
        raise HTTPException(400, "该首页门店已经有专题详情")
    return linked


@router.post("/nye")
def create_nye(payload: NyeStoreIn, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    if db.query(NyeStore).filter(NyeStore.id == payload.id).first():
        raise HTTPException(400, "ID 已存在")
    data = payload.model_dump()
    linked = _bind_nye_store(db, data["id"], data.get("store_id"))
    row = NyeStore(
        id=data["id"],
        store_id=linked,
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
    incoming = data.get("store_id")
    if incoming is None:
        linked = (getattr(row, "store_id", None) or "").strip() or row.id
    else:
        linked = _bind_nye_store(db, row.id, incoming)
    row.store_id = linked
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
    release_stale_room_holds(db)
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
                "status_text": "待发货" if r.type == "mall" and r.status == "paid" else r.status_text,
                "contact_name": r.contact_name,
                "contact_phone": r.contact_phone,
                "people": r.people,
                "remark": r.remark,
                "room_date": r.room_date,
                "room_slot": r.room_slot,
                "openid": r.openid,
                "user_id": r.user_id,
                "extra": loads(r.extra or "{}", {}) or {},
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
    prev = row.status
    next_status = payload.status
    user = db.query(AppUser).filter(AppUser.id == row.user_id).first() if row.user_id else None

    # 取消/退款：释放包房、回退销量与积分
    if prev in ("pending", "paid", "completed", "refund_pending") and next_status in ("cancelled", "refunded"):
        release_room_if_needed(db, row)
        if prev in ("paid", "completed"):
            reverse_sold_on_refund(db, row)
            reverse_order_points(db, row, user)
            # 退回已使用的优惠券
            extra = loads(row.extra or "{}", {}) or {}
            uc_id = int(extra.get("couponId") or 0)
            if uc_id:
                uc = db.query(UserCoupon).filter(UserCoupon.id == uc_id).first()
                if uc and uc.status == "used":
                    uc.status = "unused"

    if prev not in ("paid", "completed") and next_status in ("paid", "completed"):
        if row.room_date and row.room_slot and row.store_id:
            hold_room_slot(db, row)

    row.status = next_status
    row.status_text = payload.status_text or STATUS_TEXT.get(next_status, next_status)
    # 后台把待支付标成待核销/已完成时，同样累计销量 / 会员桌数 / 消费积分
    if prev not in ("paid", "completed") and next_status in ("paid", "completed"):
        bump_sold_on_paid(db, row, user)
        award_order_points(db, row, user)
        if next_status == "paid":
            ensure_order_verify_code(db, row)
    elif user and next_status in ("paid", "completed", "cancelled", "refunded"):
        sync_user_vip(db, user)
    db.commit()
    return OkResponse(data={"id": row.id, "status": row.status, "status_text": row.status_text})


def _verify_order_item(db: Session, row: Order, user: Optional[AppUser] = None) -> dict:
    if row.status == "paid" and not (row.verify_code or "").strip():
        ensure_order_verify_code(db, row)
    phone = row.contact_phone or ""
    nickname = ""
    if row.user_id:
        if user is None or user.id != row.user_id:
            user = db.query(AppUser).filter(AppUser.id == row.user_id).first()
        if user:
            phone = phone or user.phone or ""
            nickname = user.nickname or ""
    return {
        "kind": "order",
        "id": row.id,
        "verify_code": row.verify_code or "",
        "title": row.title or "",
        "spec": row.spec or "",
        "store_name": row.store_name or "",
        "amount": row.amount or 0,
        "status": row.status,
        "status_text": row.status_text or "",
        "contact_name": row.contact_name or nickname,
        "contact_phone": phone,
        "room_date": row.room_date or "",
        "room_slot": row.room_slot or "",
        "people": row.people or 0,
        "can_verify": row.status == "paid",
    }


def _verify_coupon_item(db: Session, row: UserCoupon) -> dict:
    if row.status == "unused" and not (row.verify_code or "").strip():
        ensure_coupon_verify_code(db, row)
    user = db.query(AppUser).filter(AppUser.id == row.user_id).first()
    return {
        "kind": "coupon",
        "id": row.id,
        "verify_code": row.verify_code or "",
        "title": row.name or "",
        "spec": row.condition or "",
        "amount": row.amount or 0,
        "expire": row.expire or "",
        "status": row.status,
        "status_text": {"unused": "未使用", "used": "已使用", "expired": "已失效"}.get(row.status, row.status),
        "contact_name": user.nickname if user else "",
        "contact_phone": user.phone if user else "",
        "can_verify": row.status == "unused",
    }


def _verify_log_out(row: VerifyLog) -> dict:
    return {
        "id": row.id,
        "kind": row.kind,
        "target_id": row.target_id,
        "verify_code": row.verify_code,
        "title": row.title,
        "store_name": row.store_name,
        "contact_name": row.contact_name,
        "contact_phone": row.contact_phone,
        "amount": row.amount,
        "admin_name": row.admin_name,
        "created_at": row.created_at.strftime("%Y-%m-%d %H:%M:%S") if row.created_at else "",
    }


def _add_verify_log(
    db: Session,
    *,
    kind: str,
    target_id: str,
    verify_code: str,
    title: str,
    store_name: str,
    contact_name: str,
    contact_phone: str,
    amount: float,
    admin: AdminUser,
) -> VerifyLog:
    row = VerifyLog(
        kind=kind,
        target_id=str(target_id or ""),
        verify_code=verify_code or "",
        title=title or "",
        store_name=store_name or "",
        contact_name=contact_name or "",
        contact_phone=contact_phone or "",
        amount=float(amount or 0),
        admin_name=(admin.username if admin else "") or "",
        created_at=now_cn().replace(tzinfo=None),
    )
    db.add(row)
    return row


@router.get("/verify")
def search_verify(
    q: str = Query(""),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    keyword = (q or "").strip()
    if not keyword:
        raise HTTPException(400, "请输入手机号或核销码")
    orders: list[Order] = []
    coupons: list[UserCoupon] = []
    if keyword.isdigit() and len(keyword) == 8:
        orders = [r for r in db.query(Order).filter(Order.verify_code == keyword).all() if r.type != "mall"]
        coupons = db.query(UserCoupon).filter(UserCoupon.verify_code == keyword).all()
    else:
        like = f"%{keyword}%"
        users = db.query(AppUser).filter(AppUser.phone.like(like)).all()
        user_ids = [u.id for u in users]
        oq = db.query(Order).filter(Order.status == "paid", Order.type != "mall")
        cq = db.query(UserCoupon).filter(UserCoupon.status == "unused")
        if user_ids:
            oq = oq.filter((Order.contact_phone.like(like)) | (Order.user_id.in_(user_ids)))
            cq = cq.filter(UserCoupon.user_id.in_(user_ids))
        else:
            oq = oq.filter(Order.contact_phone.like(like))
            cq = cq.filter(UserCoupon.id == -1)
        orders = oq.order_by(Order.created_at.desc()).limit(20).all()
        coupons = cq.order_by(UserCoupon.id.desc()).limit(20).all()
    for row in coupons:
        mark_coupon_expired(row)
    coupons = [row for row in coupons if row.status == "unused" or (keyword.isdigit() and len(keyword) == 8)]
    payload = [_verify_order_item(db, r) for r in orders] + [_verify_coupon_item(db, r) for r in coupons]
    db.commit()
    return {"list": payload}


@router.get("/verify/logs")
def list_verify_logs(
    date: str = Query(""),
    kind: str = Query(""),
    keyword: str = Query(""),
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    page, page_size, offset = normalize_page(page, page_size)
    day = (date or "").strip() or today_cn()
    try:
        start = datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "日期格式无效")
    end = start + timedelta(days=1)
    q = db.query(VerifyLog).filter(VerifyLog.created_at >= start, VerifyLog.created_at < end)
    if kind in ("order", "coupon"):
        q = q.filter(VerifyLog.kind == kind)
    kw = (keyword or "").strip()
    if kw:
        like = f"%{kw}%"
        q = q.filter(
            (VerifyLog.verify_code.like(like))
            | (VerifyLog.contact_phone.like(like))
            | (VerifyLog.title.like(like))
            | (VerifyLog.contact_name.like(like))
        )
    q = q.order_by(VerifyLog.id.desc())
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    return page_payload([_verify_log_out(r) for r in rows], total, page, page_size)


@router.post("/verify")
def confirm_verify(
    payload: dict,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    kind = str(payload.get("kind") or "")
    item_id = payload.get("id")
    if kind == "order":
        row = db.query(Order).filter(Order.id == str(item_id)).first()
        if not row:
            raise HTTPException(404, "订单不存在")
        if row.type == "mall":
            raise HTTPException(400, "积分兑换请按收货地址发货，不能到店核销")
        if row.status == "completed":
            return {"ok": False, "message": "该订单已核销", "item": _verify_order_item(db, row)}
        if row.status != "paid":
            raise HTTPException(400, f"当前状态不可核销：{row.status_text or row.status}")
        row.status = "completed"
        row.status_text = STATUS_TEXT.get("completed", "已完成")
        user = db.query(AppUser).filter(AppUser.id == row.user_id).first() if row.user_id else None
        if user:
            sync_user_vip(db, user)
        _add_verify_log(
            db,
            kind="order",
            target_id=str(row.id),
            verify_code=row.verify_code or "",
            title=row.title or "",
            store_name=row.store_name or "",
            contact_name=row.contact_name or "",
            contact_phone=row.contact_phone or "",
            amount=float(row.amount or 0),
            admin=admin,
        )
        db.commit()
        return {"ok": True, "message": "订单已核销", "item": _verify_order_item(db, row)}
    if kind == "coupon":
        try:
            cid = int(item_id)
        except (TypeError, ValueError):
            raise HTTPException(400, "优惠券无效")
        row = db.query(UserCoupon).filter(UserCoupon.id == cid).first()
        if not row:
            raise HTTPException(404, "优惠券不存在")
        if mark_coupon_expired(row):
            db.commit()
            return {"ok": False, "message": "该优惠券已过期", "item": _verify_coupon_item(db, row)}
        if row.status == "used":
            return {"ok": False, "message": "该优惠券已核销", "item": _verify_coupon_item(db, row)}
        if row.status != "unused":
            raise HTTPException(400, "该优惠券不可核销")
        row.status = "used"
        user = db.query(AppUser).filter(AppUser.id == row.user_id).first() if row.user_id else None
        _add_verify_log(
            db,
            kind="coupon",
            target_id=str(row.id),
            verify_code=row.verify_code or "",
            title=row.name or "到店券",
            store_name="",
            contact_name=(user.nickname if user else "") or "",
            contact_phone=(user.phone if user else "") or "",
            amount=float(row.amount or 0),
            admin=admin,
        )
        db.commit()
        return {"ok": True, "message": "优惠券已核销", "item": _verify_coupon_item(db, row)}
    raise HTTPException(400, "核销类型无效")


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
    release_stale_room_holds(db)
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
    return page_payload(
        [
            {
                "id": r.id,
                "openid": r.openid,
                "nickname": r.nickname or "",
                "avatar": r.avatar or "",
                "phone": r.phone or "",
                "points": r.points or 0,
                "vip_level": r.vip_level or "",
                "table_count": table_count(db, r.id),
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
        total,
        page,
        page_size,
    )


def _user_or_404(db: Session, user_id: int) -> AppUser:
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    return user


def _user_detail(db: Session, user: AppUser) -> dict:
    return {
        "id": user.id,
        "openid": user.openid or "",
        "nickname": user.nickname or "",
        "avatar": user.avatar or "",
        "phone": user.phone or "",
        "birthday": getattr(user, "birthday", "") or "",
        "hobby": getattr(user, "hobby", "") or "",
        "points": user.points or 0,
        "vip_level": user.vip_level or "V0",
        "vip_manual": bool(getattr(user, "vip_manual", False)),
        "table_count": table_count(db, user.id),
        "phone_edited": bool(getattr(user, "phone_edited", False)),
        "cancelled": bool(getattr(user, "cancelled", False)),
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    return _user_detail(db, _user_or_404(db, user_id))


@router.get("/users/{user_id}/points")
def list_user_points(
    user_id: int,
    page: int = Query(1),
    page_size: int = Query(20),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    user = _user_or_404(db, user_id)
    page, page_size, offset = normalize_page(page, page_size)
    q = (
        db.query(PointLedger)
        .filter(PointLedger.user_id == user.id)
        .order_by(PointLedger.created_at.desc(), PointLedger.id.desc())
    )
    total = q.count()
    rows = q.offset(offset).limit(page_size).all()
    payload = page_payload(
        [
            {
                "id": r.id,
                "title": r.title,
                "value": r.value,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
            }
            for r in rows
        ],
        total,
        page,
        page_size,
    )
    payload["balance"] = user.points or 0
    return payload


@router.get("/users/{user_id}/coupons")
def list_user_coupons(
    user_id: int,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    _user_or_404(db, user_id)
    rows = (
        db.query(UserCoupon)
        .filter(UserCoupon.user_id == user_id)
        .order_by(UserCoupon.id.desc())
        .all()
    )
    dirty = False
    for row in rows:
        if mark_coupon_expired(row):
            dirty = True
    if dirty:
        db.commit()
    return [
        {
            "id": r.id,
            "coupon_id": r.coupon_id,
            "name": r.name,
            "amount": r.amount,
            "condition": r.condition,
            "expire": r.expire,
            "status": r.status,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
        }
        for r in rows
    ]


@router.post("/users/{user_id}/coupons")
def issue_user_coupon(
    user_id: int,
    coupon_id: int = Query(...),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    user = _user_or_404(db, user_id)
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(404, "优惠券模板不存在")
    if coupon.total and coupon.claimed >= coupon.total:
        raise HTTPException(400, "优惠券已领完")
    row = UserCoupon(
        user_id=user.id,
        coupon_id=coupon.id,
        name=coupon.name,
        amount=coupon.amount,
        condition=coupon.condition,
        expire=coupon.expire or "",
        status="unused",
    )
    coupon.claimed = int(coupon.claimed or 0) + 1
    db.add(row)
    db.flush()
    ensure_coupon_verify_code(db, row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "coupon_id": row.coupon_id,
        "name": row.name,
        "amount": row.amount,
        "condition": row.condition,
        "expire": row.expire,
        "status": row.status,
    }


@router.post("/users/{user_id}/coupons/{uc_id}/void")
def void_user_coupon(
    user_id: int,
    uc_id: int,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    _user_or_404(db, user_id)
    row = (
        db.query(UserCoupon)
        .filter(UserCoupon.id == uc_id, UserCoupon.user_id == user_id)
        .first()
    )
    if not row:
        raise HTTPException(404, "用户优惠券不存在")
    if row.status != "unused":
        raise HTTPException(400, "仅未使用的券可作废")
    row.status = "expired"
    db.commit()
    return {"id": row.id, "status": row.status}


@router.get("/users/{user_id}/addresses")
def list_user_addresses(
    user_id: int,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    _user_or_404(db, user_id)
    rows = (
        db.query(Address)
        .filter(Address.user_id == user_id)
        .order_by(Address.is_default.desc(), Address.id.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "name": r.name,
            "phone": r.phone,
            "region": r.region or f"{r.province or ''}{r.city or ''}{r.district or ''}".strip(),
            "province": r.province or "",
            "city": r.city or "",
            "district": r.district or "",
            "detail": r.detail or "",
            "is_default": bool(r.is_default),
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
        }
        for r in rows
    ]


@router.post("/users/{user_id}/points")
def adjust_points(
    user_id: int,
    payload: PointsAdjustIn,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    user = _user_or_404(db, user_id)
    add_points(db, user, payload.title or "后台调整", int(payload.points or 0))
    db.commit()
    db.refresh(user)
    return {"id": user.id, "points": user.points}


@router.put("/users/{user_id}/vip")
def update_vip(
    user_id: int,
    vip_level: str = Query(...),
    lock: bool = Query(True, description="锁定手动等级，避免被桌数自动覆盖"),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    user = _user_or_404(db, user_id)
    user.vip_level = vip_level.upper()
    user.vip_manual = bool(lock)
    db.commit()
    return {
        "id": user.id,
        "vip_level": user.vip_level,
        "vip_manual": user.vip_manual,
        "table_count": table_count(db, user.id),
    }


# ---- site config ----
CMS_DEFAULTS: dict[str, Any] = {
    "privacy_collect": PRIVACY_COLLECT,
    "privacy_share": PRIVACY_SHARE,
    "member": MEMBER_CONFIG,
    "agreements": AGREEMENTS,
    "hobby_options": HOBBY_OPTIONS,
    "checkin": CHECKIN_CONFIG,
    "loyalty": LOYALTY_CONFIG,
}


def _cms_value_empty(key: str, value: Any) -> bool:
    if not isinstance(value, dict) or not value:
        return True
    if key in ("privacy_collect", "privacy_share"):
        return not (value.get("sections") or [])
    if key == "member":
        return not (value.get("levels") or [])
    if key == "agreements":
        return not value
    if key == "hobby_options":
        items = value.get("items") or []
        return not any(str(i.get("name") or "").strip() for i in items if isinstance(i, dict))
    if key == "checkin":
        return value.get("dailyPoints") is None and not (value.get("milestones") or [])
    if key == "loyalty":
        return value.get("earnRateDefault") is None and value.get("vipTables") is None
    return False


def _resolve_cms_value(db: Session, key: str) -> Any:
    value = get_config(db, key, {})
    default = CMS_DEFAULTS.get(key)
    if default is not None and _cms_value_empty(key, value):
        set_config(db, key, default)
        return default
    return value if value is not None else {}


@router.get("/config/{key}")
def get_site_config(key: str, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    return {"key": key, "value": _resolve_cms_value(db, key)}


@router.put("/config/{key}")
def put_site_config(
    key: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    value = payload.get("value", payload)
    if key in CMS_DEFAULTS and _cms_value_empty(key, value):
        raise HTTPException(400, "内容不能为空，请填写后再保存（或刷新页面从模板恢复）")
    set_config(db, key, value)
    return {"key": key, "value": value}


@router.post("/config/{key}/restore")
def restore_site_config(key: str, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)):
    default = CMS_DEFAULTS.get(key)
    if default is None:
        raise HTTPException(400, "该配置不支持从模板恢复")
    set_config(db, key, default)
    return {"key": key, "value": default}
