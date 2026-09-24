"""初始化管理员账号与演示数据。"""

from __future__ import annotations

from sqlalchemy.orm import Session

from .cms_data import (
    AGREEMENTS,
    CHECKIN_CONFIG,
    DEFAULT_ACTIVITIES,
    HOBBY_OPTIONS,
    LOYALTY_CONFIG,
    MEMBER_CONFIG,
    PRIVACY_COLLECT,
    PRIVACY_SHARE,
    default_nye_packages,
    default_theme_packages,
)
from .config import DEFAULT_ADMIN_PASSWORD, DEFAULT_JWT_SECRET, get_settings
from .deps import hash_password, verify_password
from .wx import wx_configured
from .models import (
    AdminUser,
    Banner,
    Coupon,
    GatherProduct,
    GatherRegion,
    GatherTab,
    MallGoods,
    NyeStore,
    RecommendItem,
    Store,
)
from .utils import dumps, get_config, loads, set_config

settings = get_settings()


def demo_img(seed: str, w: int = 800, h: int = 600) -> str:
    """业务模块占位图（不依赖小程序本地包）。"""
    return f"https://picsum.photos/seed/gather-{seed}/{w}/{h}"


STORES = [
    {
        "id": "shibo",
        "name": "天天俱乐部上海世博店",
        "cover": demo_img("store-shibo"),
        "address": "上海市浦东新区长清路92号 中邻上钢里3楼",
        "route": "地铁长清路站7号线2号出口，13号线7号出口，步行后进入到中邻上钢里商场内3楼",
        "phone": "4001919179",
        "lat": 31.1846,
        "lng": 121.4852,
        "sort": 1,
    },
    {
        "id": "xinzhuang",
        "name": "天天俱乐部上海莘庄店",
        "cover": demo_img("store-xinzhuang"),
        "address": "上海市闵行区都市路5001号5楼",
        "route": "地铁1/5号线莘庄站南1口出，步行约600米至莘庄仲盛世界商城5楼",
        "phone": "4001919179",
        "lat": 31.1134,
        "lng": 121.3851,
        "sort": 2,
    },
    {
        "id": "yaxin",
        "name": "天天俱乐部上海亚新店",
        "cover": demo_img("store-yaxin"),
        "address": "上海市普陀区长寿路401号3号楼2楼",
        "route": "地铁7、13号线长寿路站7号口出来左转步行50米进入亚新广场内",
        "phone": "4001919179",
        "lat": 31.2432,
        "lng": 121.4374,
        "sort": 3,
    },
    {
        "id": "gongkang",
        "name": "天天俱乐部上海共康店",
        "cover": demo_img("store-gongkang"),
        "address": "上海市宝山区共和新路5000弄绿地新都会1号楼二楼",
        "route": "地铁1号线共康路站下4号口出往北直行过共康路约200米",
        "phone": "4001919179",
        "lat": 31.3208,
        "lng": 121.4476,
        "sort": 4,
    },
    {
        "id": "ningbo",
        "name": "宁波天天俱乐部天一店",
        "cover": demo_img("store-ningbo"),
        "address": "浙江省宁波市海曙区中山路220号第二百货商店7楼",
        "route": "地铁1号线东门口站A出口",
        "phone": "4001919179",
        "lat": 29.8684,
        "lng": 121.5502,
        "sort": 5,
    },
]

# 去哪聚顶部 Tab：按「怎么聚」分类（不是单点菜/精品套餐）
GATHER_TABS = [
    {"key": "day", "name": "聚一天", "show_sold": True, "sort": 1},
    {"key": "meal", "name": "聚个餐", "show_sold": True, "sort": 2},
    {"key": "room", "name": "包房局", "show_sold": True, "sort": 3},
    {"key": "biz", "name": "商务宴", "show_sold": True, "sort": 4},
]

GATHER_REGIONS = [
    {"id": "all", "name": "全部", "sort": 0},
    {"id": "jiangsu", "name": "江苏省", "sort": 1},
    {"id": "shanghai", "name": "上海市", "sort": 2},
    {"id": "ningbo", "name": "宁波市", "sort": 3},
]

