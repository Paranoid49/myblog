from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.routes.admin_auth import router as admin_auth_router
from app.routes.admin_posts import router as admin_posts_router
from app.routes.admin_taxonomy import router as admin_taxonomy_router
from app.routes.api_v1_auth import router as api_v1_auth_router
from app.routes.api_v1_posts import router as api_v1_posts_router
from app.routes.public import router as public_router
from app.routes.setup import router as setup_router

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="myblog")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(setup_router)
app.include_router(admin_auth_router)
app.include_router(admin_posts_router)
app.include_router(admin_taxonomy_router)
app.include_router(api_v1_auth_router)
app.include_router(api_v1_posts_router)
app.include_router(public_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
