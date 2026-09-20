"""初始化管理员账号与小程序演示数据。"""

from __future__ import annotations

from sqlalchemy.orm import Session

from .config import get_settings
from .deps import hash_password
from .cms_data import (
    AGREEMENTS,
    MEMBER_CONFIG,
    PRIVACY_COLLECT,
    PRIVACY_SHARE,
    RECOMMEND_BANNERS,
    RECOMMEND_ITEMS,
    default_nye_packages,
)
from .models import (
    AdminUser,
    Banner,
    Coupon,
    GatherProduct,
    GatherTab,
    MallGoods,
    NyeStore,
    RecommendItem,
    Store,
    VideoLive,
)
from .utils import dumps, get_config, loads, set_config

settings = get_settings()

STORES = [
    {
        "id": "shibo",
        "name": "天天俱乐部上海世博店",
        "cover": "/static/stores/shibo.png",
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
        "cover": "/static/stores/xinzhuang.png",
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
        "cover": "/static/stores/yaxin.png",
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
        "cover": "/static/stores/gongkang.png",
        "address": "上海市宝山区共和新路5000弄绿地新都会1号楼二楼",
        "route": "地铁1号线共康路站下4号口出往北直行过共康路约200米，甬粤江南隔壁大门进2楼",
        "phone": "4001919179",
        "lat": 31.3208,
        "lng": 121.4476,
        "sort": 4,
    },
    {
        "id": "ningbo",
        "name": "宁波天天俱乐部天一店",
        "cover": "/static/stores/ningbo.png",
        "address": "浙江省宁波市海曙区中山路220号第二百货商店7楼",
        "route": "地铁1号线东门口站A出口，公交药行街、东门口、灵桥西下",
        "phone": "4001919179",
        "lat": 29.8684,
        "lng": 121.5502,
        "sort": 5,
    },
]

GATHER_TABS = [
    {"key": "day", "name": "聚一天", "show_sold": True, "sort": 1},
    {"key": "meal", "name": "聚个餐", "show_sold": True, "sort": 2},
    {"key": "dish", "name": "招牌菜", "show_sold": False, "sort": 3},
    {"key": "set", "name": "精品套餐", "show_sold": False, "sort": 4},
]

