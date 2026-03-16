from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.error_codes import CATEGORY_NOT_FOUND, TAG_NOT_FOUND
from app.core.exceptions import NotFoundError
from app.schemas.api_response import ApiResponse, ok_response
from app.schemas.pagination import build_paginated_data
from app.schemas.serializers import serialize_category, serialize_post, serialize_tag
from app.services.taxonomy_service import (
    get_published_posts_by_category,
    get_published_posts_by_tag,
)

router = APIRouter(prefix="/api/v1", tags=["api-v1-taxonomy"])


@router.get("/categories/{slug}", response_model=ApiResponse)
def get_category_posts_api(
    slug: str, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
) -> JSONResponse:
    category, posts, total = get_published_posts_by_category(db, slug, page, page_size)
    if not category:
        raise NotFoundError("category_not_found", CATEGORY_NOT_FOUND)
    return ok_response(
        {
            "category": serialize_category(category),
            "posts": build_paginated_data([serialize_post(post) for post in posts], total, page, page_size),
        }
    )


@router.get("/tags/{slug}", response_model=ApiResponse)
def get_tag_posts_api(slug: str, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)) -> JSONResponse:
    tag, posts, total = get_published_posts_by_tag(db, slug, page, page_size)
    if not tag:
        raise NotFoundError("tag_not_found", TAG_NOT_FOUND)
    return ok_response(
        {
            "tag": serialize_tag(tag),
            "posts": build_paginated_data([serialize_post(post) for post in posts], total, page, page_size),
        }
    )
