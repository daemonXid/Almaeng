"""
🏥 Health Check URL Configuration

Endpoints:
- /health/         - Basic health status
- /health/ready/   - Readiness probe
- /health/live/    - Liveness probe
"""

from django.urls import path

from .pages.status import views

app_name = "health"

urlpatterns = [
    path("", views.health, name="health"),
    path("ready/", views.readiness, name="readiness"),
    path("live/", views.liveness, name="liveness"),
]
