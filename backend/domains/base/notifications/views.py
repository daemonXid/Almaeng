"""
🔔 Notification Views
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .interface import get_recent_notifications, get_unread_count
from .interface import mark_all_read as mark_all_read_service
from .models import Notification


@login_required
def notification_list(request: HttpRequest) -> HttpResponse:
    """알림 목록 페이지"""
    notifications = get_recent_notifications(request.user, limit=50)
    unread_count = get_unread_count(request.user)

    return render(
        request,
        "notifications/list.html",
        {
            "page_title": "알림 | ALMAENG",
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def notification_dropdown(request: HttpRequest) -> HttpResponse:
    """HTMX: 알림 드롭다운 (헤더용)"""
    notifications = get_recent_notifications(request.user, limit=5)
    unread_count = get_unread_count(request.user)

    return render(
        request,
        "notifications/_dropdown.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def mark_read(request: HttpRequest, notification_id: int) -> HttpResponse:
    """HTMX: 알림 읽음 처리"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()

    # Return updated notification item
    return render(
        request,
        "notifications/_item.html",
        {"notification": notification},
    )


@login_required
def mark_all_read(request: HttpRequest) -> HttpResponse:
    """HTMX: 모든 알림 읽음 처리"""
    count = mark_all_read_service(request.user)
    unread_count = get_unread_count(request.user)

    return render(
        request,
        "notifications/_dropdown.html",
        {
            "notifications": get_recent_notifications(request.user, limit=5),
            "unread_count": unread_count,
            "marked_count": count,
        },
    )