# 去哪聚总库：每张卡独立商品；tag=所属活动（年夜饭/家宴/宴席）；tags=卖点
GATHER_PRODUCTS = [
    # 聚一天
    {
        "id": "d1",
        "tab": "day",
        "region": "shanghai",
        "detail_id": "xinzhuang",
        "title": "莘庄店·2027年夜饭专场",
        "tag": "年夜饭",
        "tags": ["大厅+包厢", "可预订"],
        "cover": demo_img("gather-d1-nye"),
        "price": 2688,
        "origin_price": 3688,
        "sort": 1,
    },
    {
        "id": "d2",
        "tab": "day",
        "region": "shanghai",
        "detail_id": "gongkang",
        "title": "共康店·年夜饭家庭日",
        "tag": "年夜饭",
        "tags": ["近地铁", "亲子友好"],
        "cover": demo_img("gather-d2-nye"),
        "price": 2388,
        "origin_price": 2988,
        "sort": 2,
    },
    {
        "id": "d5",
        "tab": "day",
        "region": "shanghai",
        "detail_id": "yaxin",
        "title": "亚新店·同学聚会一整天",
        "tag": "家宴",
        "tags": ["棋牌", "投影"],
        "cover": demo_img("gather-d5-party"),
        "price": 1288,
        "origin_price": 1688,
        "sort": 3,
    },
    {
        "id": "d8",
        "tab": "day",
        "region": "shanghai",
        "detail_id": "shibo",
        "title": "世博店·亲子欢乐日",
        "tag": "家宴",
        "tags": ["儿童餐", "活动区"],
        "cover": demo_img("gather-d8-kids"),
        "price": 988,
        "origin_price": 1288,
        "sort": 4,
    },
    # 聚个餐
    {
        "id": "m1",
        "tab": "meal",
        "region": "shanghai",
        "detail_id": "xinzhuang",
        "title": "莘庄店·团圆家宴（10人）",
        "tag": "家宴",
        "tags": ["近地铁", "包厢"],
        "cover": demo_img("gather-m1-family"),
        "price": 799,
        "origin_price": 999,
        "sort": 1,
    },
    {
        "id": "m2",
        "tab": "meal",
        "region": "shanghai",
        "detail_id": "yaxin",
        "title": "亚新店·帝王蟹海鲜宴（10人）",
        "tag": "宴席",
        "tags": ["海鲜", "沉浸式"],
        "cover": demo_img("gather-m2-seafood"),
        "price": 1888,
        "origin_price": 2288,
        "sort": 2,
    },
    {
        "id": "m3",
        "tab": "meal",
        "region": "shanghai",
        "detail_id": "gongkang",
        "title": "共康店·喜气羊羊宴（10-12人）",
        "tag": "宴席",
        "tags": ["生日宴", "可定制"],
        "cover": demo_img("gather-m3-sheep"),
        "price": 1288,
        "origin_price": 1588,
        "sort": 3,
    },
    {
        "id": "m4",
        "tab": "meal",
        "region": "shanghai",
        "detail_id": "shibo",
        "title": "世博店·本帮家常宴",
        "tag": "家宴",
        "tags": ["本帮菜", "直营"],
        "cover": demo_img("gather-m4-local"),
        "price": 699,
        "origin_price": 899,
        "sort": 4,
    },
    # 包房局
    {
        "id": "r1",
        "tab": "room",
        "region": "shanghai",
        "detail_id": "xinzhuang",
        "title": "莘庄店·六人棋牌包房",
        "tag": "家宴",
        "tags": ["麻将", "可延长"],
        "cover": demo_img("gather-r1-mahjong"),
        "price": 399,
        "origin_price": 499,
        "sort": 1,
    },
    {
        "id": "r2",
        "tab": "room",
        "region": "shanghai",
        "detail_id": "yaxin",
        "title": "亚新店·双桌豪华包厢",
        "tag": "宴席",
        "tags": ["独立卫浴", "沙发区"],
        "cover": demo_img("gather-r2-vip"),
        "price": 1299,
        "origin_price": 1599,
        "sort": 2,
    },
    {
        "id": "r3",
        "tab": "room",
        "region": "shanghai",
        "detail_id": "gongkang",
        "title": "共康店·通宵娱乐包场",
        "tag": "家宴",
        "tags": ["通宵", "含早餐"],
        "cover": demo_img("gather-r3-night"),
        "price": 1599,
        "origin_price": 1999,
        "sort": 3,
    },
    # 商务宴
    {
        "id": "b1",
        "tab": "biz",
        "region": "shanghai",
        "detail_id": "shibo",
        "title": "世博店·商务宴请套餐",
        "tag": "宴席",
        "tags": ["含茶歇", "可开发票"],
        "cover": demo_img("gather-b1-biz"),
        "price": 1588,
        "origin_price": 1988,
        "sort": 1,
    },
    {
        "id": "b2",
        "tab": "biz",
        "region": "ningbo",
        "detail_id": "ningbo",
        "title": "宁波天一店·客户接待宴",
        "tag": "宴席",
        "tags": ["地铁直达", "静音包厢"],
        "cover": demo_img("gather-b2-ningbo"),
        "price": 1188,
        "origin_price": 1488,
        "sort": 2,
    },
]


