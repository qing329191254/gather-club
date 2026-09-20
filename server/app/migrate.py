"""Lightweight schema patches for existing SQLite DBs."""

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
        if "gather_products" in tables:
            cols = {c["name"] for c in inspector.get_columns("gather_products")}
            if "sold_count" not in cols:
                conn.execute(text("ALTER TABLE gather_products ADD COLUMN sold_count INTEGER DEFAULT 0"))
            if "region" not in cols:
                conn.execute(text("ALTER TABLE gather_products ADD COLUMN region VARCHAR(32) DEFAULT ''"))
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
                    conn.execute(
                        text(
                            "INSERT INTO site_configs (`key`, value) VALUES ('sold_text_manual_v1', '{\"ok\":true}')"
                        )
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
                            WHERE orders.type = 'gather'
                              AND orders.store_id = gather_products.id
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
        # recommend_items / addresses created by create_all
