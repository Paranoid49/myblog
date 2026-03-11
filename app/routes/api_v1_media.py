from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin
from app.core.hook_bus import hook_bus
from app.models import User
from app.routes.api_v1_posts import ApiResponse, _error, _ok
from app.services.post_service import slugify

router = APIRouter(prefix="/api/v1", tags=["api-v1-media"])

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "static" / "uploads"
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.post("/admin/media/images", response_model=ApiResponse)
async def upload_image_api(
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        return _error("unsupported_image_type", status.HTTP_400_BAD_REQUEST, 1411)

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        return _error("image_too_large", status.HTTP_400_BAD_REQUEST, 1412)

    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    ext = ext_map.get(content_type, ".img")
    filename = f"{slugify(Path(file.filename or 'image').stem)}-{len(content)}{ext}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / filename
    save_path.write_bytes(content)

    url = f"/static/uploads/{filename}"
    hook_bus.emit("media.image_uploaded", {"key": filename, "url": url, "content_type": content_type})
    return _ok(
        {
            "url": url,
            "key": filename,
            "size": len(content),
            "content_type": content_type,
        },
        status_code=status.HTTP_201_CREATED,
    )
