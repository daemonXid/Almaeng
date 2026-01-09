"""
😈 DAEMON Module - Django App Configuration

This is the core module for DAEMON-ONE template.
All base models, events, and configuration patterns live here.
"""

from django.apps import AppConfig


class DaemonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.base.core"
    verbose_name = "😈 Core (Base Module)"

    def ready(self):
        """Import receivers to register signal handlers."""
        # Import receivers here when you have them
        # from . import receivers
        pass
