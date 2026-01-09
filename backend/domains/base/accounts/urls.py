"""
🔗 Auth URL Patterns
"""

from django.urls import path

from .pages.profile import views

app_name = "auth"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
]