def ensure_default_activities(db: Session) -> None:
    """补齐默认活动（年夜饭/家宴/宴席），不覆盖已有自定义项。"""
    raw = get_config(db, "activities")
    if isinstance(raw, dict):
        items = raw.get("list")
    else:
        items = raw
    if not isinstance(items, list):
        items = []
    by_id = {str(x.get("id")): dict(x) for x in items if isinstance(x, dict) and x.get("id")}
    changed = False
    for d in DEFAULT_ACTIVITIES:
        aid = d["id"]
        if aid not in by_id:
            by_id[aid] = dict(d)
            changed = True
        else:
            row = by_id[aid]
            # 补缺字段，不改已填名称/标识
            for key in ("banners", "open_start", "open_end", "enabled", "sort", "tag", "name"):
                if key not in row or row.get(key) in (None, ""):
                    if key in d and d[key] not in (None, ""):
                        row[key] = d[key]
                        changed = True
            if "enabled" not in row:
                row["enabled"] = True
                changed = True
    if changed or not items:
        merged = list(by_id.values())
        merged.sort(key=lambda x: (int(x.get("sort") or 0), str(x.get("id") or "")))
        set_config(db, "activities", merged)


def sync_gather_demo_catalog(db: Session) -> None:
    """把去哪聚演示目录刷成聚会业务数据（一次性 v2）。

    正式环境（已配微信密钥）不跑，避免覆盖运营已改的商品。
    """
    if get_config(db, "gather_demo_catalog_v2"):
        return
    if wx_configured():
        # 正式库只打标记，不改目录
        set_config(db, "gather_demo_catalog_v2", "1")
        set_config(db, "gather_demo_variety_v1", "1")
        db.commit()
        return

    existing_tabs = {t.key: t for t in db.query(GatherTab).all()}
    for item in GATHER_TABS:
        row = existing_tabs.get(item["key"])
        if row:
            row.name = item["name"]
            row.show_sold = item["show_sold"]
            row.sort = item["sort"]
            row.enabled = True
        else:
            db.add(GatherTab(**item, enabled=True))

    # 旧「招牌菜 / 精品套餐」只下架，不硬删（避免误伤关联订单引用）
    for key in ("dish", "set"):
        row = existing_tabs.get(key)
        if row:
            row.enabled = False
    for row in db.query(GatherProduct).filter(GatherProduct.tab.in_(("dish", "set"))).all():
        row.enabled = False

    demo_ids = {item["id"] for item in GATHER_PRODUCTS}
    store_ids = {item["id"] for item in STORES}
    # 下架门店编号遗留卡、以及 0.01 占位价测试商品
    for row in db.query(GatherProduct).all():
        if row.id in demo_ids:
            continue
        if row.id in store_ids or float(row.price or 0) <= 0.01:
            row.enabled = False

    catalog = _nye_catalog_by_store()
    home_stores = {s.id: s for s in db.query(Store).all()}
    for item in GATHER_PRODUCTS:
        fields = _build_gather_product_fields(item, catalog)
        home = home_stores.get(fields.get("detail_id") or "")
        if home:
            if not fields.get("address"):
                fields["address"] = home.address or ""
            if not fields.get("route"):
                fields["route"] = home.route or ""
            if not fields.get("lat"):
                fields["lat"] = float(home.lat or 0)
            if not fields.get("lng"):
                fields["lng"] = float(home.lng or 0)
        row = db.query(GatherProduct).filter(GatherProduct.id == fields["id"]).first()
        if row:
            # 已有演示卡只补空字段 / 套餐，不覆盖运营已改标题封面
            for key, value in fields.items():
                if key == "id":
                    continue
                cur = getattr(row, key, None)
                empty = cur is None or cur == "" or cur == "[]" or cur == "{}" or cur == 0
                if empty or (key == "packages" and not loads(getattr(row, "packages", None) or "[]", [])):
                    setattr(row, key, value)
            row.enabled = True
        else:
            db.add(GatherProduct(**fields))

    ensure_default_activities(db)

    set_config(db, "gather_demo_catalog_v2", "1")
    set_config(db, "gather_demo_variety_v1", "1")
    db.commit()


