"""
💰 Prices URL Configuration
"""

from django.urls import path

from .pages.history.views import history, price_chart
from .pages.search.views import search, search_results

app_name = "prices"

urlpatterns = [
    # Pages
    path("search/", search, name="search"),
    path("<int:supplement_id>/", history, name="history"),
    # HTMX Partials
    path("htmx/search/", search_results, name="search_results"),
    path("htmx/chart/<int:supplement_id>/", price_chart, name="chart"),
]
