from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import UploadFile

from app.core.config import settings


async def save_upload(file: UploadFile) -> str:
    ext = Path(file.filename or "file").suffix.lower()
    filename = f"{uuid4().hex}{ext}"

    data = await file.read()

    url = (
        f"{settings.supabase_url}"
        f"/storage/v1/object/"
        f"{settings.supabase_bucket}/{filename}"
    )

    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
        "Content-Type": file.content_type or "application/octet-stream",
        "x-upsert": "true",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            content=data,
            headers=headers,
        )

    if response.status_code >= 400:
        raise RuntimeError(
            f"Supabase upload failed: {response.status_code} {response.text}"
        )

    return (
        f"{settings.supabase_url}"
        f"/storage/v1/object/public/"
        f"{settings.supabase_bucket}/{filename}"
    )