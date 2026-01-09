from django.apps import AppConfig


class GenaiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.ai.service.providers"
    label = "ai_providers"
    verbose_name = "🤖 AI Providers"
