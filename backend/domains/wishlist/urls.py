"""
🔗 URL Configuration - Wishlist Domain
"""

from django.urls import path

from .pages.index import views

app_name = "wishlist"

urlpatterns = [
    path("", views.index, name="index"),
    path("toggle/", views.toggle, name="toggle"),
]
