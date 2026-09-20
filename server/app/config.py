from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Gather Club API"
    database_url: str = "sqlite:///./gather.db"
    jwt_secret: str = "gather-club-dev-secret-change-me"
    jwt_expire_hours: int = 72
    admin_username: str = "admin"
    admin_password: str = "admin123"
    wx_appid: str = ""
    wx_secret: str = ""
    wx_mch_id: str = ""
    wx_mch_key: str = ""
    wx_notify_url: str = ""
    port: int = 80


@lru_cache
def get_settings() -> Settings:
    return Settings()
