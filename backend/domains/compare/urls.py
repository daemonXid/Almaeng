"""
⚖️ Compare URL Configuration
"""

from django.urls import path

from .pages.compare.views import compare_page

app_name = "compare"

urlpatterns = [
    path("", compare_page, name="compare"),
]
