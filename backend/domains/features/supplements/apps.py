from django.apps import AppConfig


class SupplementsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.features.supplements"
    label = "supplements"
    verbose_name = "💊 Supplements"
