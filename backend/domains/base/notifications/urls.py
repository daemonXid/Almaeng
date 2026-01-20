"""
🔔 Notifications URL Configuration
"""

from django.urls import path

from .views import (
    notification_list,
    notification_dropdown,
    mark_read,
    mark_all_read,
)

app_name = "notifications"

urlpatterns = [
    # Pages
    path("", notification_list, name="list"),
    # HTMX Partials
    path("htmx/dropdown/", notification_dropdown, name="dropdown"),
    path("htmx/mark-read/<int:notification_id>/", mark_read, name="mark_read"),
    path("htmx/mark-all-read/", mark_all_read, name="mark_all_read"),
]
