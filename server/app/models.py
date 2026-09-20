from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def now() -> datetime:
    return datetime.utcnow()


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class SiteConfig(Base):
    __tablename__ = "site_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text, default="{}")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class Banner(Base):
    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image: Mapped[str] = mapped_column(String(512))
    link: Mapped[str] = mapped_column(String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    cover: Mapped[str] = mapped_column(String(512), default="")
    address: Mapped[str] = mapped_column(String(255), default="")
    route: Mapped[str] = mapped_column(Text, default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    lat: Mapped[float] = mapped_column(Float, default=0)
    lng: Mapped[float] = mapped_column(Float, default=0)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class GatherTab(Base):
    __tablename__ = "gather_tabs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    show_sold: Mapped[bool] = mapped_column(Boolean, default=True)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class GatherProduct(Base):
    __tablename__ = "gather_products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tab: Mapped[str] = mapped_column(String(32), index=True)
    detail_id: Mapped[str] = mapped_column(String(64), default="")
    cover: Mapped[str] = mapped_column(String(512), default="")
    title: Mapped[str] = mapped_column(String(255))
    tag: Mapped[str] = mapped_column(String(64), default="")
    tags: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    sold_text: Mapped[str] = mapped_column(String(64), default="")
    price: Mapped[float] = mapped_column(Float, default=0)
    origin_price: Mapped[float] = mapped_column(Float, default=0)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class NyeStore(Base):
    __tablename__ = "nye_stores"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    cover: Mapped[str] = mapped_column(String(512), default="")
    price: Mapped[float] = mapped_column(Float, default=0)
    origin_price: Mapped[float] = mapped_column(Float, default=0)
    tag: Mapped[str] = mapped_column(String(64), default="年夜饭")
    address: Mapped[str] = mapped_column(String(255), default="")
    route: Mapped[str] = mapped_column(Text, default="")
    lat: Mapped[float] = mapped_column(Float, default=0)
    lng: Mapped[float] = mapped_column(Float, default=0)
    banners: Mapped[str] = mapped_column(Text, default="[]")
    detail_images: Mapped[str] = mapped_column(Text, default="[]")
    recent_buy: Mapped[str] = mapped_column(Text, default="{}")
    open_start: Mapped[str] = mapped_column(String(16), default="2027-02-05")
    open_end: Mapped[str] = mapped_column(String(16), default="2027-02-12")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class MallGoods(Base):
    __tablename__ = "mall_goods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(255), default="")
    cover: Mapped[str] = mapped_column(String(512), default="")
    cost: Mapped[int] = mapped_column(Integer, default=0)
    usage: Mapped[str] = mapped_column(Text, default="")
    valid: Mapped[str] = mapped_column(String(255), default="")
    stock: Mapped[int] = mapped_column(Integer, default=999)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    openid: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    unionid: Mapped[str] = mapped_column(String(64), default="", index=True)
    session_key: Mapped[str] = mapped_column(String(128), default="")
    nickname: Mapped[str] = mapped_column(String(64), default="微信用户")
    avatar: Mapped[str] = mapped_column(String(512), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    birthday: Mapped[str] = mapped_column(String(16), default="")
    hobby: Mapped[str] = mapped_column(String(128), default="")
    phone_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    points: Mapped[int] = mapped_column(Integer, default=0)
    vip_level: Mapped[str] = mapped_column(String(16), default="V0")
    cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(64), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    region: Mapped[str] = mapped_column(String(255), default="")
    province: Mapped[str] = mapped_column(String(64), default="")
    city: Mapped[str] = mapped_column(String(64), default="")
    district: Mapped[str] = mapped_column(String(64), default="")
    detail: Mapped[str] = mapped_column(String(255), default="")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, default=0, index=True)
    openid: Mapped[str] = mapped_column(String(64), default="", index=True)
    type: Mapped[str] = mapped_column(String(32), default="nye")  # nye | room | mall
    store_id: Mapped[str] = mapped_column(String(64), default="")
    store_name: Mapped[str] = mapped_column(String(128), default="")
    title: Mapped[str] = mapped_column(String(255), default="")
    spec: Mapped[str] = mapped_column(String(255), default="")
    cover: Mapped[str] = mapped_column(String(512), default="")
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[float] = mapped_column(Float, default=0)
    amount: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    status_text: Mapped[str] = mapped_column(String(32), default="待支付")
    contact_name: Mapped[str] = mapped_column(String(64), default="")
    contact_phone: Mapped[str] = mapped_column(String(32), default="")
    people: Mapped[int] = mapped_column(Integer, default=0)
    remark: Mapped[str] = mapped_column(Text, default="")
    room_date: Mapped[str] = mapped_column(String(16), default="")
    room_slot: Mapped[str] = mapped_column(String(16), default="")
    extra: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class RoomSlot(Base):
    __tablename__ = "room_slots"
    __table_args__ = (UniqueConstraint("store_id", "date", "slot", name="uq_room_slot"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String(64), index=True)
    date: Mapped[str] = mapped_column(String(16), index=True)
    slot: Mapped[str] = mapped_column(String(16))  # lunch | dinner
    capacity: Mapped[int] = mapped_column(Integer, default=4)
    booked: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128))
    amount: Mapped[float] = mapped_column(Float, default=0)
    condition: Mapped[str] = mapped_column(String(128), default="无门槛")
    expire: Mapped[str] = mapped_column(String(64), default="")
    total: Mapped[int] = mapped_column(Integer, default=0)
    claimed: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class UserCoupon(Base):
    __tablename__ = "user_coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    coupon_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(128), default="")
    amount: Mapped[float] = mapped_column(Float, default=0)
    condition: Mapped[str] = mapped_column(String(128), default="")
    expire: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(16), default="unused")  # unused|used|expired
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class PointLedger(Base):
    __tablename__ = "point_ledgers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(128))
    value: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class CheckinRecord(Base):
    __tablename__ = "checkin_records"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_checkin_user_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    date: Mapped[str] = mapped_column(String(16), index=True)
    points: Mapped[int] = mapped_column(Integer, default=2)
    is_makeup: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class VideoLive(Base):
    __tablename__ = "video_lives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(16), default="scheduled")  # living | scheduled
    time_text: Mapped[str] = mapped_column(String(64), default="")
    line1: Mapped[str] = mapped_column(String(128), default="")
    line2: Mapped[str] = mapped_column(String(128), default="")
    points: Mapped[int] = mapped_column(Integer, default=10)
    avatar: Mapped[str] = mapped_column(String(512), default="")
    notice_id: Mapped[str] = mapped_column(String(128), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class VideoFollow(Base):
    __tablename__ = "video_follows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class VideoReserve(Base):
    __tablename__ = "video_reserves"
    __table_args__ = (UniqueConstraint("user_id", "live_id", name="uq_video_reserve"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    live_id: Mapped[int] = mapped_column(Integer, index=True)
    points: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
