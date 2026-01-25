"""
🔍 Search Page Views

자연어 검색 페이지.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ...logic.services import search_products
from ...state.interface import save_search_history


def search_page(request: HttpRequest) -> HttpResponse:
    """
    검색 페이지
    
    자연어 질문을 받아 상품 검색 결과를 표시.
    """
    query = request.GET.get("q", "").strip()

    if not query:
        return render(
            request,
            "pages/search/search.html",
            {
                "page_title": "AI 쇼핑 도우미 | 검색",
            },
        )

    # 검색 실행 (async wrapper)
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    result = loop.run_until_complete(search_products(query))

    # 검색 히스토리 저장 (로그인 사용자)
    if request.user.is_authenticated:
        save_search_history(
            user_id=request.user.id,
            query=query,
            keywords=result.keywords,
            category=result.products[0].platform if result.products else "",
        )

    return render(
        request,
        "pages/search/results.html",
        {
            "page_title": f'"{query}" 검색 결과',
            "result": result,
        },
    )
