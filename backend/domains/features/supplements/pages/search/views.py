"""
🔍 Search Page Views

영양제 검색 페이지와 HTMX 검색 결과 파셜.
"""

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ...models import MFDSHealthFood


def search(request: HttpRequest) -> HttpResponse:
    """영양제 검색 페이지"""
    q = request.GET.get("q", "")
    return render(
        request,
        "supplements/pages/search/search.html",
        {
            "page_title": "영양제 검색 | ALMAENG",
            "initial_query": q,
        },
    )


def search_results(request: HttpRequest) -> HttpResponse:
    """HTMX: 검색 결과 파셜"""
    query = request.GET.get("q", "").strip()

    if not query:
        return HttpResponse('<p class="text-gray-500 text-center py-8">검색어를 입력하세요</p>')

    supplements = MFDSHealthFood.objects.filter(
        Q(product_name__icontains=query) | 
        Q(company_name__icontains=query)
    ).order_by("-synced_at")[:20]

    return render(
        request,
        "supplements/pages/search/_results.html",
        {"supplements": supplements, "query": query},
    )
