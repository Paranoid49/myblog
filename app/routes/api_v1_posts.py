from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.hook_bus import hook_bus
from app.models import Category, Post, Tag
from app.schemas.post import PostCreate
from app.services.post_service import (
    build_post,
    get_post_by_slug,
    list_published_posts,
    publish_post,
    slugify,
    unpublish_post,
    update_post,
)
from app.services.setup_service import is_initialized

router = APIRouter(prefix="/api/v1", tags=["api-v1-posts"])

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "static" / "uploads"
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class AdminPostCreateRequest(BaseModel):
    title: str
    summary: str | None = None
    content: str
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)

    @field_validator("title", "content")
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value


class AdminPostUpdateRequest(BaseModel):
    title: str
    summary: str | None = None
    content: str
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)

    @field_validator("title", "content")
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value


class NameCreateRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value


class ImportMarkdownRequest(BaseModel):
    markdown: str
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)

    @field_validator("markdown")
    @classmethod
    def _markdown_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value


class ApiResponse(BaseModel):
    code: int
    message: str
    data: dict | list | None


def _ok(data: dict | list | None = None, message: str = "ok", status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": 0, "message": message, "data": data})


def _error(message: str, status_code: int, code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": None})


def _require_initialized(db: Session) -> JSONResponse | None:
    if not is_initialized(db):
        return _error("site_not_initialized", status.HTTP_409_CONFLICT, 1001)
    return None


def _require_login(request: Request) -> JSONResponse | None:
    if not request.session.get("user_id"):
        return _error("unauthorized", status.HTTP_401_UNAUTHORIZED, 1002)
    return None


def _resolve_category_id(db: Session, category_id: int | None) -> int:
    if category_id is not None:
        return category_id

    default_category = db.execute(select(Category).where(Category.slug == "default")).scalar_one_or_none()
    if default_category is None:
        default_category = db.execute(select(Category).where(Category.name == "默认分类")).scalar_one_or_none()

    if default_category is None:
        default_category = Category(name="默认分类", slug="default")
        db.add(default_category)
        db.flush()

    return default_category.id


def _serialize_post(post: Post) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "summary": post.summary,
        "content": post.content,
        "category_id": post.category_id,
        "category_name": post.category.name if post.category else None,
        "tag_ids": [tag.id for tag in post.tags],
        "tags": [{"id": tag.id, "name": tag.name, "slug": tag.slug} for tag in post.tags],
        "published_at": post.published_at.isoformat() if post.published_at else None,
    }


def _serialize_category(category: Category) -> dict:
    return {"id": category.id, "name": category.name, "slug": category.slug}


def _serialize_tag(tag: Tag) -> dict:
    return {"id": tag.id, "name": tag.name, "slug": tag.slug}


def _extract_title(markdown: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip() or "Untitled"
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:80]
    return "Untitled"


@router.get("/posts", response_model=ApiResponse)
def list_posts_api(db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    posts = list_published_posts(db)
    return _ok([_serialize_post(post) for post in posts])


@router.get("/posts/{slug}", response_model=ApiResponse)
def get_post_detail_api(slug: str, db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    post = get_post_by_slug(db, slug)
    if not post or not post.published_at:
        return _error("post_not_found", status.HTTP_404_NOT_FOUND, 1404)

    return _ok(_serialize_post(post))


@router.get("/admin/posts", response_model=ApiResponse)
def list_admin_posts_api(
    request: Request,
    category_id: int | None = None,
    tag_id: int | None = None,
    db: Session = Depends(get_db),
) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    stmt = select(Post).order_by(Post.created_at.desc())
    if category_id is not None:
        stmt = stmt.where(Post.category_id == category_id)
    if tag_id is not None:
        stmt = stmt.where(Post.tags.any(Tag.id == tag_id))

    posts = list(db.execute(stmt).scalars().all())
    return _ok([_serialize_post(post) for post in posts])


@router.post("/admin/posts", response_model=ApiResponse)
def create_admin_post_api(payload: AdminPostCreateRequest, request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    resolved_category_id = _resolve_category_id(db, payload.category_id)
    existing_slugs = set(db.execute(select(Post.slug)).scalars().all())
    post = build_post(
        PostCreate(
            title=payload.title,
            summary=payload.summary,
            content=payload.content,
            category_id=resolved_category_id,
            tag_ids=payload.tag_ids,
        ),
        existing_slugs=existing_slugs,
    )
    if payload.tag_ids:
        tags = list(db.execute(select(Tag).where(Tag.id.in_(payload.tag_ids))).scalars().all())
        post.tags = tags

    db.add(post)
    db.commit()
    db.refresh(post)
    hook_bus.emit("post.created", {"post_id": post.id, "slug": post.slug})
    return _ok(_serialize_post(post), status_code=status.HTTP_201_CREATED)


@router.post("/admin/posts/import-markdown", response_model=ApiResponse)
def import_markdown_post_api(payload: ImportMarkdownRequest, request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    title = _extract_title(payload.markdown)
    resolved_category_id = _resolve_category_id(db, payload.category_id)
    existing_slugs = set(db.execute(select(Post.slug)).scalars().all())
    post = build_post(
        PostCreate(
            title=title,
            summary=None,
            content=payload.markdown,
            category_id=resolved_category_id,
            tag_ids=payload.tag_ids,
        ),
        existing_slugs=existing_slugs,
    )
    if payload.tag_ids:
        tags = list(db.execute(select(Tag).where(Tag.id.in_(payload.tag_ids))).scalars().all())
        post.tags = tags

    db.add(post)
    db.commit()
    db.refresh(post)
    hook_bus.emit("post.created", {"post_id": post.id, "slug": post.slug})
    return _ok(_serialize_post(post), status_code=status.HTTP_201_CREATED)


@router.post("/admin/posts/{post_id}", response_model=ApiResponse)
def update_admin_post_api(post_id: int, payload: AdminPostUpdateRequest, request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    post = db.get(Post, post_id)
    if not post:
        return _error("post_not_found", status.HTTP_404_NOT_FOUND, 1404)

    resolved_category_id = _resolve_category_id(db, payload.category_id)
    tags = []
    if payload.tag_ids:
        tags = list(db.execute(select(Tag).where(Tag.id.in_(payload.tag_ids))).scalars().all())

    update_post(
        post,
        PostCreate(
            title=payload.title,
            summary=payload.summary,
            content=payload.content,
            category_id=resolved_category_id,
            tag_ids=payload.tag_ids,
        ),
        tags,
    )

    db.commit()
    db.refresh(post)
    hook_bus.emit("post.updated", {"post_id": post.id, "slug": post.slug})
    return _ok(_serialize_post(post))


@router.get("/admin/posts/{post_id}/export-markdown", response_model=ApiResponse)
def export_markdown_post_api(post_id: int, request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    post = db.get(Post, post_id)
    if not post:
        return _error("post_not_found", status.HTTP_404_NOT_FOUND, 1404)

    markdown = f"# {post.title}\n\n{post.content}"
    return _ok({"filename": f"{post.slug}.md", "markdown": markdown})


@router.post("/admin/media/images", response_model=ApiResponse)
async def upload_image_api(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        return _error("unsupported_image_type", status.HTTP_400_BAD_REQUEST, 1411)

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        return _error("image_too_large", status.HTTP_400_BAD_REQUEST, 1412)

    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    ext = ext_map.get(content_type, ".img")
    filename = f"{slugify(Path(file.filename or 'image').stem)}-{len(content)}{ext}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / filename
    save_path.write_bytes(content)

    url = f"/static/uploads/{filename}"
    hook_bus.emit("media.image_uploaded", {"key": filename, "url": url, "content_type": content_type})
    return _ok(
        {
            "url": url,
            "key": filename,
            "size": len(content),
            "content_type": content_type,
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/admin/posts/{post_id}/publish", response_model=ApiResponse)
def publish_post_api(post_id: int, request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    post = db.get(Post, post_id)
    if not post:
        return _error("post_not_found", status.HTTP_404_NOT_FOUND, 1404)

    publish_post(post)
    db.commit()
    db.refresh(post)
    hook_bus.emit("post.published", {"post_id": post.id, "slug": post.slug})
    return _ok(_serialize_post(post))


@router.post("/admin/posts/{post_id}/unpublish", response_model=ApiResponse)
def unpublish_post_api(post_id: int, request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    post = db.get(Post, post_id)
    if not post:
        return _error("post_not_found", status.HTTP_404_NOT_FOUND, 1404)

    unpublish_post(post)
    db.commit()
    db.refresh(post)
    hook_bus.emit("post.unpublished", {"post_id": post.id, "slug": post.slug})
    return _ok(_serialize_post(post))


@router.get("/taxonomy", response_model=ApiResponse)
def list_taxonomy_api(request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    categories = list(db.execute(select(Category).order_by(Category.name.asc())).scalars().all())
    tags = list(db.execute(select(Tag).order_by(Tag.name.asc())).scalars().all())
    return _ok(
        {
            "categories": [_serialize_category(category) for category in categories],
            "tags": [_serialize_tag(tag) for tag in tags],
        }
    )


@router.post("/admin/categories", response_model=ApiResponse)
def create_category_api(payload: NameCreateRequest, request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    normalized_name = payload.name.strip()
    category_slug = slugify(normalized_name)
    exists = db.execute(select(Category.id).where(Category.slug == category_slug)).first() is not None
    if exists:
        return _error("category_exists", status.HTTP_409_CONFLICT, 1409)

    category = Category(name=normalized_name, slug=category_slug)
    db.add(category)
    db.commit()
    db.refresh(category)
    return _ok(_serialize_category(category), status_code=status.HTTP_201_CREATED)


@router.post("/admin/tags", response_model=ApiResponse)
def create_tag_api(payload: NameCreateRequest, request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    init_error = _require_initialized(db)
    if init_error:
        return init_error

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    normalized_name = payload.name.strip()
    tag_slug = slugify(normalized_name)
    exists = db.execute(select(Tag.id).where(Tag.slug == tag_slug)).first() is not None
    if exists:
        return _error("tag_exists", status.HTTP_409_CONFLICT, 1410)

    tag = Tag(name=normalized_name, slug=tag_slug)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return _ok(_serialize_tag(tag), status_code=status.HTTP_201_CREATED)
