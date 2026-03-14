from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin
from app.core.error_codes import POST_NOT_FOUND
from app.core.hook_bus import hook_bus
from app.models import Post, User
from app.schemas.api_response import ApiResponse, error_response, ok_response
from app.schemas.post import AdminPostCreateRequest, AdminPostUpdateRequest, ImportMarkdownRequest
from app.services.post_service import (
    build_admin_post_list_query,
    build_markdown_export,
    build_post_create_payload,
    build_post_from_import_markdown,
    create_post,
    get_post_by_slug,
    list_published_posts,
    publish_post,
    unpublish_post,
    update_post,
)

router = APIRouter(prefix="/api/v1", tags=["api-v1-posts"])

# 文章模块保持“前台读取 + 后台写作闭环”边界，不在这里继续承载平台化能力。


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
    posts = list(db.execute(build_admin_post_list_query(category_id, tag_id)).scalars().all())
    return ok_response([_serialize_post(post) for post in posts])


@router.post("/admin/posts", response_model=ApiResponse)
def create_admin_post_api(
    payload: AdminPostCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    data, tags = build_post_create_payload(
        db,
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
    )
    post = create_post(db, data, tags)
    return _save_post(db, post, event_name="post.created")


# markdown import/export


@router.post("/admin/posts/import-markdown", response_model=ApiResponse)
def import_markdown_post_api(
    payload: ImportMarkdownRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    data, tags = build_post_from_import_markdown(db, payload)
    post = create_post(db, data, tags)
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

    data, tags = build_post_create_payload(
        db,
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
    )
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

    return ok_response(build_markdown_export(post))


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
