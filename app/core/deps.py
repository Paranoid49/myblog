from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.error_codes import CSRF_REJECTED, POST_NOT_FOUND, UNAUTHORIZED
from app.core.exceptions import NotFoundError
from app.models import User
from app.schemas.api_response import build_error_detail
from app.services.post_service import PostNotFoundError, get_post_or_raise

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


def get_post_or_404(
    post_id: int, db: Session = Depends(get_db)
) -> "Post":
    """获取文章或抛出 404，用于路由依赖注入"""
    from app.models import Post  # 延迟导入避免循环依赖

    try:
        return get_post_or_raise(db, post_id)
    except PostNotFoundError:
        raise NotFoundError("post_not_found", POST_NOT_FOUND) from None
