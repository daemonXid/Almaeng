"""
☁️ Storage Module Interface - Public API

Usage:
    from domains.base.media.storage.interface import upload_file, get_file_url

    url = upload_file(file, path="uploads/images/photo.jpg")
    signed_url = get_file_url(path, expires_in=3600)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import BinaryIO

from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


@dataclass
class StorageResult:
    """Result of storage operation."""

    success: bool
    path: str | None = None
    url: str | None = None
    size: int | None = None
    error: str | None = None


def upload_file(
    file: BinaryIO,
    path: str,
    public: bool = False,
) -> StorageResult:
    """
    Upload a file to storage.

    Args:
        file: File object to upload
        path: Storage path (e.g., "uploads/images/photo.jpg")
        public: Whether the file should be publicly accessible

    Returns:
        StorageResult with file path and URL
    """
    try:
        saved_path = default_storage.save(path, file)
        url = default_storage.url(saved_path) if public else None

        logger.info(f"File uploaded: {saved_path}")
        return StorageResult(
            success=True,
            path=saved_path,
            url=url,
        )

    except Exception as e:
        logger.error(f"File upload failed: {e}")
        return StorageResult(success=False, error=str(e))


def get_file_url(path: str, expires_in: int = 3600) -> str | None:
    """
    Get a URL for a stored file.

    Args:
        path: Storage path
        expires_in: URL expiration time in seconds (for signed URLs)

    Returns:
        File URL or None if not found
    """
    try:
        if default_storage.exists(path):
            return default_storage.url(path)
        return None
    except Exception as e:
        logger.error(f"Failed to get file URL: {e}")
        return None


def delete_file(path: str) -> bool:
    """
    Delete a file from storage.

    Args:
        path: Storage path

    Returns:
        True if deleted successfully
    """
    try:
        if default_storage.exists(path):
            default_storage.delete(path)
            logger.info(f"File deleted: {path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        return False


__all__ = ["StorageResult", "delete_file", "get_file_url", "upload_file"]