GATHER_PRODUCTS = [
    {"id": "d1", "tab": "day", "detail_id": "xinzhuang", "cover": "/static/banners/nye.png", "title": "上海莘庄店-天天俱乐部-2027年夜饭", "tag": "年夜饭", "sold_text": "1人已购", "price": 2688, "origin_price": 3688, "sort": 1},
    {"id": "d2", "tab": "day", "detail_id": "xinzhuang", "cover": "/static/stores/xinzhuang.png", "title": "天天俱乐部-上海莘庄店（环球主题馆）", "sold_text": "1万+人已购", "price": 899, "origin_price": 1988, "sort": 2},
    {"id": "d3", "tab": "day", "detail_id": "yaxin", "cover": "/static/banners/nye.png", "title": "上海亚新店-天天俱乐部-2027年夜饭", "tag": "年夜饭", "sold_text": "1人已购", "price": 2688, "origin_price": 3488, "sort": 3},
    {"id": "d4", "tab": "day", "detail_id": "yaxin", "cover": "/static/stores/yaxin.png", "title": "天天俱乐部上海亚新店（时光主题馆）", "tags": ["地铁直", "沉浸体验", "全包房"], "sold_text": "1万+人已购", "price": 899, "origin_price": 1988, "sort": 4},
    {"id": "d5", "tab": "day", "detail_id": "gongkang", "cover": "/static/banners/nye.png", "title": "上海共康店-天天俱乐部-2027年夜饭", "tag": "年夜饭", "sold_text": "1人已购", "price": 2388, "origin_price": 3488, "sort": 5},
    {"id": "d6", "tab": "day", "detail_id": "gongkang", "cover": "/static/stores/gongkang.png", "title": "天天俱乐部上海共康店（老上海情怀型）", "tags": ["直营", "近地铁", "怀旧风"], "sold_text": "2万+人已购", "price": 799, "origin_price": 999, "sort": 6},
    {"id": "d7", "tab": "day", "cover": "/static/stores/ningbo.png", "title": "宁波天天俱乐部（天一店）", "tags": ["核心商圈", "地铁直达"], "sold_text": "4000+人已购", "price": 828, "origin_price": 1688, "sort": 7},
    {"id": "m1", "tab": "meal", "detail_id": "xinzhuang", "cover": "/static/nye/xinzhuang.jpg", "title": "莘庄店·帝王蟹海鲜盛宴（10人）", "tag": "海鲜", "sold_text": "328人已购", "price": 1888, "origin_price": 2588, "sort": 1},
    {"id": "m2", "tab": "meal", "detail_id": "yaxin", "cover": "/static/nye/yaxin.jpg", "title": "亚新店·羊蝎子火锅双人餐", "tags": ["招牌", "双人餐"], "sold_text": "1.2万+人已购", "price": 198, "origin_price": 298, "sort": 2},
    {"id": "m3", "tab": "meal", "detail_id": "gongkang", "cover": "/static/nye/gongkang.jpg", "title": "共康店·老上海本帮菜家宴", "tag": "本帮菜", "sold_text": "860人已购", "price": 688, "origin_price": 988, "sort": 3},
    {"id": "m4", "tab": "meal", "detail_id": "shibo", "cover": "/static/nye/shibo.jpg", "title": "世博店·午市自助畅吃", "tags": ["自助", "午市"], "sold_text": "5200+人已购", "price": 168, "origin_price": 228, "sort": 4},
    {"id": "c1", "tab": "dish", "detail_id": "xinzhuang", "cover": "/static/nye/detail/banner1.jpg", "title": "招牌手撕盐焗鸡（整只）", "tag": "招牌", "price": 128, "origin_price": 168, "sort": 1},
    {"id": "c2", "tab": "dish", "detail_id": "yaxin", "cover": "/static/nye/detail/banner2.jpg", "title": "黄油香煎小牛排", "tags": ["人气", "西式"], "price": 88, "origin_price": 118, "sort": 2},
    {"id": "c3", "tab": "dish", "detail_id": "gongkang", "cover": "/static/nye/detail/banner3.jpg", "title": "红烧肉配糯米饭", "tag": "本帮", "price": 68, "origin_price": 88, "sort": 3},
    {"id": "c4", "tab": "dish", "detail_id": "shibo", "cover": "/static/nye/detail/content1.jpg", "title": "蒜蓉粉丝蒸扇贝（6只）", "tags": ["海鲜", "热销"], "price": 98, "origin_price": 128, "sort": 4},
    {"id": "s1", "tab": "set", "detail_id": "xinzhuang", "cover": "/static/nye/xinzhuang.jpg", "title": "喜气羊羊宴（10-12人）", "tag": "套餐", "price": 2688, "origin_price": 3288, "sort": 1},
    {"id": "s2", "tab": "set", "detail_id": "yaxin", "cover": "/static/nye/yaxin.jpg", "title": "团圆家宴（8-10人）", "tags": ["包厢", "晚市"], "price": 1988, "origin_price": 2588, "sort": 2},
    {"id": "s3", "tab": "set", "detail_id": "gongkang", "cover": "/static/nye/gongkang.jpg", "title": "名羊四海宴（12-14人）", "tag": "套餐", "price": 3588, "origin_price": 4288, "sort": 3},
    {"id": "s4", "tab": "set", "detail_id": "shibo", "cover": "/static/nye/shibo.jpg", "title": "商务午宴精选套餐（6人）", "tags": ["午市", "商务"], "price": 1288, "origin_price": 1688, "sort": 4},
]

