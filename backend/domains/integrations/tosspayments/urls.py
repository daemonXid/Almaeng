"""
💳 Toss Payments URL Configuration
"""

from django.urls import path

from .pages.webhook.views import toss_payments_webhook

app_name = "tosspayments"

urlpatterns = [
    path("webhook/", toss_payments_webhook, name="webhook"),
]
