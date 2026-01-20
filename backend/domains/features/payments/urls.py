"""
💳 Payments URL Configuration
"""

from django.urls import path

from .pages.checkout.views import checkout_page, payment_confirm, payment_fail, payment_success
from .pages.history.views import order_detail, order_history

app_name = "payments"

urlpatterns = [
    # Checkout
    path("checkout/", checkout_page, name="checkout"),
    path("confirm/", payment_confirm, name="confirm"),
    path("success/", payment_success, name="success"),
    path("fail/", payment_fail, name="fail"),
    # Order History
    path("orders/", order_history, name="orders"),
    path("orders/<uuid:order_id>/", order_detail, name="order_detail"),
]
