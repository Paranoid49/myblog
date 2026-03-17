import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_admin, require_csrf_header
from app.core.error_codes import IMAGE_TOO_LARGE, UNSUPPORTED_IMAGE_TYPE
from app.core.exceptions import AppError
from app.core.hook_bus import hook_bus
from app.models import User
from app.schemas.api_response import ApiResponse, ok_response

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

MAGIC_BYTES_MAP = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
}


def detect_image_type(content: bytes) -> str | None:
    """通过文件头 magic bytes 检测真实图片类型"""
    for magic, mime in MAGIC_BYTES_MAP.items():
        if content[: len(magic)] == magic:
            return mime
    # WebP 格式：RIFF....WEBP
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    return None


IMAGE_RULES = {
    "max_bytes": IMAGE_MAX_BYTES,
    "extension_by_type": IMAGE_EXTENSION_BY_TYPE,
}


@router.post("/admin/media/images", response_model=ApiResponse, summary="上传图片")
async def upload_image_api(
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> JSONResponse:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise AppError("unsupported_image_type", UNSUPPORTED_IMAGE_TYPE, 400)

    # 分块读取并校验大小，避免一次性加载大文件到内存
    chunks = []
    total_size = 0
    while True:
        chunk = await file.read(8192)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > IMAGE_MAX_BYTES:
            raise AppError("image_too_large", IMAGE_TOO_LARGE, 400)
        chunks.append(chunk)
    content = b"".join(chunks)

    # Magic bytes 校验：验证文件内容与声明的类型一致
    detected_type = detect_image_type(content)
    if detected_type is None or detected_type not in ALLOWED_IMAGE_TYPES:
        raise AppError("unsupported_image_type", UNSUPPORTED_IMAGE_TYPE, 400)

    # 声明类型与检测类型一致性校验
    if detected_type != content_type:
        raise AppError("unsupported_image_type", UNSUPPORTED_IMAGE_TYPE, 400)

    ext = IMAGE_EXTENSION_BY_TYPE.get(content_type, ".img")
    # 使用 UUID 生成文件名，避免原始文件名泄露信息或引发路径注入
    filename = f"{uuid.uuid4().hex}{ext}"

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
