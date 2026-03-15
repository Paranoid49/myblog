from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin
from app.core.error_codes import POST_NOT_FOUND
from app.models import User
from app.schemas.api_response import ApiResponse, error_response, ok_response
from app.schemas.post import AdminPostWriteRequest, ImportMarkdownRequest
from app.schemas.serializers import serialize_post
from app.services.post_service import (
    PostNotFoundError,
    build_markdown_export,
    build_post_create_payload,
    build_post_from_import_markdown,
    get_post_by_slug,
    get_post_or_raise,
    list_admin_posts,
    list_published_posts,
    save_new_post,
    save_post_update,
    save_publish,
    save_unpublish,
)

router = APIRouter(prefix="/api/v1", tags=["api-v1-posts"])

# 文章模块保持"前台读取 + 后台写作闭环"边界，不在这里继续承载平台化能力。


# public read


@router.get("/posts", response_model=ApiResponse)
def list_posts_api(db: Session = Depends(get_db)) -> JSONResponse:
    posts = list_published_posts(db)
    return ok_response([serialize_post(post) for post in posts])


@router.get("/posts/{slug}", response_model=ApiResponse)
def get_post_detail_api(slug: str, db: Session = Depends(get_db)) -> JSONResponse:
    post = get_post_by_slug(db, slug)
    if not post or not post.published_at:
        return error_response("post_not_found", status.HTTP_404_NOT_FOUND, POST_NOT_FOUND)
    return ok_response(serialize_post(post))


# admin read/write


@router.get("/admin/posts", response_model=ApiResponse)
def list_admin_posts_api(
    category_id: int | None = None,
    tag_id: int | None = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    posts = list_admin_posts(db, category_id, tag_id)
    return ok_response([serialize_post(post) for post in posts])


@router.post("/admin/posts", response_model=ApiResponse)
def create_admin_post_api(
    payload: AdminPostWriteRequest,
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
    post = save_new_post(db, data, tags)
    return ok_response(serialize_post(post), status_code=status.HTTP_201_CREATED)


# markdown import/export


@router.post("/admin/posts/import-markdown", response_model=ApiResponse)
def import_markdown_post_api(
    payload: ImportMarkdownRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    data, tags = build_post_from_import_markdown(db, payload)
    post = save_new_post(db, data, tags)
    return ok_response(serialize_post(post), status_code=status.HTTP_201_CREATED)


@router.post("/admin/posts/{post_id}", response_model=ApiResponse)
def update_admin_post_api(
    post_id: int,
    payload: AdminPostWriteRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    try:
        post = get_post_or_raise(db, post_id)
    except PostNotFoundError:
        return error_response("post_not_found", status.HTTP_404_NOT_FOUND, POST_NOT_FOUND)

    data, tags = build_post_create_payload(
        db,
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
    )
    post = save_post_update(db, post, data, tags)
    return ok_response(serialize_post(post))


@router.get("/admin/posts/{post_id}/export-markdown", response_model=ApiResponse)
def export_markdown_post_api(
    post_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    try:
        post = get_post_or_raise(db, post_id)
    except PostNotFoundError:
        return error_response("post_not_found", status.HTTP_404_NOT_FOUND, POST_NOT_FOUND)

    return ok_response(build_markdown_export(post))


# publish workflow


@router.post("/admin/posts/{post_id}/publish", response_model=ApiResponse)
def publish_post_api(
    post_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    try:
        post = get_post_or_raise(db, post_id)
    except PostNotFoundError:
        return error_response("post_not_found", status.HTTP_404_NOT_FOUND, POST_NOT_FOUND)

    post = save_publish(db, post)
    return ok_response(serialize_post(post))


@router.post("/admin/posts/{post_id}/unpublish", response_model=ApiResponse)
def unpublish_post_api(
    post_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    try:
        post = get_post_or_raise(db, post_id)
    except PostNotFoundError:
        return error_response("post_not_found", status.HTTP_404_NOT_FOUND, POST_NOT_FOUND)

    post = save_unpublish(db, post)
    return ok_response(serialize_post(post))
