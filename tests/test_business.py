"""下单、支付、库存、兑换、领券、核销的接口测试。

在仓库根目录运行：

    python tests/test_business.py

不访问微信，也不使用 server/.env 里的正式数据库。
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server"
DB_PATH = Path(tempfile.gettempdir()) / "gather-club-business-test.db"

os.environ["DATABASE_URL"] = "sqlite:///" + DB_PATH.as_posix()
os.environ["WX_APPID"] = ""
os.environ["WX_SECRET"] = ""
os.environ["WX_MCH_ID"] = ""
os.environ["WX_MCH_KEY"] = ""
os.environ["WX_NOTIFY_URL"] = ""
os.environ["JWT_SECRET"] = "gather-club-test-secret"
os.environ["ADMIN_PASSWORD"] = "admin123"

sys.path.insert(0, str(SERVER))

from fastapi.testclient import TestClient  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import AppUser, Order, UserCoupon  # noqa: E402
from app.utils import get_config, set_config, today_cn  # noqa: E402

FUTURE = "2030-06-01"


def headers(openid: str) -> dict:
    return {"X-Openid": openid}


class BusinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if DB_PATH.exists():
            DB_PATH.unlink()
        cls.client = TestClient(app)
        cls.client.__enter__()
        rec = cls.client.get("/api/v1/recommend")
        rec.raise_for_status()
        items = rec.json().get("list") or []
        if not items:
            raise RuntimeError("种子数据里没有订酒店")
        cls.hotel = items[0]

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)
        from app.database import engine

        engine.dispose()
        if DB_PATH.exists():
            DB_PATH.unlink(missing_ok=True)

    def test_unknown_type_rejects_client_price(self):
        res = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-unknown"),
            json={"type": "hack", "price": 0.01, "amount": 0.01, "title": "伪造订单"},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("订单类型无效", res.json()["detail"])

    def test_recommend_price_comes_from_catalog(self):
        hotel = self.hotel
        res = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-hotel"),
            json={
                "type": "recommend",
                "store_id": str(hotel["id"]),
                "price": 1,
                "amount": 1,
                "title": "客户端标题",
            },
        )
        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        self.assertEqual(body["amount"], hotel["price"])
        self.assertEqual(body["title"], hotel["name"])

    def test_nye_unknown_package_does_not_fall_back(self):
        res = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-nye"),
            json={
                "type": "nye",
                "store_id": "gongkang",
                "package_id": "999",
                "price": 1,
                "amount": 1,
                "spec": "名羊四海宴 (12-14人) 午市大厅",
            },
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("套餐不存在", res.json()["detail"])

    def test_nye_package_price_ignores_client_amount(self):
        res = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-nye-price"),
            json={
                "type": "nye",
                "store_id": "gongkang",
                "package_id": "1",
                "quantity": 2,
                "price": 1,
                "amount": 1,
            },
        )
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["amount"], 2388 * 2)

    def test_past_meal_date_rejected(self):
        res = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-past"),
            json={
                "type": "nye",
                "store_id": "gongkang",
                "package_id": "1",
                "room_date": "2020-01-01",
                "room_slot": "lunch",
            },
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("用餐日期已过", res.json()["detail"])

    def test_quantity_cap(self):
        res = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-qty"),
            json={
                "type": "nye",
                "store_id": "gongkang",
                "package_id": "1",
                "quantity": 21,
            },
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("数量超出范围", res.json()["detail"])

    def test_unpaid_order_expires(self):
        created = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-expire"),
            json={
                "type": "recommend",
                "store_id": str(self.hotel["id"]),
            },
        )
        self.assertEqual(created.status_code, 200, created.text)
        order_id = created.json()["id"]
        db = SessionLocal()
        try:
            row = db.query(Order).filter(Order.id == order_id).one()
            row.created_at = datetime.utcnow() - timedelta(minutes=31)
            db.commit()
        finally:
            db.close()
        listed = self.client.get("/api/v1/orders", headers=headers("openid-expire"))
        self.assertEqual(listed.status_code, 200, listed.text)
        match = next(item for item in listed.json()["list"] if item["id"] == order_id)
        self.assertEqual(match["status"], "cancelled")
        pay = self.client.post(f"/api/v1/orders/{order_id}/pay", headers=headers("openid-expire"))
        self.assertEqual(pay.status_code, 400)
        self.assertIn(pay.json()["detail"], ("订单已关闭，请重新下单", "订单状态不可支付"))

    def test_room_pay_releases_slot_when_pay_is_off(self):
        db = SessionLocal()
        try:
            loyalty = get_config(db, "loyalty", {}) or {}
            loyalty["roomPrice"] = 100
            set_config(db, "loyalty", loyalty)
        finally:
            db.close()
        created = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-room"),
            json={
                "type": "room",
                "store_id": "shibo",
                "store_name": "世博店",
                "room_date": FUTURE,
                "room_slot": "lunch",
                "quantity": 5,
                "price": 1,
                "amount": 1,
            },
        )
        self.assertEqual(created.status_code, 200, created.text)
        body = created.json()
        self.assertEqual(body["amount"], 100)
        self.assertEqual(body["quantity"], 1)
        pay = self.client.post(f"/api/v1/orders/{body['id']}/pay", headers=headers("openid-room"))
        self.assertEqual(pay.status_code, 503, pay.text)
        avail = self.client.get(
            "/api/v1/rooms/availability",
            params={"store_id": "shibo", "date": FUTURE, "slot": "lunch"},
        )
        self.assertEqual(avail.status_code, 200, avail.text)
        self.assertEqual(avail.json()["booked"], 0)

    def test_mall_redeem_is_shipping_not_verify(self):
        openid = "openid-mall"
        self.client.post(
            "/api/v1/orders",
            headers=headers(openid),
            json={"type": "recommend", "store_id": str(self.hotel["id"])},
        )
        db = SessionLocal()
        try:
            user = db.query(AppUser).filter(AppUser.openid == openid).one()
            user.points = 500
            db.commit()
            user_id = user.id
        finally:
            db.close()
        address = self.client.post(
            "/api/v1/user/addresses",
            headers=headers(openid),
            json={"name": "测试", "phone": "13800000000", "region": "上海", "detail": "测试路1号"},
        )
        self.assertEqual(address.status_code, 200, address.text)
        goods = self.client.get("/api/v1/mall/goods")
        goods.raise_for_status()
        cheap = min(goods.json()["list"], key=lambda item: item["cost"])
        redeemed = self.client.post(
            "/api/v1/mall/redeem",
            headers=headers(openid),
            json={"goodsId": cheap["id"], "addressId": address.json()["id"]},
        )
        self.assertEqual(redeemed.status_code, 200, redeemed.text)
        self.assertEqual(redeemed.json()["balance"], 500 - cheap["cost"])
        orders = self.client.get("/api/v1/orders", headers=headers(openid))
        mall = next(item for item in orders.json()["list"] if item["type"] == "mall")
        self.assertEqual(mall["statusText"], "待发货")
        self.assertEqual(mall["verifyCode"], "")
        login = self.client.post("/api/admin/login", json={"username": "admin", "password": "admin123"})
        self.assertEqual(login.status_code, 200, login.text)
        token = login.json()["access_token"]
        verified = self.client.post(
            "/api/admin/verify",
            headers={"Authorization": f"Bearer {token}"},
            json={"kind": "order", "id": mall["id"]},
        )
        self.assertEqual(verified.status_code, 400)
        self.assertIn("不能到店核销", verified.json()["detail"])
        db = SessionLocal()
        try:
            user = db.query(AppUser).filter(AppUser.id == user_id).one()
            self.assertEqual(user.points, 500 - cheap["cost"])
        finally:
            db.close()

    def test_coupon_claim_once_per_month(self):
        openid = "openid-coupon"
        first = self.client.post("/api/v1/user/coupons/claim", headers=headers(openid), json={})
        self.assertEqual(first.status_code, 200, first.text)
        self.assertTrue(first.json()["ok"])
        second = self.client.post("/api/v1/user/coupons/claim", headers=headers(openid), json={})
        self.assertEqual(second.status_code, 200, second.text)
        self.assertFalse(second.json()["ok"])
        self.assertIn("本月已领取", second.json()["message"])

    def admin_token(self) -> str:
        login = self.client.post("/api/admin/login", json={"username": "admin", "password": "admin123"})
        self.assertEqual(login.status_code, 200, login.text)
        return login.json()["access_token"]

    def test_orders_require_login_and_stay_private(self):
        anonymous = self.client.get("/api/v1/orders")
        self.assertEqual(anonymous.status_code, 401)
        created = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-owner"),
            json={"type": "recommend", "store_id": str(self.hotel["id"])},
        )
        self.assertEqual(created.status_code, 200, created.text)
        order_id = created.json()["id"]
        other = self.client.get(f"/api/v1/orders/{order_id}", headers=headers("openid-other"))
        self.assertEqual(other.status_code, 403)
        pay = self.client.post(f"/api/v1/orders/{order_id}/pay", headers=headers("openid-other"))
        self.assertEqual(pay.status_code, 403)

    def test_cancel_pending_order_only(self):
        created = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-cancel"),
            json={
                "type": "nye",
                "store_id": "gongkang",
                "package_id": "1",
                "quantity": 1,
                "price": 1,
                "amount": 1,
            },
        )
        self.assertEqual(created.status_code, 200, created.text)
        self.assertEqual(created.json()["amount"], 2388)
        order_id = created.json()["id"]
        cancelled = self.client.post(f"/api/v1/orders/{order_id}/cancel", headers=headers("openid-cancel"))
        self.assertEqual(cancelled.status_code, 200, cancelled.text)
        self.assertEqual(cancelled.json()["status"], "cancelled")
        again = self.client.post(f"/api/v1/orders/{order_id}/cancel", headers=headers("openid-cancel"))
        self.assertEqual(again.status_code, 400)

    def test_gather_standalone_order_rejected(self):
        res = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-gather-old"),
            json={"type": "gather", "store_id": "m2", "price": 1, "amount": 1},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("专题套餐", res.json()["detail"])

    def test_invalid_slot_and_missing_room_store(self):
        bad_slot = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-slot"),
            json={
                "type": "nye",
                "store_id": "gongkang",
                "package_id": "1",
                "room_date": FUTURE,
                "room_slot": "midnight",
            },
        )
        self.assertEqual(bad_slot.status_code, 400)
        self.assertIn("时段无效", bad_slot.json()["detail"])
        missing = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-slot"),
            json={"type": "room", "room_date": FUTURE, "room_slot": "lunch"},
        )
        self.assertEqual(missing.status_code, 400)

    def test_full_room_rejects_new_order(self):
        token = self.admin_token()
        saved = self.client.post(
            "/api/admin/rooms",
            headers={"Authorization": f"Bearer {token}"},
            json={"store_id": "shibo", "date": "2030-07-01", "slot": "dinner", "capacity": 1, "booked": 1},
        )
        self.assertEqual(saved.status_code, 200, saved.text)
        res = self.client.post(
            "/api/v1/orders",
            headers=headers("openid-full"),
            json={
                "type": "nye",
                "store_id": "shibo",
                "package_id": "1",
                "room_date": "2030-07-01",
                "room_slot": "dinner",
            },
        )
        self.assertEqual(res.status_code, 400, res.text)
        self.assertIn("已满", res.json()["detail"])

    def test_checkin_once_and_makeup_once(self):
        openid = "openid-checkin"
        first = self.client.post("/api/v1/checkin", headers=headers(openid))
        self.assertEqual(first.status_code, 200, first.text)
        self.assertTrue(first.json()["ok"])
        second = self.client.post("/api/v1/checkin", headers=headers(openid))
        self.assertFalse(second.json()["ok"])
        self.assertIn("今日已签到", second.json()["message"])
        makeup = self.client.post("/api/v1/checkin", headers=headers(openid), params={"makeup": True})
        self.assertTrue(makeup.json()["ok"], makeup.text)
        again = self.client.post("/api/v1/checkin", headers=headers(openid), params={"makeup": True})
        self.assertFalse(again.json()["ok"])
        self.assertIn("今日已补签", again.json()["message"])

    def test_mall_rejects_missing_address_points_and_stock(self):
        openid = "openid-mall-guard"
        goods = self.client.get("/api/v1/mall/goods").json()["list"]
        cheap = min(goods, key=lambda item: item["cost"])
        no_points = self.client.post(
            "/api/v1/mall/redeem",
            headers=headers(openid),
            json={"goodsId": cheap["id"], "addressId": 1},
        )
        self.assertEqual(no_points.status_code, 400)
        self.assertIn("积分不足", no_points.json()["detail"])
        db = SessionLocal()
        try:
            user = db.query(AppUser).filter(AppUser.openid == openid).one()
            user.points = cheap["cost"]
            expensive = max(goods, key=lambda item: item["cost"])
            from app.models import MallGoods

            row = db.query(MallGoods).filter(MallGoods.id == expensive["id"]).one()
            row.stock = 0
            db.commit()
            expensive_id = expensive["id"]
        finally:
            db.close()
        no_address = self.client.post(
            "/api/v1/mall/redeem",
            headers=headers(openid),
            json={"goodsId": cheap["id"]},
        )
        self.assertEqual(no_address.status_code, 400)
        self.assertIn("收货地址", no_address.json()["detail"])
        no_stock = self.client.post(
            "/api/v1/mall/redeem",
            headers=headers(openid),
            json={"goodsId": expensive_id, "addressId": 1},
        )
        self.assertEqual(no_stock.status_code, 400)
        self.assertIn("库存不足", no_stock.json()["detail"])

    def test_coupon_verify_once_and_expired_coupon(self):
        token = self.admin_token()
        auth = {"Authorization": f"Bearer {token}"}
        claimed = self.client.post("/api/v1/user/coupons/claim", headers=headers("openid-verify-coupon"), json={})
        self.assertTrue(claimed.json()["ok"], claimed.text)
        coupon_id = claimed.json()["data"]["id"]
        first = self.client.post("/api/admin/verify", headers=auth, json={"kind": "coupon", "id": coupon_id})
        self.assertEqual(first.status_code, 200, first.text)
        self.assertTrue(first.json()["ok"])
        second = self.client.post("/api/admin/verify", headers=auth, json={"kind": "coupon", "id": coupon_id})
        self.assertFalse(second.json()["ok"])
        other = self.client.post("/api/v1/user/coupons/claim", headers=headers("openid-expired-coupon"), json={})
        self.assertTrue(other.json()["ok"], other.text)
        expired_id = other.json()["data"]["id"]
        db = SessionLocal()
        try:
            row = db.query(UserCoupon).filter(UserCoupon.id == expired_id).one()
            row.expire = "2020-01"
            db.commit()
        finally:
            db.close()
        expired = self.client.post("/api/admin/verify", headers=auth, json={"kind": "coupon", "id": expired_id})
        self.assertEqual(expired.status_code, 200, expired.text)
        self.assertFalse(expired.json()["ok"])
        self.assertIn("过期", expired.json()["message"])
        logs = self.client.get("/api/admin/verify/logs", headers=auth, params={"date": today_cn()})
        self.assertEqual(logs.status_code, 200, logs.text)
        rows = logs.json().get("list") or []
        self.assertTrue(any(item["kind"] == "coupon" and str(item["target_id"]) == str(coupon_id) for item in rows))

    def test_admin_orders_require_login(self):
        res = self.client.get("/api/admin/orders")
        self.assertEqual(res.status_code, 401)

    def test_address_is_not_visible_to_others(self):
        created = self.client.post(
            "/api/v1/user/addresses",
            headers=headers("openid-addr-a"),
            json={"name": "甲", "phone": "13800000001", "region": "上海", "detail": "甲路"},
        )
        self.assertEqual(created.status_code, 200, created.text)
        address_id = created.json()["id"]
        self.client.delete(f"/api/v1/user/addresses/{address_id}", headers=headers("openid-addr-b"))
        own = self.client.get("/api/v1/user/addresses", headers=headers("openid-addr-a"))
        self.assertEqual(own.status_code, 200, own.text)
        self.assertTrue(any(item["id"] == address_id for item in own.json()["list"]))

    def test_video_reserve_points_only_once(self):
        db = SessionLocal()
        try:
            cfg = get_config(db, "video", {}) or {}
            cfg["defaultReservePoints"] = 10
            set_config(db, "video", cfg)
        finally:
            db.close()
        first = self.client.post(
            "/api/v1/video/reserve",
            headers=headers("openid-video"),
            json={"noticeId": "notice-once-1", "line1": "预约一次"},
        )
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(first.json()["data"]["points"], 10)
        balance = first.json()["data"]["balance"]
        second = self.client.post(
            "/api/v1/video/reserve",
            headers=headers("openid-video"),
            json={"noticeId": "notice-once-1"},
        )
        self.assertEqual(second.json()["data"]["points"], 0)
        self.assertEqual(second.json()["data"]["balance"], balance)
        home = self.client.get("/api/v1/video", headers=headers("openid-video"))
        self.assertEqual(home.status_code, 200, home.text)
        self.assertIn("notice-once-1", home.json().get("reservedNoticeIds") or [])
        self.assertEqual(home.json().get("lives") or [], [])

    def test_video_default_reserve_points_from_config(self):
        db = SessionLocal()
        try:
            cfg = get_config(db, "video", {}) or {}
            prev = cfg.get("defaultReservePoints", 10)
            cfg["defaultReservePoints"] = 25
            set_config(db, "video", cfg)
        finally:
            db.close()
        try:
            first = self.client.post(
                "/api/v1/video/reserve",
                headers=headers("openid-video-points-cfg"),
                json={"noticeId": "notice-points-25", "line1": "积分配置"},
            )
            self.assertEqual(first.status_code, 200, first.text)
            self.assertEqual(first.json()["data"]["points"], 25)
            home = self.client.get("/api/v1/video", headers=headers("openid-video-points-cfg"))
            self.assertEqual(home.status_code, 200, home.text)
            self.assertEqual(home.json()["profile"].get("defaultReservePoints"), 25)
        finally:
            db = SessionLocal()
            try:
                cfg = get_config(db, "video", {}) or {}
                cfg["defaultReservePoints"] = prev
                set_config(db, "video", cfg)
            finally:
                db.close()

    def test_video_reserve_by_notice_id(self):
        db = SessionLocal()
        try:
            cfg = get_config(db, "video", {}) or {}
            cfg["defaultReservePoints"] = 10
            set_config(db, "video", cfg)
        finally:
            db.close()
        first = self.client.post(
            "/api/v1/video/reserve",
            headers=headers("openid-video-notice"),
            json={
                "noticeId": "notice-auto-1",
                "time": "9月22 20:00",
                "line1": "测试直播",
                "line2": "自动同步",
            },
        )
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(first.json()["data"]["points"], 10)
        self.assertEqual(first.json()["data"]["noticeId"], "notice-auto-1")
        balance = first.json()["data"]["balance"]
        second = self.client.post(
            "/api/v1/video/reserve",
            headers=headers("openid-video-notice"),
            json={"noticeId": "notice-auto-1"},
        )
        self.assertEqual(second.status_code, 200, second.text)
        self.assertEqual(second.json()["data"]["points"], 0)
        self.assertEqual(second.json()["data"]["balance"], balance)

    def test_profile_reward_once_and_phone_once(self):
        db = SessionLocal()
        try:
            set_config(db, "profile_reward", {"enabled": True, "points": 20})
        finally:
            db.close()
        openid = "openid-profile"
        payload = {
            "nickname": "测试用户",
            "birthday": "1990-01-01",
            "phone": "13900000000",
            "hobby": "喝茶",
        }
        first = self.client.put("/api/v1/user/profile", headers=headers(openid), json=payload)
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(first.json()["profileRewardGranted"], 20)
        second = self.client.put("/api/v1/user/profile", headers=headers(openid), json=payload)
        self.assertEqual(second.json()["profileRewardGranted"], 0)
        changed = self.client.put(
            "/api/v1/user/profile",
            headers=headers(openid),
            json={"phone": "13900000001"},
        )
        self.assertEqual(changed.status_code, 400)
        self.assertIn("仅可修改一次", changed.json()["detail"])

    def test_cancel_account_wipes_points(self):
        openid = "openid-wipe"
        self.client.post("/api/v1/checkin", headers=headers(openid))
        db = SessionLocal()
        try:
            user = db.query(AppUser).filter(AppUser.openid == openid).one()
            user.points = 80
            db.commit()
        finally:
            db.close()
        cancelled = self.client.post("/api/v1/user/cancel", headers=headers(openid))
        self.assertEqual(cancelled.status_code, 200, cancelled.text)
        fresh = self.client.get("/api/v1/user/profile", headers=headers(openid))
        self.assertEqual(fresh.status_code, 200, fresh.text)
        self.assertNotEqual(fresh.json()["points"], 80)
        self.assertNotEqual(fresh.json()["nickname"], "已注销用户")

    def test_missing_nye_store_is_not_found(self):
        res = self.client.get("/api/v1/nye/not-a-store")
        self.assertEqual(res.status_code, 404)

    def test_gather_card_shares_nye_store_fields(self):
        gather = self.client.get("/api/v1/gather")
        self.assertEqual(gather.status_code, 200, gather.text)
        products = gather.json().get("products") or []
        card = next((p for p in products if p.get("id") == "d1"), None)
        self.assertIsNotNone(card)
        detail = self.client.get("/api/v1/nye/xinzhuang")
        self.assertEqual(detail.status_code, 200, detail.text)
        store = detail.json()
        self.assertEqual(card["title"], store["name"])
        self.assertEqual(card["cover"], store["cover"])
        self.assertEqual(card["price"], store["price"])
        packages = store.get("packages") or []
        enabled = [float(p["price"]) for p in packages if not p.get("disabled") and float(p.get("price") or 0) > 0]
        self.assertTrue(enabled)
        self.assertEqual(store["price"], min(enabled))


if __name__ == "__main__":
    unittest.main(verbosity=2)
