"""
💳 Payments URL Configuration
"""

from django.urls import path

from .pages.checkout.views import checkout_page, payment_confirm, payment_fail, payment_success

app_name = "payments"

urlpatterns = [
    path("checkout/", checkout_page, name="checkout"),
    path("confirm/", payment_confirm, name="confirm"),
    path("success/", payment_success, name="success"),
    path("fail/", payment_fail, name="fail"),
]
