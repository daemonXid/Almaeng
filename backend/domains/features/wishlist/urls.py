"""
❤️ Wishlist URL Configuration
"""

from django.urls import path

from .pages.wishlist.views import toggle_wishlist_item, wishlist_page

app_name = "wishlist"

urlpatterns = [
    path("", wishlist_page, name="list"),
    path("toggle/<int:supplement_id>/", toggle_wishlist_item, name="toggle"),
]
