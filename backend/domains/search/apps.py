"""
🔍 Search App Config
"""

from django.apps import AppConfig


class SearchConfig(AppConfig):
    """Search Domain Configuration"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.search"
    verbose_name = "Search"
