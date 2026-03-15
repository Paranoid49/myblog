from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin
from app.core.error_codes import IMAGE_TOO_LARGE, UNSUPPORTED_IMAGE_TYPE
from app.core.hook_bus import hook_bus
from app.models import User
from app.schemas.api_response import ApiResponse, error_response, ok_response
from app.utils.text import slugify

router = APIRouter(prefix="/api/v1", tags=["api-v1-media"])

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "static" / "uploads"
IMAGE_MAX_BYTES = 5 * 1024 * 1024
IMAGE_EXTENSION_BY_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
ALLOWED_IMAGE_TYPES = set(IMAGE_EXTENSION_BY_TYPE)
IMAGE_RULES = {
    "max_bytes": IMAGE_MAX_BYTES,
    "extension_by_type": IMAGE_EXTENSION_BY_TYPE,
}


@router.post("/admin/media/images", response_model=ApiResponse)
async def upload_image_api(
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        return error_response("unsupported_image_type", status.HTTP_400_BAD_REQUEST, UNSUPPORTED_IMAGE_TYPE)

    content = await file.read()
    if len(content) > IMAGE_MAX_BYTES:
        return error_response("image_too_large", status.HTTP_400_BAD_REQUEST, IMAGE_TOO_LARGE)

    ext = IMAGE_EXTENSION_BY_TYPE.get(content_type, ".img")
    filename = f"{slugify(Path(file.filename or 'image').stem)}-{len(content)}{ext}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / filename
    save_path.write_bytes(content)

    url = f"/static/uploads/{filename}"
    # 媒体模块只有单一上传接口，hook 触发就地保留，不单独建 service
    hook_bus.emit("media.image_uploaded", {"key": filename, "url": url, "content_type": content_type})
    return ok_response(
        {
            "url": url,
            "key": filename,
            "size": len(content),
            "content_type": content_type,
        },
        status_code=status.HTTP_201_CREATED,
    )
