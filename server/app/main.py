import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import Base, SessionLocal, engine
from .migrate import ensure_schema
from .routers import admin_api, miniapp
from .seed import seed_all

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent.parent
ADMIN_DIST = BASE_DIR / "static" / "admin"
# 小程序本地静态资源（icons/banners 等），后台预览 /static/... 时复用
MINIAPP_STATIC = BASE_DIR.parent / "miniapp" / "static"
SERVER_STATIC = BASE_DIR / "static"

app = FastAPI(
    title=settings.app_name,
    docs_url=None if settings.wx_appid else "/api/docs",
    redoc_url=None if settings.wx_appid else "/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(miniapp.router)
app.include_router(admin_api.router)

# 云托管只部署 server/，品牌/会员/视频号图已拷入 static/；优先挂载这里
if SERVER_STATIC.exists():
    app.mount("/static", StaticFiles(directory=str(SERVER_STATIC)), name="server-static")
elif MINIAPP_STATIC.exists():
    app.mount("/static", StaticFiles(directory=str(MINIAPP_STATIC)), name="miniapp-static")


@app.on_event("startup")
async def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    db = SessionLocal()
    try:
        seed_all(db)
        try:
            import logging

            from .asset_bootstrap import bootstrap_brand_assets

            result = await bootstrap_brand_assets(db, force=False)
            logging.getLogger(__name__).info("brand asset bootstrap: %s", result)
        except Exception:  # noqa: BLE001
            import logging

            logging.getLogger(__name__).exception("brand asset bootstrap skipped")
    finally:
        db.close()


@app.get("/api/health")
def api_health():
    return {"ok": True}


if ADMIN_DIST.exists():
    assets_dir = ADMIN_DIST / "assets"
    if assets_dir.exists():
        app.mount("/admin/assets", StaticFiles(directory=str(assets_dir)), name="admin-assets")

    @app.get("/admin")
    @app.get("/admin/")
    @app.get("/admin/{full_path:path}")
    def admin_spa(full_path: str = ""):
        # API 路径不会进这里；其余走 SPA
        candidate = ADMIN_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        index = ADMIN_DIST / "index.html"
        if index.exists():
            return FileResponse(index)
        return {"message": "Admin 未构建，请在 admin 目录执行 npm run build"}


def create_app() -> FastAPI:
    return app
