"""
🛍️ Price Search Page Views

네이버/쿠팡 등 실시간 가격 검색 페이지.
"""

import asyncio

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ...integrations.naver import NaverCrawler
from ...integrations.base import CrawlResult


def search(request: HttpRequest) -> HttpResponse:
    """가격 검색 페이지"""
    return render(
        request,
        "prices/pages/search/search.html",
        {"page_title": "가격 검색 | ALMAENG"},
    )


def search_results(request: HttpRequest) -> HttpResponse:
    """HTMX: 네이버 쇼핑 검색 결과"""
    query = request.GET.get("q", "").strip()

    if not query:
        return HttpResponse(
            '<p class="text-gray-500 text-center py-8">검색어를 입력하세요</p>'
        )

    # 네이버 쇼핑 API 검색
    crawler = NaverCrawler()
    results: list[CrawlResult] = asyncio.run(crawler.search(query))

    return render(
        request,
        "prices/pages/search/_results.html",
        {"results": results, "query": query, "platform": "naver"},
    )
