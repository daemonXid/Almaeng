"""
💊 Supplements URL Configuration
"""

from django.urls import path

from .pages.compare.views import compare, compare_result
from .pages.detail.views import product_detail, product_prices
from .pages.search.views import search, search_results
from .pages.upload.views import analyze_image, upload

app_name = "supplements"

urlpatterns = [
    # Pages
    path("", search, name="search"),
    path("<int:product_id>/", product_detail, name="detail"),
    path("compare/", compare, name="compare"),
    path("upload/", upload, name="upload"),
    # HTMX Partials
    path("htmx/search/", search_results, name="search_results"),
    path("htmx/compare/", compare_result, name="compare_result"),
    path("htmx/<int:product_id>/prices/", product_prices, name="prices"),
    path("api/analyze/", analyze_image, name="analyze_image"),
]
