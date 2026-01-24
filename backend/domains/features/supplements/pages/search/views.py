"""
🔍 Search Page Views

영양제 검색 페이지와 HTMX 검색 결과 파셜.
"""

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ...models import Supplement


def search(request: HttpRequest) -> HttpResponse:
    """영양제 검색 페이지"""
    q = request.GET.get("q", "")
    return render(
        request,
        "supplements/pages/search/search.html",
        {
            "page_title": "영양제 검색 | ALMAENG",
            "initial_query": q,
            "popular_keywords": ["오메가3", "비타민C", "유산균", "마그네슘", "루테인", "밀크씨슬", "콜라겐"],
        },
    )


def search_results(request: HttpRequest) -> HttpResponse:
    """HTMX: 검색 결과 파셜"""
    query = request.GET.get("q", "").strip()

    if not query:
        return HttpResponse('<p class="text-gray-500 text-center py-8">검색어를 입력하세요</p>')

    supplements = Supplement.objects.filter(
        Q(name__icontains=query) | 
        Q(brand__icontains=query) |
        Q(benefits__icontains=query)  # JSONField text search might vary by DB, but standard text search works often
    ).order_by("-description")[:20]  # Prioritize items with AI description

    # For PostgreSQL JSONB, might need specific lookup, but plain text exact match isn't enough for JSON list. 
    # Simplify for now: filter by name/brand, sort by has_description.
    if not supplements.exists():
         supplements = Supplement.objects.filter(
            Q(name__icontains=query) | 
            Q(brand__icontains=query)
        ).order_by("-created_at")[:20]

    return render(
        request,
        "supplements/pages/search/_results.html",
        {"supplements": supplements, "query": query},
    )
