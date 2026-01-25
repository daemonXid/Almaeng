"""
⚖️ Compare App Config
"""

from django.apps import AppConfig


class CompareConfig(AppConfig):
    """Compare Domain Configuration"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.compare"
    verbose_name = "Compare"
