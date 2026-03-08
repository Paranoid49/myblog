from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import PROJECT_ROOT
from app.core.db import SessionLocal, get_db
from app.services.database_state_service import database_exists
from app.services.post_service import get_post_by_slug, list_published_posts
from app.services.setup_service import get_site_settings, is_initialized
from app.services.taxonomy_service import get_category_by_slug, get_tag_by_slug

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory=PROJECT_ROOT / "app" / "templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    if not database_exists():
        return RedirectResponse(url="/setup", status_code=302)

    db = SessionLocal()
    try:
        if not is_initialized(db):
            return RedirectResponse(url="/setup", status_code=302)

        posts = list_published_posts(db)
        site_settings = get_site_settings(db)
        site_title = site_settings.blog_title if site_settings else None
        return templates.TemplateResponse(request, "public/index.html", {"posts": posts, "site_title": site_title})
    finally:
        db.close()


@router.get("/posts/{slug}", response_class=HTMLResponse)
def post_detail(slug: str, request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    post = get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "public/post_detail.html", {"post": post})


@router.get("/categories/{slug}", response_class=HTMLResponse)
def category_detail(slug: str, request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    category = get_category_by_slug(db, slug)
    if not category:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "public/category_detail.html", {"category": category, "posts": category.posts})


@router.get("/tags/{slug}", response_class=HTMLResponse)
def tag_detail(slug: str, request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    tag = get_tag_by_slug(db, slug)
    if not tag:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "public/tag_detail.html", {"tag": tag, "posts": tag.posts})
