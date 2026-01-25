from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from ...logic.services import search_products
from ...state.interface import save_search_history


def search_page(request: HttpRequest) -> HttpResponse:
    """검색 페이지"""
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

    # 찜 목록 ID 가져오기 (로그인 사용자)
    wishlist_ids = set()
    if request.user.is_authenticated:
        from domains.wishlist.interface import get_user_wishlist

        wishlist_ids = {item.product_id for item in get_user_wishlist(request.user.id)}

    return render(
        request,
        "pages/search/results.html",
        {
            "page_title": f'"{query}" 검색 결과',
            "result": result,
            "wishlist_ids": wishlist_ids,
        },
    )


@login_required
def track_click(request: HttpRequest) -> HttpResponse:
    """상품 클릭 시 최근 본 상품에 저장하고 리다이렉트"""
    product_data = {
        "id": request.GET.get("id"),
        "name": request.GET.get("name"),
        "price": request.GET.get("price"),
        "image": request.GET.get("image"),
        "url": request.GET.get("url"),
    }

    if not product_data["url"]:
        return redirect("daemon:home")

    # 세션에서 최근 본 상품 목록 가져오기
    recent_products = request.session.get("recent_products", [])

    # 중복 제거 (이미 있으면 맨 앞으로)
    recent_products = [p for p in recent_products if p.get("id") != product_data["id"]]
    recent_products.insert(0, product_data)

    # 최대 10개까지만 유지
    request.session["recent_products"] = recent_products[:10]

    return redirect(product_data["url"])
