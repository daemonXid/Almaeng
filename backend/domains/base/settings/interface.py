"""
⚙️ Site Settings - Public Interface

Import from here only:
    from domains.base.settings.interface import get_settings, is_maintenance_mode
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SiteSettings


def get_settings() -> "SiteSettings":
    """
    Get the current site settings.

    Returns:
        SiteSettings singleton instance
    """
    from .models import SiteSettings

    return SiteSettings.get()


def is_maintenance_mode() -> bool:
    """Check if maintenance mode is enabled."""
    return get_settings().maintenance_mode


def is_registration_allowed() -> bool:
    """Check if new user registration is allowed."""
    return get_settings().allow_registration


def is_ai_enabled() -> bool:
    """Check if AI features are enabled."""
    return get_settings().enable_ai_features


def get_site_name() -> str:
    """Get the site display name."""
    return get_settings().site_name


def get_meta_defaults() -> dict:
    """
    Get default SEO meta values.

    Returns:
        dict with title, description, keywords
    """
    settings = get_settings()
    return {
        "title": settings.meta_title,
        "description": settings.meta_description,
        "keywords": settings.meta_keywords,
    }


__all__ = [
    "get_meta_defaults",
    "get_settings",
    "get_site_name",
    "is_ai_enabled",
    "is_maintenance_mode",
    "is_registration_allowed",
]
