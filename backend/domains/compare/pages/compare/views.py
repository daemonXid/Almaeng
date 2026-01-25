"""
⚖️ Compare Page Views

가격 비교 페이지.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def compare_page(request: HttpRequest) -> HttpResponse:
    """가격 비교 페이지"""
    return render(
        request,
        "pages/compare/compare.html",
        {
            "page_title": "가격 비교 | AI 쇼핑 도우미",
        },
    )
