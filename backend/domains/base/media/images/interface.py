"""
🖼️ Images Module Interface - Public API

Usage:
    from domains.base.media.images.interface import optimize_image, create_thumbnail

    optimized = optimize_image(image_file, quality=80)
    thumbnail = create_thumbnail(image_file, size=(200, 200))
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO

logger = logging.getLogger(__name__)


@dataclass
class ImageResult:
    """Result of image processing operation."""

    success: bool
    data: bytes | None = None
    format: str | None = None
    width: int | None = None
    height: int | None = None
    error: str | None = None


def optimize_image(
    image_file: BinaryIO,
    quality: int = 85,
    max_size: tuple[int, int] | None = (1920, 1920),
    format: str = "webp",
) -> ImageResult:
    """
    Optimize an image for web usage.

    Args:
        image_file: Input image file
        quality: Output quality (1-100)
        max_size: Maximum dimensions (width, height)
        format: Output format (webp, jpeg, png)

    Returns:
        ImageResult with optimized image data
    """
    try:
        from PIL import Image

        img = Image.open(image_file)

        # Resize if needed
        if max_size:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Convert to RGB if needed for JPEG/WebP
        if img.mode in ("RGBA", "P") and format.lower() in ("jpeg", "jpg"):
            img = img.convert("RGB")

        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format=format.upper(), quality=quality, optimize=True)
        buffer.seek(0)

        return ImageResult(
            success=True,
            data=buffer.getvalue(),
            format=format,
            width=img.width,
            height=img.height,
        )

    except ImportError:
        logger.error("Pillow not installed. Run: uv add pillow")
        return ImageResult(success=False, error="Pillow not installed")
    except Exception as e:
        logger.error(f"Image optimization failed: {e}")
        return ImageResult(success=False, error=str(e))


def create_thumbnail(
    image_file: BinaryIO,
    size: tuple[int, int] = (200, 200),
    format: str = "webp",
) -> ImageResult:
    """
    Create a thumbnail from an image.

    Args:
        image_file: Input image file
        size: Thumbnail dimensions (width, height)
        format: Output format

    Returns:
        ImageResult with thumbnail data
    """
    return optimize_image(image_file, quality=80, max_size=size, format=format)


__all__ = ["ImageResult", "create_thumbnail", "optimize_image"]
