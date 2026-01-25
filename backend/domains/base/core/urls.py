"""
🌐 daemon URLs - HTMX Endpoints

This module defines URL patterns for the daemon module.
All HTMX endpoints are prefixed with /htmx/ for clarity.
"""

from django.urls import path

from .pages.home import views
from .pages.legal import views as legal_views
from .pages.offline import views as offline_views

app_name = "daemon"

urlpatterns = [
    # Page views
    path("", views.home, name="home"),
    path("landing/", views.landing, name="landing"),
    path("offline/", offline_views.offline, name="offline"),
    # Legal pages
    path("faq/", legal_views.faq, name="faq"),
    path("terms/", legal_views.terms, name="terms"),
    path("privacy/", legal_views.privacy, name="privacy"),
]
