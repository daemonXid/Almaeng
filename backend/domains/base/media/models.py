"""
📁 Media Models
"""

import os
import uuid

from django.conf import settings
from django.db import models


def media_upload_path(instance, filename):
    """Generate unique upload path for media files."""
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    # Organize by year/month
    from django.utils import timezone

    now = timezone.now()
    return f"media/{now.year}/{now.month:02d}/{unique_name}"


class MediaFile(models.Model):
    """Uploaded media file with metadata."""

    class FileType(models.TextChoices):
        IMAGE = "image", "🖼️ Image"
        VIDEO = "video", "🎬 Video"
        AUDIO = "audio", "🎵 Audio"
        DOCUMENT = "document", "📄 Document"
        OTHER = "other", "📎 Other"

    file = models.FileField(upload_to=media_upload_path)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.OTHER,
    )
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0, help_text="Size in bytes")

    # Image-specific
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    # Metadata
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )
    alt_text = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["file_type", "-created_at"]),
            models.Index(fields=["uploaded_by", "-created_at"]),
        ]
        verbose_name = "Media File"
        verbose_name_plural = "Media Files"

    def __str__(self):
        return self.original_filename

    @property
    def url(self) -> str:
        """Get the file URL."""
        return self.file.url if self.file else ""

    @property
    def is_image(self) -> bool:
        """Check if file is an image."""
        return self.file_type == self.FileType.IMAGE
