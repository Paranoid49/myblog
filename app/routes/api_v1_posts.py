from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Category, Post, Tag
from app.schemas.post import PostCreate
from app.services.post_service import build_post, list_published_posts
from app.services.setup_service import is_initialized

router = APIRouter(prefix="/api/v1", tags=["api-v1-posts"])


class AdminPostCreateRequest(BaseModel):
    title: str
    summary: str | None = None
    content: str
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)


class ApiPostItem(BaseModel):
    id: int
    title: str
    slug: str
    summary: str | None
    category_id: int
    published_at: str | None


class ApiResponse(BaseModel):
    code: int
    message: str
    data: dict | list


def _api_response(data: dict | list, message: str = "ok", code: int = 0) -> dict:
    return {"code": code, "message": message, "data": data}


def _require_initialized(db: Session) -> None:
    if not is_initialized(db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="site_not_initialized")


def _require_login(request: Request) -> None:
    if not request.session.get("user_id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")


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
        "category_id": post.category_id,
        "published_at": post.published_at.isoformat() if post.published_at else None,
    }


@router.get("/posts", response_model=ApiResponse)
def list_posts_api(db: Session = Depends(get_db)) -> dict:
    _require_initialized(db)
    posts = list_published_posts(db)
    return _api_response([_serialize_post(post) for post in posts])


@router.post("/admin/posts", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_admin_post_api(payload: AdminPostCreateRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    _require_initialized(db)
    _require_login(request)

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
    return _api_response(_serialize_post(post))
