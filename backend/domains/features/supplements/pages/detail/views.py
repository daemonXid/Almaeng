"""
📦 Product Detail Views

MFDS Data Display + Real-time Naver Price Lookup (HTMX)
"""

from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from ...logic.parser import extract_ingredients
from ...models import MFDSHealthFood
from ....prices.integrations.naver import NaverCrawler


def product_detail(request: HttpRequest, product_id: int) -> HttpResponse:
    """제품 상세 페이지 (SSR)"""
    product = get_object_or_404(MFDSHealthFood, id=product_id)
    
    # Simple Ingredient Parsing for Display
    parsed_ingredients = extract_ingredients(product.raw_materials)
    
    # Wishlist status
    in_wishlist = False
    if request.user.is_authenticated:
        from ...features.wishlist.interface import is_in_wishlist
        in_wishlist = is_in_wishlist(request.user.id, product_id)

    return render(
        request,
        "supplements/pages/detail/detail_page.html",
        {
            "product": product,
            "parsed_ingredients": parsed_ingredients,
            "page_title": f"{product.product_name} | ALMAENG",
            "in_wishlist": in_wishlist,
        },
    )


async def product_prices(request: HttpRequest, product_id: int) -> HttpResponse:
    """HTMX: 실시간 가격 조회 (Naver API)"""
    try:
        product = await MFDSHealthFood.objects.aget(id=product_id)
        
        # Crawler Orchestrator would be better, but direct use for MVP is fine
        crawler = NaverCrawler()
        
        # Search query: "Company Name Product Name"
        search_query = f"{product.company_name} {product.product_name}"
        result = await crawler.search(search_query)
        
        return render(
            request,
            "supplements/pages/detail/_price_list.html",
            {"prices": result, "product": product},
        )
    except Exception as e:
        # Error handling (e.g., API limit, network)
        return HttpResponse(
            f'<div class="text-red-500 text-sm p-4 text-center">가격 정보를 불러오는데 실패했습니다.<br><span class="text-xs text-gray-400">{str(e)}</span></div>'
        )
