"""
🔌 Integrations App Config
"""

from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    """Integrations Domain Configuration"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.integrations"
    verbose_name = "Integrations"
