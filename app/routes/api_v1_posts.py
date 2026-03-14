from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin
from app.core.error_codes import POST_NOT_FOUND
from app.core.hook_bus import hook_bus
from app.models import Post, Tag, User
from app.schemas.api_response import ApiResponse, error_response, ok_response
from app.schemas.post import PostCreate
from app.services.admin_post_service import get_tags_by_ids, resolve_category_id
from app.services.post_service import (
    build_post,
    get_post_by_slug,
    list_published_posts,
    publish_post,
    unpublish_post,
    update_post,
)

router = APIRouter(prefix="/api/v1", tags=["api-v1-posts"])

# 文章模块保持“前台读取 + 后台写作闭环”边界，不在这里继续承载平台化能力。

# request model / 辅助函数


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


def _serialize_post(post: Post) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "summary": post.summary,
        "content": post.content,
        "category_id": post.category_id,
        "category_name": post.category.name if post.category else None,
        "category_slug": post.category.slug if post.category else None,
        "tag_ids": [tag.id for tag in post.tags],
        "tags": [{"id": tag.id, "name": tag.name, "slug": tag.slug} for tag in post.tags],
        "published_at": post.published_at.isoformat() if post.published_at else None,
    }


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


def _build_post_create(
    db: Session,
    *,
    title: str,
    summary: str | None,
    content: str,
    category_id: int | None,
    tag_ids: list[int],
) -> PostCreate:
    return PostCreate(
        title=title,
        summary=summary,
        content=content,
        category_id=resolve_category_id(db, category_id),
        tag_ids=tag_ids,
    )


def _create_post_entity(db: Session, data: PostCreate) -> Post:
    existing_slugs = set(db.execute(select(Post.slug)).scalars().all())
    post = build_post(data, existing_slugs=existing_slugs)
    if data.tag_ids:
        post.tags = get_tags_by_ids(db, data.tag_ids)
    return post


def _save_post(db: Session, post: Post, *, event_name: str) -> JSONResponse:
    db.add(post)
    db.commit()
    db.refresh(post)
    hook_bus.emit(event_name, {"post_id": post.id, "slug": post.slug})
    return ok_response(_serialize_post(post), status_code=status.HTTP_201_CREATED)


def _commit_post_update(db: Session, post: Post, *, event_name: str) -> JSONResponse:
    db.commit()
    db.refresh(post)
    hook_bus.emit(event_name, {"post_id": post.id, "slug": post.slug})
    return ok_response(_serialize_post(post))


def _create_post_data(
    db: Session,
    *,
    title: str,
    summary: str | None,
    content: str,
    category_id: int | None,
    tag_ids: list[int],
) -> PostCreate:
    return _build_post_create(
        db,
        title=title,
        summary=summary,
        content=content,
        category_id=category_id,
        tag_ids=tag_ids,
    )


def _build_admin_post_query(category_id: int | None = None, tag_id: int | None = None):
    stmt = select(Post).order_by(Post.created_at.desc())
    if category_id is not None:
        stmt = stmt.where(Post.category_id == category_id)
    if tag_id is not None:
        stmt = stmt.where(Post.tags.any(Tag.id == tag_id))
    return stmt


def _get_post_or_404(db: Session, post_id: int) -> Post | JSONResponse:
    post = db.get(Post, post_id)
    if not post:
        return error_response("post_not_found", status.HTTP_404_NOT_FOUND, POST_NOT_FOUND)
    return post


# public read


@router.get("/posts", response_model=ApiResponse)
def list_posts_api(db: Session = Depends(get_db)) -> JSONResponse:
    posts = list_published_posts(db)
    return ok_response([_serialize_post(post) for post in posts])


@router.get("/posts/{slug}", response_model=ApiResponse)
def get_post_detail_api(slug: str, db: Session = Depends(get_db)) -> JSONResponse:
    post = get_post_by_slug(db, slug)
    if not post or not post.published_at:
        return error_response("post_not_found", status.HTTP_404_NOT_FOUND, POST_NOT_FOUND)
    return ok_response(_serialize_post(post))


# admin read/write


@router.get("/admin/posts", response_model=ApiResponse)
def list_admin_posts_api(
    category_id: int | None = None,
    tag_id: int | None = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    posts = list(db.execute(_build_admin_post_query(category_id, tag_id)).scalars().all())
    return ok_response([_serialize_post(post) for post in posts])


@router.post("/admin/posts", response_model=ApiResponse)
def create_admin_post_api(
    payload: AdminPostCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    data = _create_post_data(
        db,
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
    )
    post = _create_post_entity(db, data)
    return _save_post(db, post, event_name="post.created")


# markdown import/export


@router.post("/admin/posts/import-markdown", response_model=ApiResponse)
def import_markdown_post_api(
    payload: ImportMarkdownRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    data = _create_post_data(
        db,
        title=_extract_title(payload.markdown),
        summary=None,
        content=payload.markdown,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
    )
    post = _create_post_entity(db, data)
    return _save_post(db, post, event_name="post.created")


@router.post("/admin/posts/{post_id}", response_model=ApiResponse)
def update_admin_post_api(
    post_id: int,
    payload: AdminPostUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    post = _get_post_or_404(db, post_id)
    if isinstance(post, JSONResponse):
        return post

    data = _create_post_data(
        db,
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
    )
    tags = get_tags_by_ids(db, data.tag_ids)
    update_post(post, data, tags)
    return _commit_post_update(db, post, event_name="post.updated")


@router.get("/admin/posts/{post_id}/export-markdown", response_model=ApiResponse)
def export_markdown_post_api(
    post_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    post = _get_post_or_404(db, post_id)
    if isinstance(post, JSONResponse):
        return post

    markdown = f"# {post.title}\n\n{post.content}"
    return ok_response({"filename": f"{post.slug}.md", "markdown": markdown})


# publish workflow


@router.post("/admin/posts/{post_id}/publish", response_model=ApiResponse)
def publish_post_api(
    post_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    post = _get_post_or_404(db, post_id)
    if isinstance(post, JSONResponse):
        return post

    publish_post(post)
    return _commit_post_update(db, post, event_name="post.published")


@router.post("/admin/posts/{post_id}/unpublish", response_model=ApiResponse)
def unpublish_post_api(
    post_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    post = _get_post_or_404(db, post_id)
    if isinstance(post, JSONResponse):
        return post

    unpublish_post(post)
    return _commit_post_update(db, post, event_name="post.unpublished")
