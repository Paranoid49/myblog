from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin
from app.core.error_codes import CATEGORY_EXISTS, CATEGORY_NOT_FOUND, TAG_EXISTS, TAG_NOT_FOUND
from app.models import User
from app.schemas.api_response import ApiResponse, error_response, ok_response
from app.schemas.serializers import serialize_category, serialize_post, serialize_tag
from app.schemas.taxonomy import NameCreateRequest
from app.services.admin_post_service import category_exists_by_name, tag_exists_by_name
from app.services.taxonomy_service import (
    create_category,
    create_tag,
    get_category_by_slug,
    get_tag_by_slug,
    list_taxonomy,
)

router = APIRouter(prefix="/api/v1", tags=["api-v1-taxonomy"])


@router.get("/categories/{slug}", response_model=ApiResponse)
def get_category_posts_api(slug: str, db: Session = Depends(get_db)) -> JSONResponse:
    category = get_category_by_slug(db, slug)
    if not category:
        return error_response("category_not_found", status.HTTP_404_NOT_FOUND, CATEGORY_NOT_FOUND)

    posts = [post for post in category.posts if post.published_at]
    posts.sort(key=lambda post: post.published_at, reverse=True)
    return ok_response({"category": serialize_category(category), "posts": [serialize_post(post) for post in posts]})


@router.get("/tags/{slug}", response_model=ApiResponse)
def get_tag_posts_api(slug: str, db: Session = Depends(get_db)) -> JSONResponse:
    tag = get_tag_by_slug(db, slug)
    if not tag:
        return error_response("tag_not_found", status.HTTP_404_NOT_FOUND, TAG_NOT_FOUND)

    posts = [post for post in tag.posts if post.published_at]
    posts.sort(key=lambda post: post.published_at, reverse=True)
    return ok_response({"tag": serialize_tag(tag), "posts": [serialize_post(post) for post in posts]})


@router.get("/taxonomy", response_model=ApiResponse)
def list_taxonomy_api(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> JSONResponse:
    categories, tags = list_taxonomy(db)
    return ok_response({"categories": [serialize_category(category) for category in categories], "tags": [serialize_tag(tag) for tag in tags]})


@router.post("/admin/categories", response_model=ApiResponse)
def create_category_api(
    payload: NameCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
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
) -> JSONResponse:
    normalized_name = payload.name.strip()
    if tag_exists_by_name(db, normalized_name):
        return error_response("tag_exists", status.HTTP_409_CONFLICT, TAG_EXISTS)

    tag = create_tag(db, normalized_name)
    return ok_response(serialize_tag(tag), status_code=status.HTTP_201_CREATED)
