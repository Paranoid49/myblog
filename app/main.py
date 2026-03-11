from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.extension_loader import load_extensions
from app.routes.api_v1_auth import router as api_v1_auth_router
from app.routes.api_v1_author import router as api_v1_author_router
from app.routes.api_v1_posts import router as api_v1_posts_router
from app.routes.api_v1_setup import router as api_v1_setup_router
from app.services.setup_service import is_initialized

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "dist"

load_extensions(settings.extension_modules)

app = FastAPI(title="myblog")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if FRONTEND_DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST_DIR / "assets"), name="frontend-assets")
app.include_router(api_v1_setup_router)
app.include_router(api_v1_auth_router)
app.include_router(api_v1_author_router)
app.include_router(api_v1_posts_router)


# 不需要初始化检查的路径
SKIP_INIT_CHECK_PATHS = {
    "/setup",
    "/health",
}


@app.middleware("http")
async def check_initialized_middleware(request: Request, call_next):
    # 跳过静态资源、setup 相关路径
    path = request.url.path
    if (
        path.startswith("/static/")
        or path.startswith("/assets/")
        or path.startswith("/api/v1/setup")
        or path in SKIP_INIT_CHECK_PATHS
    ):
        return await call_next(request)

    # 检查初始化状态
    with SessionLocal() as db:
        initialized = is_initialized(db)

    if not initialized:
        # API 请求返回 JSON 错误
        if path.startswith("/api/"):
            return JSONResponse(
                status_code=409,
                content={"code": 1001, "message": "site_not_initialized", "data": None},
            )
        # 页面请求重定向到 /setup
        return RedirectResponse(url="/setup", status_code=302)

    return await call_next(request)


@app.get("/", include_in_schema=False)
@app.get("/setup", include_in_schema=False)
@app.get("/posts/{path:path}", include_in_schema=False)
@app.get("/categories/{path:path}", include_in_schema=False)
@app.get("/tags/{path:path}", include_in_schema=False)
@app.get("/author", include_in_schema=False)
@app.get("/admin", include_in_schema=False)
@app.get("/admin/{path:path}", include_in_schema=False)
def frontend_app(path: str = ""):
    """SPA fallback - 初始化检查由中间件统一处理"""
    index_file = FRONTEND_DIST_DIR / "index.html"
    if FRONTEND_DIST_DIR.exists() and index_file.exists():
        return FileResponse(index_file)
    return {"status": "frontend_not_built"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
