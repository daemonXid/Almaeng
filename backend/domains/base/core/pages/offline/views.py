"""
🌐 Offline Page View
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def offline(request: HttpRequest) -> HttpResponse:
    """Offline fallback page for PWA."""
    return render(request, "core/pages/offline/offline.html")
