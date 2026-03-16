from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin, require_csrf_header
from app.core.error_codes import CATEGORY_EXISTS, CATEGORY_NOT_FOUND, TAG_EXISTS, TAG_NOT_FOUND
from app.models import Category, Tag, User
from app.schemas.api_response import ApiResponse, error_response, ok_response
from app.schemas.pagination import build_paginated_data
from app.schemas.serializers import serialize_category, serialize_post, serialize_tag
from app.schemas.taxonomy import NameCreateRequest
from app.services.taxonomy_service import (
    category_exists_by_name,
    create_category,
    create_tag,
    delete_category,
    delete_tag,
    get_category_by_slug,
    get_published_posts_by_category,
    get_published_posts_by_tag,
    get_tag_by_slug,
    list_taxonomy,
    tag_exists_by_name,
    update_category,
    update_tag,
)

router = APIRouter(prefix="/api/v1", tags=["api-v1-taxonomy"])


@router.get("/categories/{slug}", response_model=ApiResponse)
def get_category_posts_api(
    slug: str, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
) -> JSONResponse:
    category, posts, total = get_published_posts_by_category(db, slug, page, page_size)
    if not category:
        return error_response("category_not_found", status.HTTP_404_NOT_FOUND, CATEGORY_NOT_FOUND)
    return ok_response({
        "category": serialize_category(category),
        "posts": build_paginated_data(
            [serialize_post(post) for post in posts], total, page, page_size
        ),
    })


@router.get("/tags/{slug}", response_model=ApiResponse)
def get_tag_posts_api(
    slug: str, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
) -> JSONResponse:
    tag, posts, total = get_published_posts_by_tag(db, slug, page, page_size)
    if not tag:
        return error_response("tag_not_found", status.HTTP_404_NOT_FOUND, TAG_NOT_FOUND)
    return ok_response({
        "tag": serialize_tag(tag),
        "posts": build_paginated_data(
            [serialize_post(post) for post in posts], total, page, page_size
        ),
    })


@router.get("/taxonomy", response_model=ApiResponse)
def list_taxonomy_api(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> JSONResponse:
    categories, tags = list_taxonomy(db)
    return ok_response({"categories": [serialize_category(category) for category in categories], "tags": [serialize_tag(tag) for tag in tags]})


@router.post("/admin/categories", response_model=ApiResponse)
def create_category_api(
    payload: NameCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    normalized_name = payload.name.strip()
    if category_exists_by_name(db, normalized_name):
        return error_response("category_exists", status.HTTP_409_CONFLICT, CATEGORY_EXISTS)

    category = create_category(db, normalized_name)
    return ok_response(serialize_category(category), status_code=status.HTTP_201_CREATED)


@router.post("/admin/tags", response_model=ApiResponse)
def create_tag_api(
    payload: NameCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    normalized_name = payload.name.strip()
    if tag_exists_by_name(db, normalized_name):
        return error_response("tag_exists", status.HTTP_409_CONFLICT, TAG_EXISTS)

    tag = create_tag(db, normalized_name)
    return ok_response(serialize_tag(tag), status_code=status.HTTP_201_CREATED)


@router.post("/admin/categories/{category_id}", response_model=ApiResponse)
def update_category_api(
    category_id: int,
    payload: NameCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    category = db.get(Category, category_id)
    if not category:
        return error_response("category_not_found", status.HTTP_404_NOT_FOUND, CATEGORY_NOT_FOUND)
    normalized_name = payload.name.strip()
    if category_exists_by_name(db, normalized_name):
        return error_response("category_exists", status.HTTP_409_CONFLICT, CATEGORY_EXISTS)
    category = update_category(db, category, normalized_name)
    return ok_response(serialize_category(category))


@router.post("/admin/categories/{category_id}/delete", response_model=ApiResponse)
def delete_category_api(
    category_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    category = db.get(Category, category_id)
    if not category:
        return error_response("category_not_found", status.HTTP_404_NOT_FOUND, CATEGORY_NOT_FOUND)
    delete_category(db, category)
    return ok_response(None)


@router.post("/admin/tags/{tag_id}", response_model=ApiResponse)
def update_tag_api(
    tag_id: int,
    payload: NameCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    tag = db.get(Tag, tag_id)
    if not tag:
        return error_response("tag_not_found", status.HTTP_404_NOT_FOUND, TAG_NOT_FOUND)
    normalized_name = payload.name.strip()
    if tag_exists_by_name(db, normalized_name):
        return error_response("tag_exists", status.HTTP_409_CONFLICT, TAG_EXISTS)
    tag = update_tag(db, tag, normalized_name)
    return ok_response(serialize_tag(tag))


@router.post("/admin/tags/{tag_id}/delete", response_model=ApiResponse)
def delete_tag_api(
    tag_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    tag = db.get(Tag, tag_id)
    if not tag:
        return error_response("tag_not_found", status.HTTP_404_NOT_FOUND, TAG_NOT_FOUND)
    delete_tag(db, tag)
    return ok_response(None)
