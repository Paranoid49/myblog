from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.error_codes import CATEGORY_NOT_FOUND, CSRF_REJECTED, POST_NOT_FOUND, TAG_NOT_FOUND, UNAUTHORIZED
from app.core.exceptions import NotFoundError
from app.models import Category, Post, Tag, User
from app.schemas.api_response import build_error_detail

UNAUTHORIZED_DETAIL = build_error_detail("unauthorized", UNAUTHORIZED)
CSRF_DETAIL = build_error_detail("csrf_rejected", CSRF_REJECTED)


def require_csrf_header(request: Request) -> None:
    """写接口要求携带自定义头，阻断浏览器默认表单提交的 CSRF 攻击"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        raise HTTPException(status_code=403, detail=CSRF_DETAIL)


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_DETAIL)

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_DETAIL)

    return user


def get_category_or_404(category_id: int, db: Session = Depends(get_db)) -> Category:
    """依赖注入：获取分类或返回 404"""
    category = db.get(Category, category_id)
    if not category:
        raise NotFoundError("category_not_found", CATEGORY_NOT_FOUND)
    return category


def get_tag_or_404(tag_id: int, db: Session = Depends(get_db)) -> Tag:
    """依赖注入：获取标签或返回 404"""
    tag = db.get(Tag, tag_id)
    if not tag:
        raise NotFoundError("tag_not_found", TAG_NOT_FOUND)
    return tag


def get_post_or_404(post_id: int, db: Session = Depends(get_db)) -> Post:
    """依赖注入：获取文章或返回 404，预加载 category 和 tags"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    post = db.execute(
        select(Post).options(selectinload(Post.category), selectinload(Post.tags)).where(Post.id == post_id)
    ).scalar_one_or_none()
    if not post:
        raise NotFoundError("post_not_found", POST_NOT_FOUND)
    return post
