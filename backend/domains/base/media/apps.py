from django.apps import AppConfig


class MediaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.base.media"
    label = "media_files"  # Avoid collision with Django's media
    verbose_name = "📁 Media Files"
