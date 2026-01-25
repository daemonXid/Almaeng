"""
💳 Billing App Config
"""

from django.apps import AppConfig


class BillingConfig(AppConfig):
    """Billing Domain Configuration"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.billing"
    verbose_name = "Billing"
