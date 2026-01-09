"""
🔔 Notifications Interface

Public API for notification system.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    from .models import Notification

    User = get_user_model()


def notify_user(
    user: "User",
    title: str,
    message: str = "",
    notification_type: str = "info",
    link: str = "",
) -> "Notification":
    """
    Send a notification to a user.

    Args:
        user: Target user
        title: Notification title
        message: Optional message body
        notification_type: info, success, warning, error
        link: Optional URL to navigate to

    Returns:
        Created Notification instance
    """
    from .models import Notification

    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )


def get_unread_count(user: "User") -> int:
    """Get count of unread notifications for user."""
    from .models import Notification

    return Notification.objects.filter(user=user, is_read=False).count()


def get_recent_notifications(user: "User", limit: int = 10):
    """Get recent notifications for user."""
    from .models import Notification

    return Notification.objects.filter(user=user)[:limit]


def mark_all_read(user: "User") -> int:
    """Mark all notifications as read for user."""
    from django.utils import timezone

    from .models import Notification

    return Notification.objects.filter(user=user, is_read=False).update(is_read=True, read_at=timezone.now())


__all__ = [
    "get_recent_notifications",
    "get_unread_count",
    "mark_all_read",
    "notify_user",
]
