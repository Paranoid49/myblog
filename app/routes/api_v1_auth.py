from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.auth_service import authenticate_user
from app.services.setup_service import is_initialized

router = APIRouter(prefix="/api/v1/auth", tags=["api-v1-auth"])


def _ok(data: dict | None = None, message: str = "ok", status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": 0, "message": message, "data": data})


def _error(message: str, status_code: int, code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": None})


@router.post("/login")
def api_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> JSONResponse:
    if not is_initialized(db):
        return _error("site_not_initialized", status.HTTP_409_CONFLICT, 1001)

    user = authenticate_user(db, username, password)
    if not user:
        return _error("invalid_credentials", status.HTTP_401_UNAUTHORIZED, 1003)

    request.session["user_id"] = user.id
    return _ok({"user_id": user.id, "username": user.username})


@router.post("/logout")
def api_logout(request: Request) -> JSONResponse:
    request.session.clear()
    return _ok(None)
