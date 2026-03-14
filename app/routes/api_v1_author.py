from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin
from app.core.error_codes import SITE_NOT_INITIALIZED
from app.models import User
from app.schemas.api_response import ApiResponse, error_response, ok_response
from app.services.setup_service import get_site_settings

router = APIRouter(prefix="/api/v1/author", tags=["api-v1-author"])


class AuthorProfileUpdateRequest(BaseModel):
    name: str
    bio: str
    email: str
    avatar: str = ""
    link: str = ""

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value.strip()

    @field_validator("bio", "email", "avatar", "link")
    @classmethod
    def _trim_text(cls, value: str) -> str:
        return value.strip()


def _serialize_author(settings) -> dict:
    return {
        "name": settings.author_name,
        "bio": settings.author_bio,
        "email": settings.author_email,
        "avatar": settings.author_avatar,
        "link": settings.author_link,
    }


@router.get("", response_model=ApiResponse)
def get_author_profile(db: Session = Depends(get_db)) -> JSONResponse:
    settings = get_site_settings(db)
    if settings is None:
        return error_response("site_not_initialized", status.HTTP_409_CONFLICT, SITE_NOT_INITIALIZED)

    return ok_response(_serialize_author(settings))


@router.post("", response_model=ApiResponse)
def update_author_profile(
    payload: AuthorProfileUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    settings = get_site_settings(db)
    if settings is None:
        return error_response("site_not_initialized", status.HTTP_409_CONFLICT, SITE_NOT_INITIALIZED)

    settings.author_name = payload.name
    settings.author_bio = payload.bio
    settings.author_email = payload.email
    settings.author_avatar = payload.avatar
    settings.author_link = payload.link
    db.commit()
    db.refresh(settings)

    return ok_response(_serialize_author(settings))