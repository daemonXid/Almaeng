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
    return render(
        request,
        "supplements/pages/search/search.html",
        {
            "page_title": "영양제 검색 | ALMAENG",
        },
    )


def search_results(request: HttpRequest) -> HttpResponse:
    """HTMX: 검색 결과 파셜"""
    query = request.GET.get("q", "").strip()

    if not query:
        return HttpResponse('<p class="text-gray-500 text-center py-8">검색어를 입력하세요</p>')

    supplements = Supplement.objects.filter(Q(name__icontains=query) | Q(brand__icontains=query))[:20]

    return render(
        request,
        "supplements/pages/search/_results.html",
        {"supplements": supplements, "query": query},
    )
