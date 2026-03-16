from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.error_codes import POST_NOT_FOUND
from app.core.exceptions import NotFoundError
from app.schemas.api_response import ApiResponse, ok_response
from app.schemas.pagination import build_paginated_data
from app.schemas.serializers import serialize_post
from app.services.post_service import get_post_by_slug, list_published_posts

router = APIRouter(prefix="/api/v1", tags=["api-v1-posts"])

# 公开文章接口


@router.get("/posts", response_model=ApiResponse)
def list_posts_api(
    page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
) -> JSONResponse:
    posts, total = list_published_posts(db, page, page_size)
    return ok_response(
        build_paginated_data(
            [serialize_post(post) for post in posts], total, page, page_size
        )
    )


@router.get("/posts/{slug}", response_model=ApiResponse)
def get_post_detail_api(slug: str, db: Session = Depends(get_db)) -> JSONResponse:
    post = get_post_by_slug(db, slug)
    if not post or not post.published_at:
        raise NotFoundError("post_not_found", POST_NOT_FOUND)
    return ok_response(serialize_post(post))
