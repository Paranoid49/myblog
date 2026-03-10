from contextlib import contextmanager

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.engine import make_url

from app.core.config import settings
from app.core.db import SessionLocal
from app.services.database_bootstrap_service import (
    DatabaseBootstrapError,
    UnsupportedDatabaseBootstrapError,
    ensure_database_exists,
)
from app.services.database_state_service import database_exists
from app.services.migration_service import upgrade_database
from app.services.setup_service import SetupAlreadyInitializedError, initialize_site, is_initialized

router = APIRouter(prefix="/api/v1/setup", tags=["setup"])


class SetupStatusResponse(BaseModel):
    initialized: bool
    database_exists: bool


class SetupRequest(BaseModel):
    blog_title: str
    username: str
    password: str
    confirm_password: str

    @field_validator("blog_title", "username", "password")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value


def _ok(data: dict | None = None, message: str = "ok") -> JSONResponse:
    return JSONResponse(status_code=200, content={"code": 0, "message": message, "data": data})


def _error(message: str, status_code: int, code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": None})


@contextmanager
def _create_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _should_bootstrap_database() -> bool:
    return make_url(settings.database_url).drivername.startswith("postgresql")


@router.get("/status")
def get_setup_status() -> JSONResponse:
    db_exists = database_exists()

    if not db_exists:
        return _ok({"initialized": False, "database_exists": False})

    with _create_session() as db:
        initialized = is_initialized(db)

    return _ok({"initialized": initialized, "database_exists": db_exists})


@router.post("")
def perform_setup(request: Request, data: SetupRequest) -> JSONResponse:
    if data.password != data.confirm_password:
        return _error("password_mismatch", 400, 2001)

    if not database_exists():
        if _should_bootstrap_database():
            try:
                ensure_database_exists(settings.database_url)
            except (DatabaseBootstrapError, UnsupportedDatabaseBootstrapError) as e:
                return _error(f"database_bootstrap_failed: {e}", 500, 2002)

    try:
        upgrade_database()
    except Exception as e:
        return _error(f"migration_failed: {e}", 500, 2003)

    with _create_session() as db:
        try:
            user = initialize_site(db=db, blog_title=data.blog_title, username=data.username, password=data.password)
        except SetupAlreadyInitializedError:
            return _error("already_initialized", 409, 2004)

    request.session["user_id"] = user.id
    return _ok({"user_id": user.id, "username": user.username})