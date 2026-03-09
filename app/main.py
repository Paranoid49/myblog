from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.extension_loader import load_extensions
from app.routes.api_v1_auth import router as api_v1_auth_router
from app.routes.api_v1_author import router as api_v1_author_router
from app.routes.api_v1_posts import router as api_v1_posts_router
from app.routes.setup import router as setup_router

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "dist"

load_extensions(settings.extension_modules)

app = FastAPI(title="myblog")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if FRONTEND_DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST_DIR / "assets"), name="frontend-assets")
app.include_router(setup_router)
app.include_router(api_v1_auth_router)
app.include_router(api_v1_author_router)
app.include_router(api_v1_posts_router)


@app.get("/", include_in_schema=False)
@app.get("/posts/{path:path}", include_in_schema=False)
@app.get("/author", include_in_schema=False)
@app.get("/admin", include_in_schema=False)
@app.get("/admin/{path:path}", include_in_schema=False)
def frontend_app(path: str = ""):
    index_file = FRONTEND_DIST_DIR / "index.html"
    if FRONTEND_DIST_DIR.exists() and index_file.exists():
        return FileResponse(index_file)
    return {"status": "frontend_not_built"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