NYE_STORES = [
    {
        "id": "gongkang",
        "name": "上海共康店-天天俱乐部-2027年夜饭",
        "cover": "/static/nye/gongkang.jpg",
        "price": 2388,
        "tag": "年夜饭",
        "address": "共和新路5000弄绿地新都会1号楼二楼",
        "route": "地铁1号线共康路站下4号口出往北直行过共康路约200米，甬粤江南隔壁大门进2楼",
        "lat": 31.3208,
        "lng": 121.4476,
        "banners": ["/static/nye/detail/banner1.jpg", "/static/nye/detail/banner2.jpg", "/static/nye/detail/banner3.jpg"],
        "detail_images": ["/static/nye/detail/content1.jpg", "/static/nye/detail/content2.jpg", "/static/nye/detail/content3.jpg"],
        "recent_buy": {"countText": "近一周1人买过", "avatar": "/static/icons/avatar-default.png", "name": "阿********)", "timeText": "22小时前买了1件"},
        "sort": 1,
    },
    {
        "id": "shibo",
        "name": "上海世博店-天天俱乐部-2027年夜饭",
        "cover": "/static/nye/shibo.jpg",
        "price": 2688,
        "tag": "年夜饭",
        "address": "浦东新区长清路92号中邻上钢里3楼",
        "route": "地铁长清路站7号线2号出口，13号线7号出口，步行进入中邻上钢里商场内3楼",
        "lat": 31.1846,
        "lng": 121.4852,
        "banners": ["/static/nye/detail/banner2.jpg", "/static/nye/detail/banner1.jpg", "/static/nye/detail/banner3.jpg"],
        "detail_images": ["/static/nye/detail/content1.jpg", "/static/nye/detail/content2.jpg", "/static/nye/detail/content3.jpg"],
        "recent_buy": {"countText": "近一周3人买过", "avatar": "/static/icons/avatar-default.png", "name": "小********)", "timeText": "5小时前买了1件"},
        "sort": 2,
    },
    {
        "id": "yaxin",
        "name": "上海亚新店-天天俱乐部-2027年夜饭",
        "cover": "/static/nye/yaxin.jpg",
        "price": 2688,
        "origin_price": 3488,
        "tag": "年夜饭",
        "address": "普陀区长寿路401号3号楼2楼",
        "route": "地铁7、13号线长寿路站7号口出来左转步行50米进入亚新广场内",
        "lat": 31.2432,
        "lng": 121.4374,
        "banners": ["/static/nye/detail/banner3.jpg", "/static/nye/detail/banner1.jpg", "/static/nye/detail/banner2.jpg"],
        "detail_images": ["/static/nye/detail/content1.jpg", "/static/nye/detail/content2.jpg", "/static/nye/detail/content3.jpg"],
        "recent_buy": {"countText": "近一周2人买过", "avatar": "/static/icons/avatar-default.png", "name": "李********)", "timeText": "1天前买了1件"},
        "sort": 3,
    },
    {
        "id": "xinzhuang",
        "name": "上海莘庄店-天天俱乐部-2027年夜饭",
        "cover": "/static/nye/xinzhuang.jpg",
        "price": 2688,
        "origin_price": 3688,
        "tag": "年夜饭",
        "address": "闵行区都市路5001号5楼",
        "route": "地铁1/5号线莘庄站南1口出，步行约600米至莘庄仲盛世界商城5楼",
        "lat": 31.1134,
        "lng": 121.3851,
        "banners": ["/static/nye/detail/banner1.jpg", "/static/nye/detail/banner3.jpg", "/static/nye/detail/banner2.jpg"],
        "detail_images": ["/static/nye/detail/content1.jpg", "/static/nye/detail/content2.jpg", "/static/nye/detail/content3.jpg"],
        "recent_buy": {"countText": "近一周5人买过", "avatar": "/static/icons/avatar-default.png", "name": "王********)", "timeText": "3小时前买了2件"},
        "sort": 4,
    },
]

MALL_USAGE = "适用于天天俱乐部上海共康店、亚新生活广场、上海莘庄店、上钢新邻里3楼，凭兑换码到店使用。"
MALL_VALID = "领取后立即生效，有效期30天。"

