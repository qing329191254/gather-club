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
