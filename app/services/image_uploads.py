from __future__ import annotations

from pathlib import Path
from secrets import token_urlsafe

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_IMAGE_KINDS = {"logo", "cover"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
_READ_CHUNK_SIZE = 1024 * 1024


def validate_image_kind(kind: str) -> str:
    normalized = str(kind or "").strip().lower()
    if normalized not in ALLOWED_IMAGE_KINDS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image kind")
    return normalized


async def save_partner_image_upload(partner_id: int, kind: str, file: UploadFile) -> str:
    normalized_kind = validate_image_kind(kind)
    _validate_content_type(file.content_type)
    _validate_filename_extension(file.filename)
    content = await _read_upload_bytes(file)
    extension = _detect_image_extension(content)

    destination_dir = Path(settings.UPLOAD_DIR) / "partners" / str(partner_id)
    destination_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{normalized_kind}-{token_urlsafe(16)}.{extension}"
    destination_path = destination_dir / filename
    destination_path.write_bytes(content)

    public_prefix = settings.PUBLIC_UPLOADS_PATH.rstrip("/") or "/uploads"
    return f"{public_prefix}/partners/{partner_id}/{filename}"


def _validate_content_type(content_type: str | None) -> None:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image content type")


def _validate_filename_extension(filename: str | None) -> None:
    if not filename:
        return
    suffix = Path(filename).suffix.lower()
    if suffix and suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image extension")


async def _read_upload_bytes(file: UploadFile) -> bytes:
    chunks: list[bytes] = []
    size = 0
    while True:
        chunk = await file.read(_READ_CHUNK_SIZE)
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image file is too large")
        chunks.append(chunk)
    content = b"".join(chunks)
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image bytes")
    return content


def _detect_image_extension(content: bytes) -> str:
    if content.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "webp"
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image bytes")
