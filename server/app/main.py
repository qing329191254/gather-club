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

app = FastAPI(title=settings.app_name, docs_url="/api/docs", redoc_url="/api/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(miniapp.router)
app.include_router(admin_api.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    db = SessionLocal()
    try:
        seed_all(db)
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
