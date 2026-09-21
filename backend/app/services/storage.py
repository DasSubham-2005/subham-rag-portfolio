from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import UploadFile

from app.core.config import settings


def _storage_headers():
    key = settings.supabase_service_role_key

    return {
        "Authorization": f"Bearer {key}",
        "apikey": key,
    }


async def save_upload(file: UploadFile) -> str:
    """
    Upload file to Supabase Storage and return its public URL.
    """

    ext = Path(file.filename or "file").suffix.lower()
    filename = f"{uuid4().hex}{ext}"

    data = await file.read()

    url = (
        f"{settings.supabase_url}"
        f"/storage/v1/object/"
        f"{settings.supabase_bucket}/"
        f"{filename}"
    )

    headers = {
        **_storage_headers(),
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
            f"Supabase upload failed: "
            f"{response.status_code} {response.text}"
        )

    return (
        f"{settings.supabase_url}"
        f"/storage/v1/object/public/"
        f"{settings.supabase_bucket}/"
        f"{filename}"
    )


async def delete_upload(file_url: str) -> bool:
    """
    Delete a previously uploaded file from Supabase Storage.
    """

    if not file_url:
        return False

    filename = file_url.rstrip("/").split("/")[-1]

    if not filename:
        return False

    url = (
        f"{settings.supabase_url}"
        f"/storage/v1/object/"
        f"{settings.supabase_bucket}/"
        f"{filename}"
    )

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.delete(
            url,
            headers=_storage_headers(),
        )

    if response.status_code in (200, 204):
        return True

    if response.status_code == 404:
        return False

    raise RuntimeError(
        f"Supabase delete failed: "
        f"{response.status_code} {response.text}"
    )