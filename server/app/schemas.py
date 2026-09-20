from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class OkResponse(BaseModel):
    ok: bool = True
    message: str = "ok"
    data: Any = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class BannerIn(BaseModel):
    image: str
    link: str = ""
    sort: int = 0
    enabled: bool = True


class BannerOut(BannerIn, ORMModel):
    id: int
    created_at: Optional[datetime] = None


class StoreIn(BaseModel):
    id: str
    name: str
    cover: str = ""
    address: str = ""
    route: str = ""
    phone: str = ""
    lat: float = 0
    lng: float = 0
    sort: int = 0
    enabled: bool = True


class StoreOut(StoreIn, ORMModel):
    created_at: Optional[datetime] = None


class GatherTabIn(BaseModel):
    key: str
    name: str
    show_sold: bool = True
    sort: int = 0
    enabled: bool = True


class GatherTabOut(GatherTabIn, ORMModel):
    id: int


class GatherProductIn(BaseModel):
    id: str
    tab: str
    detail_id: str = ""
    cover: str = ""
    title: str
    tag: str = ""
    tags: list[str] = Field(default_factory=list)
    sold_text: str = ""
    price: float = 0
    origin_price: float = 0
    sort: int = 0
    enabled: bool = True


class GatherProductOut(GatherProductIn, ORMModel):
    pass


class NyeStoreIn(BaseModel):
    id: str
    name: str
    cover: str = ""
    price: float = 0
    origin_price: float = 0
    tag: str = "年夜饭"
    address: str = ""
    route: str = ""
    lat: float = 0
    lng: float = 0
    banners: list[str] = Field(default_factory=list)
    detail_images: list[str] = Field(default_factory=list)
    recent_buy: dict[str, Any] = Field(default_factory=dict)
    open_start: str = "2027-02-05"
    open_end: str = "2027-02-12"
    sort: int = 0
    enabled: bool = True


class NyeStoreOut(NyeStoreIn, ORMModel):
    pass


class MallGoodsIn(BaseModel):
    name: str
    title: str = ""
    cover: str = ""
    cost: int = 0
    usage: str = ""
    valid: str = ""
    stock: int = 999
    sort: int = 0
    enabled: bool = True


class MallGoodsOut(MallGoodsIn, ORMModel):
    id: int


class OrderStatusIn(BaseModel):
    status: str
    status_text: str = ""


class OrderOut(ORMModel):
    id: str
    user_id: int = 0
    openid: str = ""
    type: str = "nye"
    store_id: str = ""
    store_name: str = ""
    title: str = ""
    spec: str = ""
    cover: str = ""
    quantity: int = 1
    price: float = 0
    amount: float = 0
    status: str = "pending"
    status_text: str = "待支付"
    contact_name: str = ""
    contact_phone: str = ""
    people: int = 0
    remark: str = ""
    room_date: str = ""
    room_slot: str = ""
    created_at: Optional[datetime] = None


class OrderCreateIn(BaseModel):
    type: str = "nye"
    store_id: str = ""
    store_name: str = ""
    title: str = ""
    spec: str = ""
    cover: str = ""
    quantity: int = 1
    price: float = 0
    amount: float = 0
    contact_name: str = ""
    contact_phone: str = ""
    people: int = 0
    remark: str = ""
    room_date: str = ""
    room_slot: str = ""
    openid: str = ""


class RoomSlotIn(BaseModel):
    store_id: str
    date: str
    slot: str
    capacity: int = 4
    booked: int = 0


class RoomSlotOut(RoomSlotIn, ORMModel):
    id: int


class CouponIn(BaseModel):
    name: str
    amount: float = 0
    condition: str = "无门槛"
    expire: str = ""
    total: int = 0
    enabled: bool = True


class CouponOut(CouponIn, ORMModel):
    id: int
    claimed: int = 0


class AppUserOut(ORMModel):
    id: int
    openid: str
    nickname: str
    avatar: str
    phone: str
    points: int
    vip_level: str
    created_at: Optional[datetime] = None


class WxLoginIn(BaseModel):
    code: str = ""
    nickname: str = "微信用户"
    avatar: str = ""
    phone: str = ""


class ConfigIn(BaseModel):
    value: Any


class PointsAdjustIn(BaseModel):
    points: int
    title: str = "后台调整"
