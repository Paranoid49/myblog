import logging
from contextlib import contextmanager

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.engine import make_url

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.deps import require_csrf_header
from app.core.error_codes import (
    SETUP_ALREADY_INITIALIZED,
    SETUP_DATABASE_BOOTSTRAP_FAILED,
    SETUP_MIGRATION_FAILED,
    SETUP_PASSWORD_MISMATCH,
)
from app.schemas.api_response import ApiResponse, error_response, ok_response
from app.schemas.setup import SetupRequest, SetupStatusResponse
from app.services.database_bootstrap_service import (
    DatabaseBootstrapError,
    UnsupportedDatabaseBootstrapError,
    ensure_database_exists,
)
from app.services.database_state_service import database_exists
from app.services.migration_service import upgrade_database
from app.services.setup_service import SetupAlreadyInitializedError, initialize_site, is_initialized

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/setup", tags=["setup"])




# setup 阶段数据库可能尚未完成迁移，get_db 依赖的表结构可能不存在，因此使用独立的 session 管理。
@contextmanager
def _create_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _should_bootstrap_database() -> bool:
    return make_url(settings.database_url).drivername.startswith("postgresql")


@router.get("/status", response_model=ApiResponse)
def get_setup_status() -> JSONResponse:
    db_exists = database_exists()

    if not db_exists:
        return ok_response({"initialized": False, "database_exists": False})

    with _create_session() as db:
        initialized = is_initialized(db)

    return ok_response({"initialized": initialized, "database_exists": db_exists})


@router.post("")
def perform_setup(request: Request, data: SetupRequest, _csrf: None = Depends(require_csrf_header)) -> JSONResponse:
    if data.password != data.confirm_password:
        return error_response("password_mismatch", status.HTTP_400_BAD_REQUEST, SETUP_PASSWORD_MISMATCH)

    if not database_exists():
        if _should_bootstrap_database():
            try:
                ensure_database_exists(settings.database_url)
            except (DatabaseBootstrapError, UnsupportedDatabaseBootstrapError) as e:
                logger.exception("数据库自动创建失败")
                return error_response("database_bootstrap_failed", status.HTTP_500_INTERNAL_SERVER_ERROR, SETUP_DATABASE_BOOTSTRAP_FAILED)

    try:
        upgrade_database()
    except Exception as e:
        logger.exception("数据库迁移失败")
        return error_response("migration_failed", status.HTTP_500_INTERNAL_SERVER_ERROR, SETUP_MIGRATION_FAILED)

    with _create_session() as db:
        try:
            user = initialize_site(db=db, blog_title=data.blog_title, username=data.username, password=data.password)
        except SetupAlreadyInitializedError:
            return error_response("already_initialized", status.HTTP_409_CONFLICT, SETUP_ALREADY_INITIALIZED)

    request.session["user_id"] = user.id
    return ok_response({"user_id": user.id, "username": user.username})