"""
😈 Wishlist Domain - Django App Configuration
"""

from django.apps import AppConfig


class WishlistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.wishlist"
    verbose_name = "Wishlist"

    def ready(self):
        """Import receivers to register signal handlers."""
        try:
            from . import receivers  # noqa: F401
        except ImportError:
            pass
