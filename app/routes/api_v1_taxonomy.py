from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin
from app.models import Category, Tag, User
from app.schemas.api_response import ApiResponse, error_response, ok_response
from app.services.admin_post_service import category_exists_by_name, tag_exists_by_name
from app.services.post_service import slugify
from app.services.taxonomy_service import get_category_by_slug, get_tag_by_slug, list_taxonomy

router = APIRouter(prefix="/api/v1", tags=["api-v1-taxonomy"])


class NameCreateRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value


def _serialize_category(category: Category) -> dict:
    return {"id": category.id, "name": category.name, "slug": category.slug}


def _serialize_tag(tag: Tag) -> dict:
    return {"id": tag.id, "name": tag.name, "slug": tag.slug}


def _serialize_post(post) -> dict:
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


@router.get("/categories/{slug}", response_model=ApiResponse)
def get_category_posts_api(slug: str, db: Session = Depends(get_db)) -> JSONResponse:
    category = get_category_by_slug(db, slug)
    if not category:
        return error_response("category_not_found", status.HTTP_404_NOT_FOUND, 1413)

    posts = [post for post in category.posts if post.published_at]
    posts.sort(key=lambda post: post.published_at, reverse=True)
    return ok_response({"category": _serialize_category(category), "posts": [_serialize_post(post) for post in posts]})


@router.get("/tags/{slug}", response_model=ApiResponse)
def get_tag_posts_api(slug: str, db: Session = Depends(get_db)) -> JSONResponse:
    tag = get_tag_by_slug(db, slug)
    if not tag:
        return error_response("tag_not_found", status.HTTP_404_NOT_FOUND, 1414)

    posts = [post for post in tag.posts if post.published_at]
    posts.sort(key=lambda post: post.published_at, reverse=True)
    return ok_response({"tag": _serialize_tag(tag), "posts": [_serialize_post(post) for post in posts]})


@router.get("/taxonomy", response_model=ApiResponse)
def list_taxonomy_api(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> JSONResponse:
    categories, tags = list_taxonomy(db)
    return ok_response({"categories": [_serialize_category(category) for category in categories], "tags": [_serialize_tag(tag) for tag in tags]})


@router.post("/admin/categories", response_model=ApiResponse)
def create_category_api(
    payload: NameCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    normalized_name = payload.name.strip()
    category_slug = slugify(normalized_name)
    if category_exists_by_name(db, normalized_name):
        return error_response("category_exists", status.HTTP_409_CONFLICT, 1409)

    category = Category(name=normalized_name, slug=category_slug)
    db.add(category)
    db.commit()
    db.refresh(category)
    return ok_response(_serialize_category(category), status_code=status.HTTP_201_CREATED)


@router.post("/admin/tags", response_model=ApiResponse)
def create_tag_api(
    payload: NameCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    normalized_name = payload.name.strip()
    tag_slug = slugify(normalized_name)
    if tag_exists_by_name(db, normalized_name):
        return error_response("tag_exists", status.HTTP_409_CONFLICT, 1410)

    tag = Tag(name=normalized_name, slug=tag_slug)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return ok_response(_serialize_tag(tag), status_code=status.HTTP_201_CREATED)
