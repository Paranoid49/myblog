import logging
from contextlib import asynccontextmanager
from pathlib import Path

# 版本号单一来源：优先从包元数据读取，回退到硬编码默认值
try:
    from importlib.metadata import version as get_version

    APP_VERSION = get_version("myblog")
except Exception:
    APP_VERSION = "1.0.0"

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.error_codes import REQUEST_TOO_LARGE, SITE_NOT_INITIALIZED
from app.core.exceptions import AppError
from app.core.extension_loader import load_extensions
from app.core.logging_config import setup_logging
from app.routes.api_v1_admin_posts import router as api_v1_admin_posts_router
from app.routes.api_v1_admin_taxonomy import router as api_v1_admin_taxonomy_router
from app.routes.api_v1_auth import router as api_v1_auth_router
from app.routes.api_v1_author import router as api_v1_author_router
from app.routes.api_v1_media import router as api_v1_media_router
from app.routes.api_v1_posts import router as api_v1_posts_router
from app.routes.api_v1_setup import router as api_v1_setup_router
from app.routes.api_v1_taxonomy import router as api_v1_taxonomy_router
from app.routes.feed import router as feed_router
from app.schemas.api_response import build_error_detail
from app.services.setup_service import is_initialized

setup_logging(settings.environment)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "dist"

_loaded_extensions, _failed_extensions = load_extensions(settings.extension_modules)
if _loaded_extensions:
    logger.info("已加载扩展: %s", ", ".join(_loaded_extensions))
if _failed_extensions:
    logger.warning("以下扩展加载失败: %s", ", ".join(_failed_extensions))

# 生产环境禁止使用默认密钥
if settings.environment == "production" and settings.secret_key == "change-me":
    raise RuntimeError("生产环境禁止使用默认 SECRET_KEY，请在 .env 中配置安全的随机密钥")

if settings.secret_key == "change-me":
    logger.warning("SECRET_KEY 使用默认值 'change-me'，生产环境请在 .env 中配置安全的密钥")


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """应用生命周期管理"""
    logger.info("myblog 启动完成")
    yield
    from app.core.db import engine

    engine.dispose()
    logger.info("myblog 已关闭，数据库连接已释放")


app = FastAPI(title="myblog", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=86400,
    # 生产环境仅通过 HTTPS 传输 session cookie
    https_only=settings.environment == "production",
    same_site="lax",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if FRONTEND_DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST_DIR / "assets"), name="frontend-assets")
app.include_router(api_v1_setup_router)
app.include_router(api_v1_auth_router)
app.include_router(api_v1_author_router)
app.include_router(api_v1_posts_router)
app.include_router(api_v1_admin_posts_router)
app.include_router(api_v1_taxonomy_router)
app.include_router(api_v1_admin_taxonomy_router)
app.include_router(api_v1_media_router)
app.include_router(feed_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """统一 HTTPException 响应格式"""
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_detail(str(exc.detail), exc.status_code),
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """全局业务异常处理器 — 将 AppError 转换为统一 API 响应格式"""
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_detail(exc.message, exc.code),
    )


# 不需要初始化检查的路径
SKIP_INIT_CHECK_PATHS = {
    "/setup",
    "/health",
}


# --- 中间件注册 ---
# ASGI 洋葱模型：后注册的中间件先执行请求方向处理
# 实际请求执行顺序：request_size_limit → spa_fallback → security_headers → check_initialized
@app.middleware("http")
async def check_initialized_middleware(request: Request, call_next):
    path = request.url.path
    if (
        path.startswith("/static/")
        or path.startswith("/assets/")
        or path.startswith("/api/v1/setup")
        or path in SKIP_INIT_CHECK_PATHS
    ):
        return await call_next(request)

    # 先检查内存缓存，命中则跳过数据库查询（绝大多数请求走此分支）
    from app.services.setup_service import is_cache_initialized

    if is_cache_initialized():
        return await call_next(request)

    # 缓存未命中时创建独立 Session 查询初始化状态
    # 此 Session 与路由层 get_db 的 Session 独立，但仅在首次请求时触发一次，
    # 查询完成后缓存即命中，后续请求不再进入此分支，性能影响可忽略
    with SessionLocal() as db:
        initialized = is_initialized(db)

    if not initialized:
        if path.startswith("/api/"):
            return JSONResponse(
                status_code=409,
                content=build_error_detail("site_not_initialized", SITE_NOT_INITIALIZED),
            )
        return RedirectResponse(url="/setup", status_code=302)

    return await call_next(request)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """为所有响应添加安全头"""
    response = await call_next(request)
    path = request.url.path
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if path.startswith("/api/"):
        response.headers["Content-Security-Policy"] = "default-src 'none'"
    else:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'"
        )
    # 静态资源缓存
    if path.startswith(("/static/", "/assets/")):
        response.headers["Cache-Control"] = "public, max-age=86400"
    # 生产环境启用 HSTS
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def spa_fallback_middleware(request: Request, call_next):
    """SPA 通用 fallback — 非 API/静态资源的未匹配路径返回 index.html"""
    response = await call_next(request)
    path = request.url.path
    if response.status_code == 404 and not path.startswith(("/api/", "/static/", "/assets/", "/health", "/feed.xml")):
        index_file = FRONTEND_DIST_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
    return response


@app.middleware("http")
async def request_size_limit_middleware(request: Request, call_next):
    """限制非上传接口的请求体大小（1MB），防止恶意大请求"""
    if not request.url.path.startswith("/api/v1/admin/media"):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > 1_048_576:
                    return JSONResponse(
                        status_code=413,
                        content=build_error_detail("request_too_large", REQUEST_TOO_LARGE),
                    )
            except (ValueError, TypeError):
                pass
    return await call_next(request)


@app.get("/health")
def health() -> dict:
    """健康检查，包含数据库连通性和版本信息"""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "version": APP_VERSION,
    }
