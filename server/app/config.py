from functools import lru_cache

from pydantic import field_validator
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
    # 微信云托管对象存储
    wx_cloud_env: str = "prod-d7gemg7fe0004adc9"
    cos_bucket: str = "7072-prod-d7gemg7fe0004adc9-1492244999"
    cos_region: str = "ap-shanghai"
    cos_cdn_domain: str = "https://7072-prod-d7gemg7fe0004adc9-1492244999.tcb.qcloud.la"
    port: int = 80

    @field_validator(
        "wx_appid",
        "wx_secret",
        "wx_mch_id",
        "wx_mch_key",
        "wx_notify_url",
        "wx_cloud_env",
        "cos_bucket",
        "cos_region",
        "cos_cdn_domain",
        mode="before",
    )
    @classmethod
    def strip_str(cls, v):
        if v is None:
            return ""
        s = str(v).strip()
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            s = s[1:-1].strip()
        return s


@lru_cache
def get_settings() -> Settings:
    return Settings()
