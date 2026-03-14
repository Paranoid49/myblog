from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.error_codes import INVALID_CREDENTIALS, SITE_NOT_INITIALIZED
from app.schemas.api_response import ApiResponse, error_response, ok_response
from app.services.auth_service import authenticate_user
from app.services.setup_service import is_initialized

router = APIRouter(prefix="/api/v1/auth", tags=["api-v1-auth"])
@router.post("/login", response_model=ApiResponse)
def api_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> JSONResponse:
    if not is_initialized(db):
        return error_response("site_not_initialized", status.HTTP_409_CONFLICT, SITE_NOT_INITIALIZED)

    user = authenticate_user(db, username, password)
    if not user:
        return error_response("invalid_credentials", status.HTTP_401_UNAUTHORIZED, INVALID_CREDENTIALS)

    request.session["user_id"] = user.id
    return ok_response({"user_id": user.id, "username": user.username})


@router.post("/logout", response_model=ApiResponse)
def api_logout(request: Request) -> JSONResponse:
    request.session.clear()
    return ok_response(None)
