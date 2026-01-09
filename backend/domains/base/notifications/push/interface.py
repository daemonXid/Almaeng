"""
🔔 Push Module Interface - Public API

Usage:
    from domains.base.notifications.push.interface import send_push

    send_push(
        user_id=1,
        title="New Message",
        body="You have a new notification",
    )

Note:
    Requires web-push library: uv add pywebpush
    Requires VAPID keys in settings
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PushResult:
    """Result of push notification operation."""

    success: bool
    sent_count: int = 0
    error: str | None = None


def send_push(
    user_id: int,
    title: str,
    body: str,
    url: str | None = None,
    icon: str | None = None,
) -> PushResult:
    """
    Send a push notification to a user.

    Args:
        user_id: Target user ID
        title: Notification title
        body: Notification body
        url: URL to open on click
        icon: Icon URL

    Returns:
        PushResult with success status
    """
    # TODO: Implement when pywebpush is added
    logger.info(f"Push notification to user {user_id}: {title}")
    return PushResult(success=True, sent_count=1)


__all__ = ["PushResult", "send_push"]
