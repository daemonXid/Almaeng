"""
💊 Supplements URL Configuration
"""

from django.urls import path

from .pages.compare.views import compare, compare_result
from .pages.detail.views import product_detail, product_prices
from .pages.ingredient_search.views import ingredient_search, ingredient_search_async
from .pages.search.views import search_direct
from .pages.upload.views import analyze_image, save_ocr_result, upload

app_name = "supplements"

urlpatterns = [
    # Pages
    path("search-direct/", search_direct, name="search_direct"),
    path("ingredient-search/", ingredient_search, name="ingredient_search"),
    path("<int:product_id>/", product_detail, name="detail"),
    path("compare/", compare, name="compare"),
    path("upload/", upload, name="upload"),
    # HTMX Partials
    path("htmx/ingredient-search/", ingredient_search_async, name="ingredient_search_async"),
    path("htmx/compare/", compare_result, name="compare_result"),
    path("htmx/<int:product_id>/prices/", product_prices, name="prices"),
    path("api/analyze/", analyze_image, name="analyze_image"),
    path("api/save/", save_ocr_result, name="save_ocr"),
]
