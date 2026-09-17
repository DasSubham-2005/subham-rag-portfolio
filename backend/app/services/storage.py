from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from app.core.config import settings

ROOT = Path(__file__).resolve().parents[2]
UPLOADS = ROOT / settings.upload_dir
UPLOADS.mkdir(parents=True, exist_ok=True)

async def save_upload(file: UploadFile) -> str:
    ext = Path(file.filename or "file").suffix.lower()
    name = f"{uuid4().hex}{ext}"
    path = UPLOADS / name
    data = await file.read()
    path.write_bytes(data)
    return f"/uploads/{name}"
