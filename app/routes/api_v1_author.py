from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.setup_service import get_site_settings, is_initialized

router = APIRouter(prefix="/api/v1/author", tags=["api-v1-author"])


class ApiResponse(BaseModel):
    code: int
    message: str
    data: dict | None


class AuthorProfileUpdateRequest(BaseModel):
    name: str
    bio: str
    email: str

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value.strip()

    @field_validator("bio", "email")
    @classmethod
    def _trim_text(cls, value: str) -> str:
        return value.strip()



def _ok(data: dict | None = None, message: str = "ok", status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": 0, "message": message, "data": data})



def _error(message: str, status_code: int, code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": None})



def _require_login(request: Request) -> JSONResponse | None:
    if not request.session.get("user_id"):
        return _error("unauthorized", status.HTTP_401_UNAUTHORIZED, 1002)
    return None



def _serialize_author(settings) -> dict:
    return {
        "name": settings.author_name,
        "bio": settings.author_bio,
        "email": settings.author_email,
    }


@router.get("", response_model=ApiResponse)
def get_author_profile(db: Session = Depends(get_db)) -> JSONResponse:
    if not is_initialized(db):
        return _error("site_not_initialized", status.HTTP_409_CONFLICT, 1001)

    settings = get_site_settings(db)
    if settings is None:
        return _error("site_not_initialized", status.HTTP_409_CONFLICT, 1001)

    return _ok(_serialize_author(settings))


@router.post("", response_model=ApiResponse)
def update_author_profile(payload: AuthorProfileUpdateRequest, request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    if not is_initialized(db):
        return _error("site_not_initialized", status.HTTP_409_CONFLICT, 1001)

    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    settings = get_site_settings(db)
    if settings is None:
        return _error("site_not_initialized", status.HTTP_409_CONFLICT, 1001)

    settings.author_name = payload.name
    settings.author_bio = payload.bio
    settings.author_email = payload.email
    db.commit()
    db.refresh(settings)

    return _ok(_serialize_author(settings))
