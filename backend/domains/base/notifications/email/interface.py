"""
📧 Email Module Interface - Public API

Usage:
    from domains.base.notifications.email.interface import send_email

    send_email(
        to="user@example.com",
        subject="Welcome!",
        template="welcome",
        context={"name": "John"},
    )
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@dataclass
class EmailResult:
    """Result of email sending operation."""

    success: bool
    message_id: str | None = None
    error: str | None = None


def send_email(
    to: str | list[str],
    subject: str,
    template: str | None = None,
    body: str | None = None,
    context: dict | None = None,
    from_email: str | None = None,
) -> EmailResult:
    """
    Send an email to one or more recipients.

    Args:
        to: Recipient email(s)
        subject: Email subject
        template: Template name (without extension)
        body: Plain text body (if no template)
        context: Context for template rendering
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)

    Returns:
        EmailResult with success status
    """
    if isinstance(to, str):
        to = [to]

    context = context or {}
    from_email = from_email or settings.DEFAULT_FROM_EMAIL

    try:
        if template:
            html_body = render_to_string(f"notifications/email/{template}.html", context)
            text_body = render_to_string(f"notifications/email/{template}.txt", context)
        else:
            html_body = None
            text_body = body or ""

        send_mail(
            subject=subject,
            message=text_body,
            from_email=from_email,
            recipient_list=to,
            html_message=html_body,
            fail_silently=False,
        )

        logger.info(f"Email sent to {to}: {subject}")
        return EmailResult(success=True)

    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return EmailResult(success=False, error=str(e))


__all__ = ["EmailResult", "send_email"]
