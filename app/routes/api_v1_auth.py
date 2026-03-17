import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_csrf_header
from app.core.error_codes import INVALID_CREDENTIALS, SITE_NOT_INITIALIZED, TOO_MANY_ATTEMPTS
from app.core.exceptions import ConflictError, TooManyRequestsError, UnauthorizedError
from app.core.rate_limiter import login_limiter
from app.schemas.api_response import ApiResponse, ok_response
from app.services.auth_service import authenticate_user
from app.services.setup_service import is_initialized

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["api-v1-auth"])


def _get_client_ip(request: Request) -> str:
    """获取真实客户端 IP，支持反向代理"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=ApiResponse, summary="管理员登录")
def api_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    if not is_initialized(db):
        raise ConflictError("site_not_initialized", SITE_NOT_INITIALIZED)

    # 速率限制检查（同时限制 IP 和账户维度，防止伪造 X-Forwarded-For 绕过）
    client_ip = _get_client_ip(request)
    limit_key = f"{client_ip}:{username}"
    if login_limiter.is_blocked(limit_key):
        logger.warning("登录速率限制触发: IP=%s, user=%s", client_ip, username)
        raise TooManyRequestsError("too_many_attempts", TOO_MANY_ATTEMPTS)

    user = authenticate_user(db, username, password)
    if not user:
        login_limiter.record(limit_key)
        raise UnauthorizedError("invalid_credentials", INVALID_CREDENTIALS)

    # 登录成功，重置速率限制
    login_limiter.reset(limit_key)
    request.session["user_id"] = user.id
    return ok_response({"user_id": user.id, "username": user.username})


@router.post("/logout", response_model=ApiResponse, summary="管理员退出登录")
def api_logout(request: Request, _csrf: None = Depends(require_csrf_header)) -> JSONResponse:
    request.session.clear()
    return ok_response(None)
