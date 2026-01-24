"""
⚖️ Compare Page Views

성분 비교 페이지와 HTMX 비교 결과 파셜.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ...services import compare_supplements


def compare(request: HttpRequest) -> HttpResponse:
    """성분 비교 페이지 - 찜 목록만 사용"""
    wishlist_products = []
    if request.user.is_authenticated:
        from ...models import Supplement
        from domains.features.wishlist.interface import get_user_wishlist
        
        wishlist_items = get_user_wishlist(request.user.id)
        ids = [item.supplement_id for item in wishlist_items]
        wishlist_products = Supplement.objects.filter(id__in=ids)

    return render(
        request,
        "supplements/pages/compare/compare.html",
        {
            "page_title": "성분 비교 | ALMAENG",
            "wishlist_products": wishlist_products,
        },
    )


def compare_result(request: HttpRequest) -> HttpResponse:
    """HTMX: 비교 결과 파셜"""
    product_a_id = request.GET.get("product_a")
    product_b_id = request.GET.get("product_b")

    if not product_a_id or not product_b_id:
        return HttpResponse('<p class="text-gray-500 text-center py-8">두 제품을 선택하세요</p>')

    try:
        result = compare_supplements(int(product_a_id), int(product_b_id))
    except (ValueError, TypeError):
        return HttpResponse('<p class="text-red-500 text-center py-8">유효하지 않은 제품입니다</p>')

    if not result:
        return HttpResponse('<p class="text-red-500 text-center py-8">제품을 찾을 수 없습니다</p>')

    return render(
        request,
        "supplements/pages/compare/_result.html",
        {"result": result},
    )
