"""
💳 Billing URL Configuration

PRD v2: 결제 페이지 라우팅
"""

from django.urls import path

from .pages.checkout.views import checkout_page, payment_success, payment_fail

app_name = "billing"

urlpatterns = [
    path("checkout/", checkout_page, name="checkout"),
    path("success/", payment_success, name="success"),
    path("fail/", payment_fail, name="fail"),
]