MALL_GOODS = [
    {"name": "鱼缸投币挑战 (3次)", "title": "鱼缸投币挑战 (3枚祈福币)", "cover": "/static/mall/tank.png", "cost": 300, "sort": 1},
    {"name": "百事可乐一瓶1.25L", "cover": "/static/mall/pepsi.png", "cost": 500, "sort": 2},
    {"name": "雪碧一瓶1.25L", "cover": "/static/mall/sprite.png", "cost": 500, "sort": 3},
    {"name": "美汁源果粒橙一瓶1.25L", "cover": "/static/mall/minute.png", "cost": 500, "sort": 4},
    {"name": "光明啤酒", "cover": "/static/mall/beer.png", "cost": 800, "sort": 5},
    {"name": "鱼林扑克", "cover": "/static/mall/poker.png", "cost": 200, "sort": 6},
    {"name": "葱烤海参烩鱼肚1份", "cover": "/static/mall/haishen.png", "cost": 2500, "sort": 7},
    {"name": "壹聚黄酒（8年纯酿）", "cover": "/static/mall/wine.png", "cost": 3000, "sort": 8},
    {"name": "麻将桌券1份", "cover": "/static/mall/mahjong.png", "cost": 3000, "sort": 9},
    {"name": "鲍鱼炒年糕1份", "cover": "/static/mall/abalone.png", "cost": 2500, "sort": 10},
    {"name": "蜂蜜小烤肉1份", "cover": "/static/mall/meat.png", "cost": 2000, "sort": 11},
]


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
        db.add(Banner(image="/static/banners/hotel.png", link="/pages/recommend/recommend", sort=1, enabled=True))
        db.add(Banner(image="/static/banners/nye.png", link="/pages/nye/nye", sort=2, enabled=True))
        db.commit()

    if db.query(GatherTab).count() == 0:
        for item in GATHER_TABS:
            db.add(GatherTab(**item, enabled=True))
        db.commit()

    if db.query(GatherProduct).count() == 0:
        from .utils import dumps

        for item in GATHER_PRODUCTS:
            payload = dict(item)
            tags = payload.pop("tags", [])
            db.add(GatherProduct(**payload, tags=dumps(tags), enabled=True))
        db.commit()

    if db.query(NyeStore).count() == 0:
        for item in NYE_STORES:
            payload = dict(item)
            pkgs = default_nye_packages(payload.get("price") or 2388, payload.get("cover") or "")
            db.add(
                NyeStore(
                    **{
                        **payload,
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
        # 已有门店补齐 packages
        for row in db.query(NyeStore).all():
            existing = loads(getattr(row, "packages", None) or "[]", [])
            if not existing:
                row.packages = dumps(default_nye_packages(row.price or 2388, row.cover or ""))
        db.commit()

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

    if db.query(VideoLive).count() == 0:
        db.add(VideoLive(status="living", line1="新锦江4+6+10人", line2="中餐", points=10, sort=0, enabled=True))
        lives = [
            ("09月20 11:30", "天鹅宾馆下午茶/", "中餐"),
            ("09月20 16:00", "外高桥喜来登中餐+", "自助下午茶"),
            ("09月21 11:30", "海伦宾馆4/6/8人", "中餐"),
            ("09月21 16:00", "虹桥宾馆", "大闸蟹自助"),
            ("09月22 11:30", "静安洲际大闸蟹晚市自助", "（新品）"),
        ]
        for i, (time_text, line1, line2) in enumerate(lives, start=1):
            db.add(
                VideoLive(
                    status="scheduled",
                    time_text=time_text,
                    line1=line1,
                    line2=line2,
                    points=10,
                    sort=i,
                    enabled=True,
                )
            )
        db.commit()

    if not get_config(db, "site"):
        set_config(
            db,
            "site",
            {
                "hotline": "4001919179",
                "stewardTitle": "添加管家企业微信",
                "stewardTip": "长按二维码添加管家微信",
                "stewardQr": "/static/common/steward-qr.png",
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
                "avatar": "/static/icons/brand.png",
                "cover": "/static/banners/video-cover.png",
                "intro": "天天俱乐部！天天都有局！关注直播间，给您带来更多超高性价比的聚会餐，酒店直播！",
                "finderUserName": "",
            },
        )
    if not get_config(db, "recommend"):
        set_config(db, "recommend", {"banners": RECOMMEND_BANNERS})
    if not get_config(db, "agreements"):
        set_config(db, "agreements", AGREEMENTS)
    if not get_config(db, "privacy_collect"):
        set_config(db, "privacy_collect", PRIVACY_COLLECT)
    if not get_config(db, "privacy_share"):
        set_config(db, "privacy_share", PRIVACY_SHARE)
    if not get_config(db, "member"):
        set_config(db, "member", MEMBER_CONFIG)
