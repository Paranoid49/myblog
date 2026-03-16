from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin, require_csrf_header
from app.core.error_codes import POST_NOT_FOUND
from app.core.exceptions import NotFoundError
from app.models import User
from app.schemas.api_response import ApiResponse, ok_response
from app.schemas.pagination import build_paginated_data
from app.schemas.post import AdminPostWriteRequest, ImportMarkdownRequest
from app.schemas.serializers import serialize_post
from app.services.post_service import (
    PostNotFoundError,
    build_markdown_export,
    build_post_create_payload,
    build_post_from_import_markdown,
    delete_post,
    get_post_or_raise,
    list_admin_posts,
    save_new_post,
    save_post_update,
    save_publish,
    save_unpublish,
)

router = APIRouter(prefix="/api/v1", tags=["api-v1-admin-posts"])

# 后台文章管理接口


@router.get("/admin/posts", response_model=ApiResponse)
def list_admin_posts_api(
    category_id: int | None = None,
    tag_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    posts, total = list_admin_posts(db, category_id, tag_id, page, page_size)
    return ok_response(
        build_paginated_data(
            [serialize_post(post) for post in posts], total, page, page_size
        )
    )


@router.post("/admin/posts", response_model=ApiResponse)
def create_admin_post_api(
    payload: AdminPostWriteRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
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


# markdown 导入/导出


@router.post("/admin/posts/import-markdown", response_model=ApiResponse)
def import_markdown_post_api(
    payload: ImportMarkdownRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
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
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    try:
        post = get_post_or_raise(db, post_id)
    except PostNotFoundError:
        raise NotFoundError("post_not_found", POST_NOT_FOUND)

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
        raise NotFoundError("post_not_found", POST_NOT_FOUND)

    return ok_response(build_markdown_export(post))


# 发布工作流


@router.post("/admin/posts/{post_id}/publish", response_model=ApiResponse)
def publish_post_api(
    post_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    try:
        post = get_post_or_raise(db, post_id)
    except PostNotFoundError:
        raise NotFoundError("post_not_found", POST_NOT_FOUND)

    post = save_publish(db, post)
    return ok_response(serialize_post(post))


@router.post("/admin/posts/{post_id}/unpublish", response_model=ApiResponse)
def unpublish_post_api(
    post_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    try:
        post = get_post_or_raise(db, post_id)
    except PostNotFoundError:
        raise NotFoundError("post_not_found", POST_NOT_FOUND)

    post = save_unpublish(db, post)
    return ok_response(serialize_post(post))


@router.post("/admin/posts/{post_id}/delete", response_model=ApiResponse)
def delete_post_api(
    post_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    try:
        post = get_post_or_raise(db, post_id)
    except PostNotFoundError:
        raise NotFoundError("post_not_found", POST_NOT_FOUND)
    delete_post(db, post)
    return ok_response(None)
