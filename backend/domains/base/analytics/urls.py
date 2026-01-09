"""
🔗 Analytics URL Patterns
"""

from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("database/", views.database_stats, name="database"),
    path("slow-queries/", views.slow_queries, name="slow_queries"),
]
