from contextlib import contextmanager

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
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

router = APIRouter(tags=["setup"])
templates = Jinja2Templates(directory="app/templates")


@contextmanager
def create_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def should_bootstrap_database() -> bool:
    return make_url(settings.database_url).drivername.startswith("postgresql")


@router.get("/setup", response_class=HTMLResponse)
def setup_page(request: Request):
    if not database_exists():
        return templates.TemplateResponse(request, "setup/setup.html", {"error": None})

    with create_session() as db:
        if is_initialized(db):
            return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(request, "setup/setup.html", {"error": None})


@router.post("/setup")
def setup_submit(
    request: Request,
    blog_title: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    if password != confirm_password:
        return templates.TemplateResponse(
            request,
            "setup/setup.html",
            {"error": "两次密码不一致"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        if should_bootstrap_database():
            ensure_database_exists(settings.database_url)
        with create_session() as db:
            if is_initialized(db):
                return RedirectResponse(url="/", status_code=302)
        upgrade_database()
        with create_session() as db:
            user = initialize_site(db=db, blog_title=blog_title, username=username, password=password)
    except SetupAlreadyInitializedError:
        return RedirectResponse(url="/", status_code=302)
    except (DatabaseBootstrapError, UnsupportedDatabaseBootstrapError):
        return templates.TemplateResponse(
            request,
            "setup/setup.html",
            {"error": "初始化失败，请检查数据库配置后重试"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/admin/posts", status_code=302)
