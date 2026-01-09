"""
⚙️ Module Configuration Pattern

Provides a way to have module-specific settings with defaults
that can be overridden from the global Django settings.

Usage in your module:

    # your_module/conf.py
    from domains.daemon.conf import ModuleSettings

    class YourModuleSettings(ModuleSettings):
        NAMESPACE = "YOUR_MODULE"

        DEFAULTS = {
            "TIMEOUT": 30,
            "MAX_RETRIES": 3,
            "API_KEY": None,
        }

    settings = YourModuleSettings()

    # your_module/services.py
    from .conf import settings

    def call_api():
        timeout = settings.TIMEOUT  # Gets 30 or overridden value

Override in Django settings:

    # config/settings.py
    YOUR_MODULE = {
        "TIMEOUT": 60,  # Override default
    }
"""

from typing import Any

from django.conf import settings as django_settings


class ModuleSettings:
    """
    Base class for module-specific settings.

    Subclass this and define:
    - NAMESPACE: str - The key in Django settings (e.g., "AI_CEREBRO")
    - DEFAULTS: dict - Default values for all settings
    """

    NAMESPACE: str = ""
    DEFAULTS: dict[str, Any] = {}

    def __init__(self):
        self._cached_attrs = set()

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)

        # Check if value is in DEFAULTS
        if name not in self.DEFAULTS:
            raise AttributeError(f"'{self.NAMESPACE}' has no setting '{name}'")

        # Try to get from Django settings first
        user_settings = getattr(django_settings, self.NAMESPACE, {})

        if name in user_settings:
            return user_settings[name]

        # Fall back to default
        return self.DEFAULTS[name]

    def as_dict(self) -> dict[str, Any]:
        """Get all settings as a dictionary."""
        result = dict(self.DEFAULTS)
        user_settings = getattr(django_settings, self.NAMESPACE, {})
        result.update(user_settings)
        return result


# =============================================================================
# 📦 DAEMON Module Settings
# =============================================================================


class DaemonSettings(ModuleSettings):
    """Settings for the DAEMON core module."""

    NAMESPACE = "DAEMON"

    DEFAULTS = {
        # Soft delete behavior
        "SOFT_DELETE_ENABLED": True,
        # Pagination
        "DEFAULT_PAGE_SIZE": 20,
        "MAX_PAGE_SIZE": 100,
        # Events
        "EMIT_EVENTS": True,
    }


daemon_settings = DaemonSettings()
