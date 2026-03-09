from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import PROJECT_ROOT
from app.core.db import get_db
from app.models import Category, Post, Tag
from app.schemas.post import PostCreate
from app.services.post_service import build_post, publish_post, unpublish_post, update_post
from app.services.setup_service import is_initialized

router = APIRouter(prefix="/admin/posts", tags=["admin-posts"])
templates = Jinja2Templates(directory=PROJECT_ROOT / "app" / "templates")


def _require_initialized(db: Session) -> RedirectResponse | None:
    if not is_initialized(db):
        return RedirectResponse(url="/setup", status_code=302)
    return None


def _require_login(request: Request) -> RedirectResponse | None:
    if not request.session.get("user_id"):
        return RedirectResponse(url="/admin/login", status_code=302)
    return None


def _resolve_category_id(db: Session, category_id: str | None) -> int:
    if category_id not in (None, ""):
        try:
            return int(category_id)
        except ValueError:
            pass

    default_category = db.execute(select(Category).where(Category.slug == "default")).scalar_one_or_none()
    if default_category is None:
        default_category = db.execute(select(Category).where(Category.name == "默认分类")).scalar_one_or_none()

    if default_category is None:
        default_category = Category(name="默认分类", slug="default")
        db.add(default_category)
        db.flush()

    return default_category.id



def _load_form_options(db: Session) -> tuple[list[Category], list[Tag]]:
    categories = list(db.execute(select(Category).order_by(Category.name.asc())).scalars().all())
    tags = list(db.execute(select(Tag).order_by(Tag.name.asc())).scalars().all())
    return categories, tags


@router.get("", response_class=HTMLResponse)
def post_list(request: Request, db: Session = Depends(get_db)):
    init_redirect = _require_initialized(db)
    if init_redirect:
        return init_redirect

    redirect = _require_login(request)
    if redirect:
        return redirect

    stmt = select(Post).options(selectinload(Post.category)).order_by(Post.created_at.desc())
    posts = list(db.execute(stmt).scalars().all())
    return templates.TemplateResponse(request, "admin/post_list.html", {"posts": posts})


@router.get("/new", response_class=HTMLResponse)
def new_post_page(request: Request, db: Session = Depends(get_db)):
    init_redirect = _require_initialized(db)
    if init_redirect:
        return init_redirect

    redirect = _require_login(request)
    if redirect:
        return redirect

    categories, tags = _load_form_options(db)
    return templates.TemplateResponse(
        request,
        "admin/post_form.html",
        {
            "page_title": "新建文章",
            "form_action": "/admin/posts/new",
            "submit_label": "保存",
            "post": None,
            "selected_tag_ids": [],
            "categories": categories,
            "tags": tags,
            "error": None,
        },
    )


@router.post("/new")
def create_post(
    request: Request,
    title: str = Form(...),
    summary: str = Form(""),
    content: str = Form(...),
    category_id: str | None = Form(default=None),
    tag_ids: list[int] = Form(default=[]),
    db: Session = Depends(get_db),
):
    init_redirect = _require_initialized(db)
    if init_redirect:
        return init_redirect

    redirect = _require_login(request)
    if redirect:
        return redirect

    resolved_category_id = _resolve_category_id(db, category_id)

    existing_slugs = set(db.execute(select(Post.slug)).scalars().all())
    post = build_post(
        PostCreate(
            title=title,
            summary=summary or None,
            content=content,
            category_id=resolved_category_id,
            tag_ids=tag_ids,
        ),
        existing_slugs=existing_slugs,
    )
    if tag_ids:
        tags = list(db.execute(select(Tag).where(Tag.id.in_(tag_ids))).scalars().all())
        post.tags = tags

    db.add(post)
    db.commit()
    return RedirectResponse(url="/admin/posts", status_code=302)


@router.post("/{post_id}/publish")
def publish_post_route(post_id: int, request: Request, db: Session = Depends(get_db)):
    init_redirect = _require_initialized(db)
    if init_redirect:
        return init_redirect

    redirect = _require_login(request)
    if redirect:
        return redirect

    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404)

    publish_post(post)
    db.commit()
    return RedirectResponse(url="/admin/posts", status_code=302)


@router.post("/{post_id}/unpublish")
def unpublish_post_route(post_id: int, request: Request, db: Session = Depends(get_db)):
    init_redirect = _require_initialized(db)
    if init_redirect:
        return init_redirect

    redirect = _require_login(request)
    if redirect:
        return redirect

    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404)

    unpublish_post(post)
    db.commit()
    return RedirectResponse(url="/admin/posts", status_code=302)


@router.get("/{post_id}/edit", response_class=HTMLResponse)
def edit_post_page(post_id: int, request: Request, db: Session = Depends(get_db)):
    init_redirect = _require_initialized(db)
    if init_redirect:
        return init_redirect

    redirect = _require_login(request)
    if redirect:
        return redirect

    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404)

    categories, tags = _load_form_options(db)
    return templates.TemplateResponse(
        request,
        "admin/post_form.html",
        {
            "page_title": "编辑文章",
            "form_action": f"/admin/posts/{post_id}/edit",
            "submit_label": "更新",
            "post": post,
            "selected_tag_ids": [tag.id for tag in post.tags],
            "categories": categories,
            "tags": tags,
        },
    )


@router.post("/{post_id}/edit")
def edit_post(
    post_id: int,
    request: Request,
    title: str = Form(...),
    summary: str = Form(""),
    content: str = Form(...),
    category_id: int = Form(...),
    tag_ids: list[int] = Form(default=[]),
    db: Session = Depends(get_db),
):
    init_redirect = _require_initialized(db)
    if init_redirect:
        return init_redirect

    redirect = _require_login(request)
    if redirect:
        return redirect

    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404)

    tags = []
    if tag_ids:
        tags = list(db.execute(select(Tag).where(Tag.id.in_(tag_ids))).scalars().all())

    update_post(
        post,
        PostCreate(
            title=title,
            summary=summary or None,
            content=content,
            category_id=category_id,
            tag_ids=tag_ids,
        ),
        tags,
    )
    db.commit()
    return RedirectResponse(url="/admin/posts", status_code=302)
