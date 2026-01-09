"""
🌐 Analytics Views

HTMX views for the admin dashboard.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .conf import settings
from .interface import (
    get_dashboard_stats,
    get_database_stats,
    get_slow_queries,
)


@staff_member_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Main analytics dashboard (admin only)."""
    stats = get_dashboard_stats()
    db_stats = get_database_stats()

    return render(
        request,
        "analytics/dashboard.html",
        {
            "stats": stats,
            "db_stats": db_stats,
            "refresh_interval": settings.REFRESH_INTERVAL,
        },
    )


@staff_member_required
def database_stats(request: HttpRequest) -> HttpResponse:
    """HTMX partial for database stats."""
    db_stats = get_database_stats()

    return render(
        request,
        "analytics/_database_stats.html",
        {"db_stats": db_stats},
    )


@staff_member_required
def slow_queries(request: HttpRequest) -> HttpResponse:
    """HTMX partial for slow queries."""
    queries = get_slow_queries()

    return render(
        request,
        "analytics/_slow_queries.html",
        {"queries": queries},
    )
