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
                conn.execute(text("ALTER TABLE nye_stores ADD COLUMN packages TEXT DEFAULT '[]'"))
        if "orders" in tables:
            cols = {c["name"] for c in inspector.get_columns("orders")}
            if "extra" not in cols:
                conn.execute(text("ALTER TABLE orders ADD COLUMN extra TEXT DEFAULT '{}'"))
        # recommend_items / addresses created by create_all
