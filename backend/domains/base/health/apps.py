from django.apps import AppConfig


class HealthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.base.health"
    label = "health"
    verbose_name = "🏥 Health Checks"