def _build_gather_product_fields(item: dict, catalog: dict) -> dict:
    """从门店目录拼出完整商品字段；非年夜饭主题用独立标题/套餐。"""
    payload = dict(item)
    tags = payload.pop("tags", [])
    detail_id = (payload.get("detail_id") or "").strip()
    tag = (payload.get("tag") or "").strip()
    src = catalog.get(detail_id) or {}
    is_nye = tag == "年夜饭"
    cover = payload.get("cover") or src.get("cover") or demo_img(f"gather-{payload.get('id')}")
    price = float(payload.get("price") or src.get("price") or (2388 if is_nye else 799))
    origin_price = float(payload.get("origin_price") or src.get("origin_price") or 0)
    if is_nye:
        title = payload.get("title") or src.get("name") or detail_id
        pkgs = default_nye_packages(price, cover)
        open_start = src.get("open_start") or "2027-02-05"
        open_end = src.get("open_end") or "2027-02-12"
        banners = payload.get("banners") or src.get("banners") or ([cover] if cover else [])
        detail_images = payload.get("detail_images") or src.get("detail_images") or []
    else:
        store_label = (src.get("name") or detail_id or "").split("-")[0] or detail_id
        title = payload.get("title") or f"{store_label}-{tag}"
        pkgs = default_theme_packages(price, cover)
        open_start = ""
        open_end = ""
        banners = payload.get("banners") or (
            [cover, demo_img(f"gather-{payload.get('id')}-b2"), demo_img(f"gather-{payload.get('id')}-b3")]
            if cover
            else []
        )
        detail_images = payload.get("detail_images") or [
            demo_img(f"gather-{payload.get('id')}-d1", 900, 1200),
            demo_img(f"gather-{payload.get('id')}-d2", 900, 1200),
        ]
    return {
        **payload,
        "title": title,
        "cover": cover,
        "price": price,
        "origin_price": origin_price,
        "address": payload.get("address") or src.get("address") or "",
        "route": payload.get("route") or src.get("route") or "",
        "lat": float(payload.get("lat") or src.get("lat") or 0),
        "lng": float(payload.get("lng") or src.get("lng") or 0),
        "banners": dumps(banners),
        "detail_images": dumps(detail_images),
        "recent_buy": dumps(payload.get("recent_buy") or {}),
        "packages": dumps(pkgs),
        "open_start": payload.get("open_start") or open_start,
        "open_end": payload.get("open_end") or open_end,
        "tags": dumps(tags),
        "enabled": True,
    }

NYE_STORES = [
    {
        "id": "gongkang",
        "name": "上海共康店-天天俱乐部-2027年夜饭",
        "cover": demo_img("nye-gongkang"),
        "price": 2388,
        "tag": "年夜饭",
        "address": "共和新路5000弄绿地新都会1号楼二楼",
        "route": "地铁1号线共康路站下4号口出往北直行过共康路约200米",
        "lat": 31.3208,
        "lng": 121.4476,
        "banners": [demo_img("nye-b1"), demo_img("nye-b2"), demo_img("nye-b3")],
        "detail_images": [demo_img("nye-d1", 900, 1200), demo_img("nye-d2", 900, 1200)],
        "recent_buy": {},
        "sort": 1,
    },
    {
        "id": "shibo",
        "name": "上海世博店-天天俱乐部-2027年夜饭",
        "cover": demo_img("nye-shibo"),
        "price": 2688,
        "tag": "年夜饭",
        "address": "浦东新区长清路92号中邻上钢里3楼",
        "route": "地铁长清路站7号线2号出口，13号线7号出口",
        "lat": 31.1846,
        "lng": 121.4852,
        "banners": [demo_img("nye-b2"), demo_img("nye-b1"), demo_img("nye-b3")],
        "detail_images": [demo_img("nye-d1", 900, 1200), demo_img("nye-d3", 900, 1200)],
        "recent_buy": {},
        "sort": 2,
    },
    {
        "id": "yaxin",
        "name": "上海亚新店-天天俱乐部-2027年夜饭",
        "cover": demo_img("nye-yaxin"),
        "price": 2688,
        "origin_price": 3488,
        "tag": "年夜饭",
        "address": "普陀区长寿路401号3号楼2楼",
        "route": "地铁7、13号线长寿路站7号口",
        "lat": 31.2432,
        "lng": 121.4374,
        "banners": [demo_img("nye-b3"), demo_img("nye-b1")],
        "detail_images": [demo_img("nye-d2", 900, 1200)],
        "recent_buy": {},
        "sort": 3,
    },
    {
        "id": "xinzhuang",
        "name": "上海莘庄店-天天俱乐部-2027年夜饭",
        "cover": demo_img("nye-xinzhuang"),
        "price": 2688,
        "origin_price": 3688,
        "tag": "年夜饭",
        "address": "闵行区都市路5001号5楼",
        "route": "地铁1/5号线莘庄站南1口出",
        "lat": 31.1134,
        "lng": 121.3851,
        "banners": [demo_img("nye-b1"), demo_img("nye-b3")],
        "detail_images": [demo_img("nye-d1", 900, 1200), demo_img("nye-d2", 900, 1200)],
        "recent_buy": {},
        "sort": 4,
    },
]


