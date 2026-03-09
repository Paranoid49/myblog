from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import PROJECT_ROOT
from app.core.db import get_db
from app.models import Category, Tag
from app.services.post_service import slugify
from app.services.setup_service import is_initialized

router = APIRouter(prefix="/admin", tags=["admin-taxonomy"])
templates = Jinja2Templates(directory=PROJECT_ROOT / "app" / "templates")


def _require_initialized(db: Session) -> RedirectResponse | None:
    if not is_initialized(db):
        return RedirectResponse(url="/setup", status_code=302)
    return None


def _require_login(request: Request) -> RedirectResponse | None:
    if not request.session.get("user_id"):
        return RedirectResponse(url="/admin/login", status_code=302)
    return None


def _build_taxonomy_context(db: Session, error: str | None = None) -> dict:
    categories = list(db.execute(select(Category).order_by(Category.name.asc())).scalars().all())
    tags = list(db.execute(select(Tag).order_by(Tag.name.asc())).scalars().all())
    return {
        "categories": categories,
        "tags": tags,
        "error": error,
    }


@router.get("/taxonomy", response_class=HTMLResponse)
def taxonomy_page(request: Request, db: Session = Depends(get_db)):
    init_redirect = _require_initialized(db)
    if init_redirect:
        return init_redirect

    redirect = _require_login(request)
    if redirect:
        return redirect

    return templates.TemplateResponse(request, "admin/taxonomy.html", _build_taxonomy_context(db))


@router.post("/categories")
def create_category(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    init_redirect = _require_initialized(db)
    if init_redirect:
        return init_redirect

    redirect = _require_login(request)
    if redirect:
        return redirect

    normalized_name = name.strip()
    if not normalized_name:
        return templates.TemplateResponse(
            request,
            "admin/taxonomy.html",
            _build_taxonomy_context(db, error="分类名称不能为空"),
            status_code=400,
        )

    category_slug = slugify(normalized_name)
    exists = db.execute(select(Category.id).where(Category.slug == category_slug)).first() is not None
    if exists:
        return templates.TemplateResponse(
            request,
            "admin/taxonomy.html",
            _build_taxonomy_context(db, error="分类已存在"),
            status_code=400,
        )

    db.add(Category(name=normalized_name, slug=category_slug))
    db.commit()
    return RedirectResponse(url="/admin/taxonomy", status_code=302)


@router.post("/tags")
def create_tag(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    init_redirect = _require_initialized(db)
    if init_redirect:
        return init_redirect

    redirect = _require_login(request)
    if redirect:
        return redirect

    normalized_name = name.strip()
    if not normalized_name:
        return templates.TemplateResponse(
            request,
            "admin/taxonomy.html",
            _build_taxonomy_context(db, error="标签名称不能为空"),
            status_code=400,
        )

    tag_slug = slugify(normalized_name)
    exists = db.execute(select(Tag.id).where(Tag.slug == tag_slug)).first() is not None
    if exists:
        return templates.TemplateResponse(
            request,
            "admin/taxonomy.html",
            _build_taxonomy_context(db, error="标签已存在"),
            status_code=400,
        )

    db.add(Tag(name=normalized_name, slug=tag_slug))
    db.commit()
    return RedirectResponse(url="/admin/taxonomy", status_code=302)
