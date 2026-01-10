"""
💰 Prices URL Configuration
"""

from django.urls import path

from .pages.history.views import history, price_chart

app_name = "prices"

urlpatterns = [
    # Pages
    path("<int:supplement_id>/", history, name="history"),
    # HTMX Partials
    path("htmx/chart/<int:supplement_id>/", price_chart, name="chart"),
]