def _nye_catalog_by_store() -> dict:
    return {item["id"]: item for item in NYE_STORES}


MALL_USAGE = "适用于天天俱乐部上海共康店、亚新生活广场、上海莘庄店、上钢新邻里3楼，凭兑换码到店使用。"
MALL_VALID = "领取后立即生效，有效期30天。"

MALL_GOODS = [
    {"name": "鱼缸投币挑战 (3次)", "title": "鱼缸投币挑战 (3枚祈福币)", "cover": demo_img("mall-1", 600, 600), "cost": 300, "sort": 1},
    {"name": "百事可乐一瓶1.25L", "cover": demo_img("mall-2", 600, 600), "cost": 500, "sort": 2},
    {"name": "雪碧一瓶1.25L", "cover": demo_img("mall-3", 600, 600), "cost": 500, "sort": 3},
    {"name": "美汁源果粒橙一瓶1.25L", "cover": demo_img("mall-4", 600, 600), "cost": 500, "sort": 4},
    {"name": "光明啤酒", "cover": demo_img("mall-5", 600, 600), "cost": 800, "sort": 5},
    {"name": "鱼林扑克", "cover": demo_img("mall-6", 600, 600), "cost": 200, "sort": 6},
    {"name": "葱烤海参烩鱼肚1份", "cover": demo_img("mall-7", 600, 600), "cost": 2500, "sort": 7},
    {"name": "壹聚黄酒（8年纯酿）", "cover": demo_img("mall-8", 600, 600), "cost": 3000, "sort": 8},
    {"name": "麻将桌券1份", "cover": demo_img("mall-9", 600, 600), "cost": 3000, "sort": 9},
    {"name": "鲍鱼炒年糕1份", "cover": demo_img("mall-10", 600, 600), "cost": 2500, "sort": 10},
    {"name": "蜂蜜小烤肉1份", "cover": demo_img("mall-11", 600, 600), "cost": 2000, "sort": 11},
]

RECOMMEND_BANNERS = [demo_img("rec-b1", 1200, 500), demo_img("rec-b2", 1200, 500), demo_img("rec-b3", 1200, 500)]
RECOMMEND_ITEMS = [
    {"name": "太仓锦江国际酒店", "cover": demo_img("rec-1"), "price": 249, "sort": 1},
    {"name": "苏州知音温德姆至尊酒店", "cover": demo_img("rec-2"), "price": 324, "sort": 2},
    {"name": "3天2晚(含2早1正)|苏州同里湖大饭店", "cover": demo_img("rec-3"), "price": 599, "sort": 3},
    {"name": "苏州金陵南林饭店", "cover": demo_img("rec-4"), "price": 229, "sort": 4},
    {"name": "江阴城发金茂嘉悦酒店", "cover": demo_img("rec-5"), "price": 399, "sort": 5},
    {"name": "3天2晚(含2早2正)|常州远洲酒店", "cover": demo_img("rec-6"), "price": 459, "sort": 6},
    {"name": "无锡希尔顿逸林酒店", "cover": demo_img("rec-7"), "price": 369, "sort": 7},
    {"name": "南通新城吾悦精选酒店", "cover": demo_img("rec-8"), "price": 289, "sort": 8},
    {"name": "常熟虞城希尔顿欢朋酒店", "cover": demo_img("rec-9"), "price": 319, "sort": 9},
]


def _needs_demo_cover(url: str) -> bool:
    u = (url or "").strip()
    return (not u) or u.startswith("/static/")


