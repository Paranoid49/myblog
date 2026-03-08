from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.routes.admin_auth import router as admin_auth_router

app = FastAPI(title="myblog")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.include_router(admin_auth_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
