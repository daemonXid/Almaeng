"""
📦 Product Detail Views

Supplement Model Display + Real-time Naver Price Lookup (HTMX) + Similar Products Comparison
"""

from decimal import Decimal
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from ...logic.parser import extract_ingredients, extract_nutrient_content, calculate_unit_cost, TARGET_NUTRIENTS
from ...logic.sets import calculate_value_metrics
from ...services import find_similar_supplements
from django.db.models import Q
from ...models import Supplement, Ingredient

def product_detail(request: HttpRequest, product_id: int) -> HttpResponse:
    """제품 상세 페이지 (SSR)"""
    # 1. Supplement 모델 사용 (없으면 404)
    try:
        product = Supplement.objects.prefetch_related("ingredients").get(id=product_id)
    except Supplement.DoesNotExist:
        return render(request, "404.html", status=404)
    
    # 2. Wishlist status
    in_wishlist = False
    if request.user.is_authenticated:
        from domains.features.wishlist.interface import is_in_wishlist
        in_wishlist = is_in_wishlist(request.user.id, product_id)

    # 3. 동일 성분 함량 비교 분석 제품 추천 (성분 기반)
    from ...conf import settings as supplements_settings
    
    SIMILAR_PRODUCTS_LIMIT = supplements_settings.DEFAULT_SEARCH_LIMIT // 5  # 4개
    
    similar_by_ingredients = find_similar_supplements(product_id, min_match_percent=50.0)[:SIMILAR_PRODUCTS_LIMIT]

    # 4. Fallback: Same Brand or Random
    if not similar_by_ingredients:
        similar_products = Supplement.objects.filter(brand=product.brand).exclude(id=product_id)[:SIMILAR_PRODUCTS_LIMIT]
        if not similar_products:
            similar_products = Supplement.objects.exclude(id=product_id).order_by("?")[:SIMILAR_PRODUCTS_LIMIT]
    else:
        # Convert to Supplement objects
        similar_ids = [s["supplement_id"] for s in similar_by_ingredients]
        similar_products = Supplement.objects.filter(id__in=similar_ids)
        # Preserve order
        similar_products_dict = {p.id: p for p in similar_products}
        similar_products = [similar_products_dict[sid] for sid in similar_ids if sid in similar_products_dict]

    # 5. Price History (최저가 확인) - interface.py를 통해
    from domains.features.prices.interface import get_lowest_price_record
    lowest_price = get_lowest_price_record(product.id)

    return render(
        request,
        "supplements/pages/detail/detail_page.html",
        {
            "product": product,
            "page_title": f"{product.name} | ALMAENG",
            "in_wishlist": in_wishlist,
            "similar_products": similar_products,
            "similar_by_ingredients": similar_by_ingredients,
            "lowest_price": lowest_price,
        },
    )


async def product_prices(request: HttpRequest, product_id: int) -> HttpResponse:
    """HTMX: 실시간 가격 조회 (Naver API) - Top 4만 표시 (캐싱 적용)"""
    from django.core.cache import cache
    
    try:
        
        # 캐시 키 생성
        cache_key = f"product_prices_{product_id}"
        
        # 캐시에서 가격 정보 확인 (1시간 TTL)
        cached_result = cache.get(cache_key)
        if cached_result:
            from ....prices.integrations.base import CrawlResult
            
            # 캐시된 데이터를 CrawlResult 객체로 변환
            cached_prices = cached_result.get("prices", [])
            top_prices = [
                CrawlResult(
                    product_name=p.get("product_name", ""),
                    price=Decimal(str(p.get("price", 0))),
                    url=p.get("url", ""),
                    image_url=p.get("image_url", ""),
                    platform=p.get("platform", "naver"),
                    is_in_stock=True,
                )
                for p in cached_prices[:prices_settings.DEFAULT_PRICE_SEARCH_LIMIT]
            ]
            value_metrics = cached_result.get("value_metrics")
            cached_product_id = cached_result.get("product_id")
            
            if cached_product_id and top_prices:
                product = await Supplement.objects.select_related().aget(id=cached_product_id)
                return render(
                    request,
                    "supplements/pages/detail/_price_list.html",
                    {
                        "prices": top_prices,
                        "product": product,
                        "value_metrics": value_metrics,
                    },
                )
        
        # 캐시 미스 - API 호출
        product = await Supplement.objects.select_related().aget(id=product_id)
        
        # 네이버 쇼핑 가격 검색 (interface.py를 통한 접근)
        from domains.features.prices.interface import search_naver_prices
        
        # Search query strategy: "{Brand} {Product Name}"
        search_query = f"{product.brand} {product.name}"
        
        from domains.features.prices.conf import settings as prices_settings
        
        result = await search_naver_prices(search_query, limit=prices_settings.DEFAULT_PRICE_SEARCH_LIMIT)
        
        # Fallback: Product name only
        if not result:
            result = await search_naver_prices(product.name, limit=prices_settings.DEFAULT_PRICE_SEARCH_LIMIT)
        
        top_prices = result
        
        # Value Metrics 계산 (첫 번째 가격 기준) - 개선된 가성비 계산
        value_metrics = None
        if top_prices and top_prices[0].price:
            from ...services import calculate_price_per_unit
            
            price_info = calculate_price_per_unit(
                product,
                Decimal(str(top_prices[0].price))
            )
            
            if price_info:
                value_metrics = {
                    "primary_ingredient": price_info["ingredient_name"],
                    "amount_per_serving": price_info["amount_per_serving"],
                    "unit": price_info["unit"],
                    "total_amount": price_info["total_amount"],
                    "unit_cost": price_info["price_per_unit"],
                    "price_per_serving": price_info["price_per_serving"],
                    "rank_label": "💰 가성비 분석",
                }
        
        # 캐시에 저장 (1시간 = 3600초)
        # CrawlResult를 딕셔너리로 변환하여 저장 (Decimal을 float로 변환)
        cache.set(cache_key, {
            "prices": [
                {
                    "product_name": r.product_name,
                    "price": float(r.price),  # Decimal을 float로 변환
                    "url": r.url,
                    "image_url": r.image_url,
                    "platform": r.platform,
                }
                for r in result
            ],
            "value_metrics": value_metrics,
            "product_id": product.id,
        }, timeout=prices_settings.PRICE_CACHE_TIMEOUT)

        return render(
            request,
            "supplements/pages/detail/_price_list.html",
            {
                "prices": top_prices,
                "product": product,
                "value_metrics": value_metrics,
            },
        )
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"product_prices exception: {e}", exc_info=True)
        return HttpResponse(
            f'<div class="text-red-500 text-sm p-4 text-center">가격 정보를 불러오는데 실패했습니다.<br><span class="text-xs text-gray-400">{str(e)}</span></div>'
        )

