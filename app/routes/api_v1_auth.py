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

router = APIRouter(prefix="/api/v1/auth", tags=["api-v1-auth"])
@router.post("/login", response_model=ApiResponse)
def api_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    if not is_initialized(db):
        raise ConflictError("site_not_initialized", SITE_NOT_INITIALIZED)

    # 速率限制检查
    client_ip = request.client.host if request.client else "unknown"
    if login_limiter.is_blocked(client_ip):
        raise TooManyRequestsError("too_many_attempts", TOO_MANY_ATTEMPTS)

    user = authenticate_user(db, username, password)
    if not user:
        login_limiter.record(client_ip)
        raise UnauthorizedError("invalid_credentials", INVALID_CREDENTIALS)

    # 登录成功，重置速率限制
    login_limiter.reset(client_ip)
    request.session["user_id"] = user.id
    return ok_response({"user_id": user.id, "username": user.username})


@router.post("/logout", response_model=ApiResponse)
def api_logout(request: Request, _csrf: None = Depends(require_csrf_header)) -> JSONResponse:
    request.session.clear()
    return ok_response(None)
