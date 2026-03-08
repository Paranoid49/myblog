from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.auth_service import authenticate_user
from app.services.setup_service import is_initialized

router = APIRouter(prefix="/admin", tags=["admin-auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    if not is_initialized(db):
        return RedirectResponse(url="/setup", status_code=302)
    return templates.TemplateResponse(request, "admin/login.html", {"error": None})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if not is_initialized(db):
        return RedirectResponse(url="/setup", status_code=status.HTTP_302_FOUND)

    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"error": "用户名或密码错误"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/admin/posts", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
