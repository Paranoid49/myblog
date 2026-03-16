from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin, require_csrf_header
from app.core.error_codes import SITE_NOT_INITIALIZED
from app.core.exceptions import ConflictError
from app.models import User
from app.schemas.api_response import ApiResponse, ok_response
from app.schemas.author import AuthorProfileUpdateRequest
from app.schemas.serializers import serialize_author
from app.services.author_service import update_author
from app.services.setup_service import get_site_settings

router = APIRouter(prefix="/api/v1/author", tags=["api-v1-author"])


@router.get("", response_model=ApiResponse, summary="获取作者资料")
def get_author_profile(db: Session = Depends(get_db)) -> JSONResponse:
    settings = get_site_settings(db)
    if settings is None:
        raise ConflictError("site_not_initialized", SITE_NOT_INITIALIZED)

    return ok_response(serialize_author(settings))


@router.post("", response_model=ApiResponse, summary="更新作者资料")
def update_author_profile(
    payload: AuthorProfileUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    settings = get_site_settings(db)
    if settings is None:
        raise ConflictError("site_not_initialized", SITE_NOT_INITIALIZED)

    settings = update_author(
        db, settings, name=payload.name, bio=payload.bio, email=payload.email, avatar=payload.avatar, link=payload.link
    )
    return ok_response(serialize_author(settings))
