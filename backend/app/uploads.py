"""Safe handling of user-uploaded images."""
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# Leading bytes ("magic numbers") for each allowed format. The extension alone is user-controlled.
_SIGNATURES = (
    (b"\x89PNG\r\n\x1a\n", {"png"}),
    (b"\xff\xd8\xff", {"jpg", "jpeg"}),
    (b"GIF87a", {"gif"}),
    (b"GIF89a", {"gif"}),
)


def _matches_signature(head: bytes, ext: str) -> bool:
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ext == "webp"
    return any(head.startswith(sig) and ext in exts for sig, exts in _SIGNATURES)


def save_image(file: FileStorage, subfolder: str) -> str | None:
    """Validate and store an uploaded image.

    Returns the path relative to the server root (e.g. ``uploads/photos/<uuid>.png``),
    or ``None`` if the file is not an allowed image. The original filename is never used
    on disk, which rules out path traversal and name collisions.
    """
    if not file or not file.filename or "." not in file.filename:
        return None
    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None

    head = file.stream.read(16)
    file.stream.seek(0)
    if not _matches_signature(head, ext):
        return None

    target_dir = Path(current_app.config["UPLOAD_FOLDER"]) / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(target_dir / filename)
    return f"uploads/{subfolder}/{filename}"