def refresh_demo_covers(db: Session) -> None:
    """把仍指向失效 /static 的业务图刷成占位图（不影响已上传的 COS 地址）。

    正式环境跳过，避免启动时把运营素材误刷成 picsum。
    """
    if wx_configured():
        return

    def _patch_list(items: list, factory) -> list:
        if not items:
            return factory()
        changed = False
        out = []
        for i, x in enumerate(items):
            if _needs_demo_cover(x):
                out.append(factory()[min(i, 2)])
                changed = True
            else:
                out.append(x)
        return out if changed else items

    for row in db.query(Store).all():
        if _needs_demo_cover(row.cover):
            row.cover = demo_img(f"store-{row.id}")
    for row in db.query(Banner).all():
        if _needs_demo_cover(row.image):
            row.image = demo_img(f"banner-{row.id}", 1200, 500)
    for row in db.query(GatherProduct).all():
        if _needs_demo_cover(row.cover):
            row.cover = demo_img(f"gather-{row.id}")
        banners = loads(row.banners, [])
        patched = _patch_list(
            banners if isinstance(banners, list) else [],
            lambda: [demo_img(f"gather-{row.id}-b{i}") for i in range(1, 4)],
        )
        if patched is not banners:
            row.banners = dumps(patched)
        details = loads(row.detail_images, [])
        patched_d = _patch_list(
            details if isinstance(details, list) else [],
            lambda: [demo_img(f"gather-{row.id}-d{i}", 900, 1200) for i in range(1, 3)],
        )
        if patched_d is not details:
            row.detail_images = dumps(patched_d)
    for row in db.query(NyeStore).all():
        if _needs_demo_cover(row.cover):
            row.cover = demo_img(f"nye-{row.id}")
        banners = loads(row.banners, [])
        patched = _patch_list(
            banners if isinstance(banners, list) else [],
            lambda: [demo_img(f"nye-{row.id}-b{i}") for i in range(1, 4)],
        )
        if patched is not banners:
            row.banners = dumps(patched)
        details = loads(row.detail_images, [])
        patched_d = _patch_list(
            details if isinstance(details, list) else [],
            lambda: [demo_img(f"nye-{row.id}-d{i}", 900, 1200) for i in range(1, 3)],
        )
        if patched_d is not details:
            row.detail_images = dumps(patched_d)
    for row in db.query(RecommendItem).all():
        if _needs_demo_cover(row.cover):
            row.cover = demo_img(f"rec-{row.id}")
    for row in db.query(MallGoods).all():
        if _needs_demo_cover(row.cover):
            row.cover = demo_img(f"mall-{row.id}", 600, 600)
    rec = dict(get_config(db, "recommend") or {})
    banners = rec.get("banners") or []
    if not banners:
        set_config(db, "recommend", {"banners": RECOMMEND_BANNERS})
    elif any(_needs_demo_cover(x) for x in banners):
        patched = []
        for i, x in enumerate(banners):
            if _needs_demo_cover(x):
                patched.append(RECOMMEND_BANNERS[min(i, len(RECOMMEND_BANNERS) - 1)])
            else:
                patched.append(x)
        set_config(db, "recommend", {"banners": patched})
    db.commit()


