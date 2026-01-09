"""
🔔 Notification Models
"""

from django.conf import settings
from django.db import models


class Notification(models.Model):
    """In-app notification for users."""

    class Type(models.TextChoices):
        INFO = "info", "ℹ️ Info"
        SUCCESS = "success", "✅ Success"
        WARNING = "warning", "⚠️ Warning"
        ERROR = "error", "❌ Error"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.INFO,
    )
    link = models.URLField(blank=True, help_text="Optional link to navigate to")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "is_read"]),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone

        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
