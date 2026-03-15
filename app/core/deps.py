from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.error_codes import UNAUTHORIZED
from app.models import User
from app.schemas.api_response import build_error_detail


UNAUTHORIZED_DETAIL = build_error_detail("unauthorized", UNAUTHORIZED)


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_DETAIL)

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_DETAIL)

    return user