def seed_all(db: Session) -> None:
    if not db.query(AdminUser).filter(AdminUser.username == settings.admin_username).first():
        db.add(
            AdminUser(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
            )
        )
        db.commit()

    if db.query(Store).count() == 0:
        for item in STORES:
            db.add(Store(**item, enabled=True))
        db.commit()

    if db.query(Banner).count() == 0:
        db.add(Banner(image=demo_img("home-banner-1", 1200, 500), link="/pages/recommend/recommend", sort=1, enabled=True))
        db.add(Banner(image=demo_img("home-banner-2", 1200, 500), link="/pages/nye/nye", sort=2, enabled=True))
        db.commit()

    if db.query(GatherTab).count() == 0:
        for item in GATHER_TABS:
            db.add(GatherTab(**item, enabled=True))
        db.commit()

    if db.query(GatherRegion).count() == 0:
        for item in GATHER_REGIONS:
            db.add(GatherRegion(**item, enabled=True))
        db.commit()

    if db.query(NyeStore).count() == 0:
        for item in NYE_STORES:
            payload = dict(item)
            pkgs = default_nye_packages(payload.get("price") or 2388, payload.get("cover") or "")
            db.add(
                NyeStore(
                    **{
                        **payload,
                        "store_id": payload.get("store_id") or payload.get("id") or "",
                        "banners": dumps(payload.get("banners", [])),
                        "detail_images": dumps(payload.get("detail_images", [])),
                        "recent_buy": dumps(payload.get("recent_buy", {})),
                        "packages": dumps(pkgs),
                        "enabled": True,
                    }
                )
            )
        db.commit()
    else:
        for row in db.query(NyeStore).all():
            existing = loads(getattr(row, "packages", None) or "[]", [])
            if not existing:
                row.packages = dumps(default_nye_packages(row.price or 2388, row.cover or ""))
        db.commit()

    if db.query(GatherProduct).count() == 0:
        catalog = _nye_catalog_by_store()
        for item in GATHER_PRODUCTS:
            db.add(GatherProduct(**_build_gather_product_fields(item, catalog)))
        db.commit()
    else:
        catalog = _nye_catalog_by_store()
        for row in db.query(GatherProduct).all():
            pkgs = loads(getattr(row, "packages", None) or "[]", [])
            if pkgs:
                continue
            item = {
                "id": row.id,
                "tab": row.tab,
                "region": getattr(row, "region", "") or "",
                "detail_id": row.detail_id or "",
                "tag": row.tag or "",
                "title": row.title or "",
                "cover": row.cover or "",
                "price": row.price or 0,
                "origin_price": row.origin_price or 0,
                "sort": row.sort or 0,
            }
            filled = _build_gather_product_fields(item, catalog)
            for key in (
                "title",
                "cover",
                "price",
                "origin_price",
                "address",
                "route",
                "lat",
                "lng",
                "banners",
                "detail_images",
                "packages",
                "open_start",
                "open_end",
            ):
                cur = getattr(row, key, None)
                empty = cur is None or cur == "" or cur == "[]" or cur == 0
                if empty or key in ("packages",):
                    setattr(row, key, filled[key])
        db.commit()

    sync_gather_demo_catalog(db)
    ensure_default_activities(db)

    if not get_config(db, "activities"):
        set_config(db, "activities", DEFAULT_ACTIVITIES)
    if db.query(RecommendItem).count() == 0:
        for item in RECOMMEND_ITEMS:
            db.add(RecommendItem(**item, enabled=True))
        db.commit()

    if db.query(MallGoods).count() == 0:
        for item in MALL_GOODS:
            db.add(
                MallGoods(
                    name=item["name"],
                    title=item.get("title") or item["name"],
                    cover=item["cover"],
                    cost=item["cost"],
                    usage=MALL_USAGE,
                    valid=MALL_VALID,
                    sort=item["sort"],
                    enabled=True,
                )
            )
        db.commit()

    if db.query(Coupon).count() == 0:
        db.add(Coupon(name="红酒20元立减券", amount=20, condition="前台核销使用", expire="领取当月有效", total=999, enabled=True))
        db.commit()

    # 站点 / 视频号默认仍用包内静态路径；启动后由 asset_bootstrap 上传到 COS 并回写
    if not get_config(db, "site"):
        set_config(
            db,
            "site",
            {
                "logo": "",
                "hotline": "4001919179",
                "stewardTitle": "添加管家企业微信",
                "stewardTip": "长按二维码添加管家微信",
                "stewardQr": "",
                "groupQr": "",
                "mallRules": [
                    "兑换成功后，可在「我的-积分商城-兑换记录」中查看已兑换商品及核销码。",
                    "适用门店：天天俱乐部上海共康店、亚新生活广场、上海莘庄店、上钢新邻里3楼。",
                    "仅限到店当日消费使用，每件商品每日限兑5份，请至前台核销。",
                    "如遇缺货，可更换等值商品或退还相应积分。",
                    "仅限本人使用，不可转让、不可截图核销；如发现异常兑换，平台有权取消相关权益。",
                ],
                "roomCapacity": {"lunch": 4, "dinner": 8},
                "nyeOpenStart": "2027-02-05",
                "nyeOpenEnd": "2027-02-12",
            },
        )
    if not get_config(db, "video"):
        set_config(
            db,
            "video",
            {
                "name": "天天俱乐部",
                "avatar": "",
                "cover": "",
                "intro": "天天俱乐部！天天都有局！关注直播间，给您带来更多超高性价比的聚会餐，酒店直播！",
                "finderUserName": "",
                "defaultReservePoints": 10,
            },
        )
    else:
        video_cfg = get_config(db, "video") or {}
        if video_cfg.get("defaultReservePoints") is None:
            video_cfg["defaultReservePoints"] = 10
            set_config(db, "video", video_cfg)
    if not get_config(db, "recommend"):
        set_config(db, "recommend", {"banners": RECOMMEND_BANNERS})
    if not get_config(db, "agreements"):
        set_config(db, "agreements", AGREEMENTS)
    # 若曾被空数据覆盖，自动从内置模板恢复
    for key, default in (
        ("privacy_collect", PRIVACY_COLLECT),
        ("privacy_share", PRIVACY_SHARE),
        ("member", MEMBER_CONFIG),
        ("agreements", AGREEMENTS),
        ("hobby_options", HOBBY_OPTIONS),
        ("checkin", CHECKIN_CONFIG),
        ("loyalty", LOYALTY_CONFIG),
    ):
        cur = get_config(db, key)
        if not cur:
            set_config(db, key, default)
            continue
        if key in ("privacy_collect", "privacy_share"):
            if not (isinstance(cur, dict) and (cur.get("sections") or [])):
                set_config(db, key, default)
        elif key == "member":
            # 旧库只有 levels、或章程仍是「会员等级体系」→ 用新年卡配置覆盖（保留 monthCoupon 若已有）
            need_refresh = False
            if not isinstance(cur, dict):
                need_refresh = True
            elif cur.get("price") is None and not (cur.get("benefits") or []):
                need_refresh = True
            else:
                rules = cur.get("rules") or []
                if isinstance(rules, list) and rules:
                    blob = str(rules)
                    if (
                        "等级体系" in blob
                        or "不设等级" in blob
                        or "统一会员身份" in blob
                        or any(tag in blob for tag in ("V0", "V1", "V2", "V3"))
                        or "到店对账" in blob
                    ):
                        need_refresh = True
                if not (cur.get("benefits") or []):
                    need_refresh = True
                if not (cur.get("reminders") or []):
                    need_refresh = True
                for b in cur.get("benefits") or []:
                    if isinstance(b, dict) and str(b.get("desc") or "").strip() == "到店消费按会员折扣对账":
                        need_refresh = True
                        break
            if need_refresh:
                merged = dict(default)
                if isinstance(cur, dict) and cur.get("monthCoupon"):
                    merged["monthCoupon"] = cur["monthCoupon"]
                if isinstance(cur, dict) and cur.get("levels"):
                    merged["levels"] = cur["levels"]
                # 已有年费/权益时只刷新章程与权益说明，避免覆盖后台改价
                if isinstance(cur, dict) and cur.get("price") is not None and (cur.get("benefits") or []):
                    merged = dict(cur)
                    merged["rules"] = default.get("rules")
                    benefits = []
                    for b in cur.get("benefits") or []:
                        if not isinstance(b, dict):
                            continue
                        row = dict(b)
                        if str(row.get("desc") or "").strip() == "到店消费按会员折扣对账":
                            row["desc"] = ""
                        benefits.append(row)
                    if benefits:
                        merged["benefits"] = benefits
                    if not (merged.get("reminders") or []):
                        merged["reminders"] = default.get("reminders")
                set_config(db, key, merged)
        elif key == "agreements":
            if not (isinstance(cur, dict) and cur):
                set_config(db, key, default)
        elif key == "hobby_options":
            items = (cur.get("items") or []) if isinstance(cur, dict) else []
            if not any(isinstance(i, dict) and str(i.get("name") or "").strip() for i in items):
                set_config(db, key, default)
        elif key == "checkin":
            if not isinstance(cur, dict) or cur.get("dailyPoints") is None:
                set_config(db, key, default)
        elif key == "loyalty":
            if not isinstance(cur, dict) or cur.get("earnRateDefault") is None:
                set_config(db, key, default)

    refresh_demo_covers(db)


def enforce_production_secrets(db: Session) -> None:
    """配了微信密钥即视为正式环境：拒绝默认 JWT / 后台口令，并把已有管理员密码同步成环境变量。"""
    if not wx_configured():
        return
    settings = get_settings()
    if (settings.jwt_secret or "") == DEFAULT_JWT_SECRET:
        raise RuntimeError("正式环境必须设置 JWT_SECRET，不能使用开发默认值")
    password = settings.admin_password or ""
    if not password or password == DEFAULT_ADMIN_PASSWORD:
        raise RuntimeError("正式环境必须设置 ADMIN_PASSWORD，不能使用 admin123")
    user = db.query(AdminUser).filter(AdminUser.username == settings.admin_username).first()
    if user and not verify_password(password, user.password_hash):
        user.password_hash = hash_password(password)
        db.commit()
