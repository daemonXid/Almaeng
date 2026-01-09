from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.base.accounts"
    label = "daemon_auth"  # Avoid collision with django.contrib.auth
    verbose_name = "👤 Authentication"
