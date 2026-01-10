"""
🛒 Cart URL Configuration
"""

from django.urls import path

from .pages.cart.views import add_to_cart, cart_count, cart_page, remove_from_cart, update_cart_item

app_name = "cart"

urlpatterns = [
    path("", cart_page, name="cart"),
    path("add/", add_to_cart, name="add"),
    path("update/<int:item_id>/", update_cart_item, name="update"),
    path("remove/<int:item_id>/", remove_from_cart, name="remove"),
    path("htmx/count/", cart_count, name="count"),
]
