"""
🌐 Index Page - Wishlist Domain

HTMX-friendly views that return HTML fragments.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    """Main page for wishlist."""
    return render(request, "wishlist/pages/index/index.html", {})
