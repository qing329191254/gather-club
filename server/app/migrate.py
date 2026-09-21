"""Lightweight schema patches for existing SQLite DBs."""

from datetime import datetime

from sqlalchemy import inspect, text

from .database import engine


def ensure_schema() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        if "app_users" in tables:
            cols = {c["name"] for c in inspector.get_columns("app_users")}
            patches = {
                "birthday": "ALTER TABLE app_users ADD COLUMN birthday VARCHAR(16) DEFAULT ''",
                "hobby": "ALTER TABLE app_users ADD COLUMN hobby VARCHAR(128) DEFAULT ''",
                "phone_edited": "ALTER TABLE app_users ADD COLUMN phone_edited BOOLEAN DEFAULT 0",
                "cancelled": "ALTER TABLE app_users ADD COLUMN cancelled BOOLEAN DEFAULT 0",
                "session_key": "ALTER TABLE app_users ADD COLUMN session_key VARCHAR(128) DEFAULT ''",
                "vip_manual": "ALTER TABLE app_users ADD COLUMN vip_manual BOOLEAN DEFAULT 0",
                "profile_rewarded": "ALTER TABLE app_users ADD COLUMN profile_rewarded BOOLEAN DEFAULT 0",
            }
            for name, sql in patches.items():
                if name not in cols:
                    conn.execute(text(sql))
        if "nye_stores" in tables:
            cols = {c["name"] for c in inspector.get_columns("nye_stores")}
            if "packages" not in cols:
                # MySQL: TEXT/JSON/BLOB cannot have DEFAULT
                conn.execute(text("ALTER TABLE nye_stores ADD COLUMN packages TEXT NULL"))
                conn.execute(text("UPDATE nye_stores SET packages = '[]' WHERE packages IS NULL"))
            if "sold_count" not in cols:
                conn.execute(text("ALTER TABLE nye_stores ADD COLUMN sold_count INTEGER DEFAULT 0"))
            if "store_id" not in cols:
                conn.execute(text("ALTER TABLE nye_stores ADD COLUMN store_id VARCHAR(64) DEFAULT ''"))
                conn.execute(
                    text(
                        "UPDATE nye_stores SET store_id = id "
                        "WHERE store_id IS NULL OR store_id = ''"
                    )
                )
        if "gather_products" in tables:
            cols = {c["name"] for c in inspector.get_columns("gather_products")}
            gather_patches = {
                "sold_count": "ALTER TABLE gather_products ADD COLUMN sold_count INTEGER DEFAULT 0",
                "region": "ALTER TABLE gather_products ADD COLUMN region VARCHAR(32) DEFAULT ''",
                "address": "ALTER TABLE gather_products ADD COLUMN address VARCHAR(255) DEFAULT ''",
                "route": "ALTER TABLE gather_products ADD COLUMN route TEXT NULL",
                "lat": "ALTER TABLE gather_products ADD COLUMN lat FLOAT DEFAULT 0",
                "lng": "ALTER TABLE gather_products ADD COLUMN lng FLOAT DEFAULT 0",
                "banners": "ALTER TABLE gather_products ADD COLUMN banners TEXT NULL",
                "detail_images": "ALTER TABLE gather_products ADD COLUMN detail_images TEXT NULL",
                "recent_buy": "ALTER TABLE gather_products ADD COLUMN recent_buy TEXT NULL",
                "packages": "ALTER TABLE gather_products ADD COLUMN packages TEXT NULL",
                "open_start": "ALTER TABLE gather_products ADD COLUMN open_start VARCHAR(16) DEFAULT ''",
                "open_end": "ALTER TABLE gather_products ADD COLUMN open_end VARCHAR(16) DEFAULT ''",
            }
            added_region = "region" not in cols
            for name, sql in gather_patches.items():
                if name not in cols:
                    conn.execute(text(sql))
            # TEXT 列补空 JSON，避免旧库 NULL
            for text_col, empty in (
                ("banners", "[]"),
                ("detail_images", "[]"),
                ("recent_buy", "{}"),
                ("packages", "[]"),
                ("route", ""),
            ):
                conn.execute(
                    text(
                        f"UPDATE gather_products SET {text_col} = :empty "
                        f"WHERE {text_col} IS NULL"
                    ),
                    {"empty": empty},
                )
            if added_region:
                # 按门店/标题粗略回填，便于老数据立刻可筛
                conn.execute(
                    text(
                        """
                        UPDATE gather_products SET region = 'ningbo'
                        WHERE COALESCE(region, '') = ''
                          AND (detail_id = 'ningbo' OR title LIKE '%宁波%')
                        """
                    )
                )
                conn.execute(
                    text(
                        """
                        UPDATE gather_products SET region = 'shanghai'
                        WHERE COALESCE(region, '') = ''
                          AND (
                            detail_id IN ('xinzhuang', 'yaxin', 'gongkang', 'shibo')
                            OR title LIKE '%上海%'
                            OR title LIKE '%莘庄%'
                            OR title LIKE '%亚新%'
                            OR title LIKE '%共康%'
                            OR title LIKE '%世博%'
                          )
                        """
                    )
                )
            # 已购文案改为「手动优先」：一次性清空历史营销文案，默认走真实销量
            if "site_configs" in tables:
                marker = conn.execute(
                    text("SELECT id FROM site_configs WHERE `key` = 'sold_text_manual_v1' LIMIT 1")
                ).fetchone()
                if not marker:
                    conn.execute(text("UPDATE gather_products SET sold_text = ''"))
                    # 原始 INSERT 不走 ORM，MySQL 严格模式要求显式带上 updated_at
                    conn.execute(
                        text(
                            "INSERT INTO site_configs (`key`, value, updated_at) "
                            "VALUES ('sold_text_manual_v1', '1', :updated_at)"
                        ),
                        {"updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")},
                    )
            # 去哪聚总库：从宴会专题拷贝封面/套餐等到商品（仅空字段，一次性）
            if "site_configs" in tables and "nye_stores" in tables:
                marker = conn.execute(
                    text("SELECT id FROM site_configs WHERE `key` = 'gather_catalog_v1' LIMIT 1")
                ).fetchone()
                if not marker:
                    nye_rows = conn.execute(
                        text(
                            "SELECT id, store_id, name, cover, price, origin_price, address, route, "
                            "lat, lng, banners, detail_images, packages, open_start, open_end, sold_count "
                            "FROM nye_stores"
                        )
                    ).mappings().all()
                    nye_by_key: dict = {}
                    for n in nye_rows:
                        nye_by_key[n["id"]] = n
                        sid = (n.get("store_id") or "").strip()
                        if sid:
                            nye_by_key[sid] = n
                    products = conn.execute(
                        text(
                            "SELECT id, detail_id, tag, cover, title, price, origin_price, address, route, "
                            "lat, lng, banners, detail_images, packages, open_start, open_end, sold_count "
                            "FROM gather_products"
                        )
                    ).mappings().all()

                    def _empty(val, empty_json=None):
                        if val is None:
                            return True
                        s = str(val).strip()
                        if not s:
                            return True
                        if empty_json is not None and s == empty_json:
                            return True
                        return False

                    for g in products:
                        detail_id = (g.get("detail_id") or "").strip()
                        if not detail_id:
                            continue
                        n = nye_by_key.get(detail_id)
                        if not n:
                            continue
                        is_nye_theme = (g.get("tag") or "").strip() == "年夜饭"
                        # 非年夜饭主题不拷贝年夜饭套餐，留给默认家宴套餐
                        packages_val = g["packages"]
                        if _empty(g.get("packages"), "[]"):
                            packages_val = (n.get("packages") or "[]") if is_nye_theme else "[]"
                        conn.execute(
                            text(
                                """
                                UPDATE gather_products SET
                                  cover = :cover,
                                  title = :title,
                                  price = :price,
                                  origin_price = :origin_price,
                                  address = :address,
                                  route = :route,
                                  lat = :lat,
                                  lng = :lng,
                                  banners = :banners,
                                  detail_images = :detail_images,
                                  packages = :packages,
                                  open_start = :open_start,
                                  open_end = :open_end,
                                  sold_count = :sold_count
                                WHERE id = :id
                                """
                            ),
                            {
                                "id": g["id"],
                                "cover": g["cover"] if not _empty(g.get("cover")) else (n.get("cover") or ""),
                                "title": g["title"] if not _empty(g.get("title")) else (n.get("name") or ""),
                                "price": float(g.get("price") or 0) or float(n.get("price") or 0),
                                "origin_price": float(g.get("origin_price") or 0)
                                or float(n.get("origin_price") or 0),
                                "address": g["address"]
                                if not _empty(g.get("address"))
                                else (n.get("address") or ""),
                                "route": g["route"] if not _empty(g.get("route")) else (n.get("route") or ""),
                                "lat": float(g.get("lat") or 0) or float(n.get("lat") or 0),
                                "lng": float(g.get("lng") or 0) or float(n.get("lng") or 0),
                                "banners": g["banners"]
                                if not _empty(g.get("banners"), "[]")
                                else (n.get("banners") or "[]"),
                                "detail_images": g["detail_images"]
                                if not _empty(g.get("detail_images"), "[]")
                                else (n.get("detail_images") or "[]"),
                                "packages": packages_val,
                                "open_start": g["open_start"]
                                if not _empty(g.get("open_start"))
                                else ((n.get("open_start") or "") if is_nye_theme else ""),
                                "open_end": g["open_end"]
                                if not _empty(g.get("open_end"))
                                else ((n.get("open_end") or "") if is_nye_theme else ""),
                                "sold_count": int(g.get("sold_count") or 0)
                                or int(n.get("sold_count") or 0),
                            },
                        )
                    conn.execute(
                        text(
                            "INSERT INTO site_configs (`key`, value, updated_at) "
                            "VALUES ('gather_catalog_v1', '1', :updated_at)"
                        ),
                        {"updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")},
                    )
        if "orders" in tables:
            cols = {c["name"] for c in inspector.get_columns("orders")}
            if "extra" not in cols:
                conn.execute(text("ALTER TABLE orders ADD COLUMN extra TEXT NULL"))
                conn.execute(text("UPDATE orders SET extra = '{}' WHERE extra IS NULL"))
            # 用历史实付订单回填销量（仅当计数仍为 0，避免覆盖已有累计）
            if "gather_products" in tables:
                conn.execute(
                    text(
                        """
                        UPDATE gather_products
                        SET sold_count = COALESCE((
                            SELECT SUM(COALESCE(orders.quantity, 1))
                            FROM orders
                            WHERE orders.store_id = gather_products.id
                              AND orders.type IN ('nye', 'gather')
                              AND orders.status IN ('paid', 'completed')
                        ), 0)
                        WHERE COALESCE(sold_count, 0) = 0
                        """
                    )
                )
            if "nye_stores" in tables:
                conn.execute(
                    text(
                        """
                        UPDATE nye_stores
                        SET sold_count = COALESCE((
                            SELECT SUM(COALESCE(orders.quantity, 1))
                            FROM orders
                            WHERE orders.type = 'nye'
                              AND orders.store_id = nye_stores.id
                              AND orders.status IN ('paid', 'completed')
                        ), 0)
                        WHERE COALESCE(sold_count, 0) = 0
                        """
                    )
                )
            # 统一已支付文案为「待核销」
            conn.execute(
                text(
                    """
                    UPDATE orders SET status_text = '待核销'
                    WHERE status = 'paid' AND (status_text IS NULL OR status_text = '' OR status_text = '已支付')
                    """
                )
            )
            conn.execute(
                text(
                    """
                    UPDATE orders SET status_text = '待支付'
                    WHERE status = 'pending' AND (status_text IS NULL OR status_text = '')
                    """
                )
            )
            if "verify_code" not in cols:
                conn.execute(text("ALTER TABLE orders ADD COLUMN verify_code VARCHAR(16) DEFAULT ''"))
            conn.execute(
                text(
                    """
                    UPDATE orders SET status_text = '已取消'
                    WHERE status = 'cancelled' AND (status_text IS NULL OR status_text = '')
                    """
                )
            )
            conn.execute(
                text(
                    """
                    UPDATE orders SET status_text = '已完成'
                    WHERE status = 'completed' AND (status_text IS NULL OR status_text = '')
                    """
                )
            )
            conn.execute(
                text(
                    """
                    UPDATE orders SET status_text = '已退款'
                    WHERE status = 'refunded' AND (status_text IS NULL OR status_text = '')
                    """
                )
            )
        if "user_coupons" in tables:
            cols = {c["name"] for c in inspector.get_columns("user_coupons")}
            if "verify_code" not in cols:
                conn.execute(text("ALTER TABLE user_coupons ADD COLUMN verify_code VARCHAR(16) DEFAULT ''"))
        # 去哪聚只做专题入口：下架单点分类/无关联门店的旧商品
        if "site_configs" in tables and "gather_tabs" in tables and "gather_products" in tables:
            marker = conn.execute(
                text("SELECT id FROM site_configs WHERE `key` = 'gather_entry_only_v1' LIMIT 1")
            ).fetchone()
            if not marker:
                conn.execute(
                    text("UPDATE gather_tabs SET enabled = 0 WHERE `key` IN ('dish', 'set')")
                )
                conn.execute(
                    text("UPDATE gather_products SET enabled = 0 WHERE tab IN ('dish', 'set')")
                )
                conn.execute(
                    text(
                        "UPDATE gather_products SET enabled = 0 "
                        "WHERE detail_id IS NULL OR TRIM(detail_id) = ''"
                    )
                )
                conn.execute(
                    text(
                        "INSERT INTO site_configs (`key`, value, updated_at) "
                        "VALUES ('gather_entry_only_v1', '1', :updated_at)"
                    ),
                    {"updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")},
                )
        # recommend_items / addresses created by create_all
