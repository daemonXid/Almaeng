"""
🔔 Notifications Module

In-app and email notification system.

Features:
- In-app notifications with read/unread status
- Email notification integration
- Notification preferences per user
- Real-time updates via HTMX polling

Usage:
    from domains.base.notifications.interface import notify_user, get_unread_count

    notify_user(user, "Welcome!", notification_type="info")
    count = get_unread_count(user)
"""
