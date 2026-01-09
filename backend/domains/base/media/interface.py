"""
📁 Media Interface

Public API for media file management.
"""

import mimetypes
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from django.core.files.uploadedfile import UploadedFile

    from .models import MediaFile

    User = get_user_model()


def upload_file(
    file: "UploadedFile",
    user: "User | None" = None,
    alt_text: str = "",
    description: str = "",
) -> "MediaFile":
    """
    Upload a file and create MediaFile record.

    Args:
        file: Django uploaded file
        user: User uploading the file
        alt_text: Alt text for images
        description: Optional description

    Returns:
        Created MediaFile instance
    """
    from .models import MediaFile

    # Detect file type
    mime_type, _ = mimetypes.guess_type(file.name)
    file_type = _get_file_type(mime_type)

    # Get image dimensions if applicable
    width, height = None, None
    if file_type == "image":
        width, height = _get_image_dimensions(file)

    media = MediaFile.objects.create(
        file=file,
        original_filename=file.name,
        file_type=file_type,
        mime_type=mime_type or "",
        file_size=file.size,
        width=width,
        height=height,
        uploaded_by=user,
        alt_text=alt_text,
        description=description,
    )

    return media


def get_media_url(media: "MediaFile") -> str:
    """Get the URL for a media file."""
    return media.url


def get_user_files(user: "User", file_type: str | None = None, limit: int = 50):
    """Get files uploaded by a user."""
    from .models import MediaFile

    qs = MediaFile.objects.filter(uploaded_by=user)
    if file_type:
        qs = qs.filter(file_type=file_type)
    return qs[:limit]


def delete_file(media: "MediaFile") -> bool:
    """Delete a media file and its record."""
    try:
        media.file.delete(save=False)
        media.delete()
        return True
    except Exception:
        return False


def _get_file_type(mime_type: str | None) -> str:
    """Determine file type from MIME type."""
    if not mime_type:
        return "other"

    if mime_type.startswith("image/"):
        return "image"
    elif mime_type.startswith("video/"):
        return "video"
    elif mime_type.startswith("audio/"):
        return "audio"
    elif mime_type in ["application/pdf", "text/plain", "application/msword"]:
        return "document"
    return "other"


def _get_image_dimensions(file) -> tuple[int | None, int | None]:
    """Get image width and height."""
    try:
        from PIL import Image

        img = Image.open(file)
        width, height = img.size
        file.seek(0)  # Reset file pointer
        return width, height
    except Exception:
        return None, None


__all__ = [
    "delete_file",
    "get_media_url",
    "get_user_files",
    "upload_file",
]
