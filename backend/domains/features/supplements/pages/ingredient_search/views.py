"""
🔬 Ingredient-Based Search Views

성분명으로 영양제를 검색하고 가성비를 비교하는 페이지.
"""

from decimal import Decimal

from django.core.cache import cache
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ...conf import settings as supplements_settings
from ...models import Supplement
from ...services import compare_by_ingredient_price, search_by_ingredient
from domains.features.prices.conf import settings as prices_settings
from domains.features.prices.interface import search_naver_prices


def ingredient_search(request: HttpRequest) -> HttpResponse:
    """성분 기반 검색 페이지"""
    ingredient_name = request.GET.get("ingredient", "").strip()
    min_amount = request.GET.get("min_amount", "")
    max_amount = request.GET.get("max_amount", "")
    unit = request.GET.get("unit", "mg")
    sort_by = request.GET.get("sort", "value")  # value, price, amount
    
    results = []
    comparison_data = []
    
    if ingredient_name:
        # 성분명으로 검색
        supplements = search_by_ingredient(ingredient_name, limit=50)
        
        # 함량 범위 필터링
        if min_amount or max_amount:
            filtered_supplements = []
            for supplement in supplements:
                ingredient = supplement.ingredients.filter(
                    name__icontains=ingredient_name
                ).first()
                
                if ingredient:
                    # 단위 정규화 필요 시 여기서 처리
                    amount = float(ingredient.amount)
                    
                    if min_amount and amount < float(min_amount):
                        continue
                    if max_amount and amount > float(max_amount):
                        continue
                    
                    filtered_supplements.append(supplement)
            supplements = filtered_supplements
        
        # 가격 정보 가져오기 (비동기로 처리하거나 캐시 사용)
        # 여기서는 간단히 첫 번째 결과만 가격 조회
        if supplements:
            # 실제로는 모든 제품의 가격을 가져와야 하지만,
            # 성능을 위해 상위 10개만 처리
            prices = {}
            for supplement in supplements[:10]:
                # 실제로는 Naver API를 호출하거나 캐시에서 가져옴
                # 여기서는 예시로 처리
                prices[supplement.id] = None  # 실제로는 가격 정보
            
            # 가성비 비교 (가격 정보가 있을 때만)
            if any(prices.values()):
                comparison_data = compare_by_ingredient_price(
                    ingredient_name, prices
                )
            else:
                # 가격 정보 없이 성분 정보만 표시
                comparison_data = [
                    {
                        "supplement_id": s.id,
                        "name": s.name,
                        "brand": s.brand,
                        "image_url": s.image_url,
                        "amount_per_serving": s.ingredients.filter(
                            name__icontains=ingredient_name
                        ).first().amount if s.ingredients.filter(
                            name__icontains=ingredient_name
                        ).exists() else None,
                        "unit": s.ingredients.filter(
                            name__icontains=ingredient_name
                        ).first().unit if s.ingredients.filter(
                            name__icontains=ingredient_name
                        ).exists() else None,
                    }
                    for s in supplements[:20]
                ]
    
    return render(
        request,
        "supplements/pages/ingredient_search/search.html",
        {
            "page_title": "성분 기반 검색 | ALMAENG",
            "ingredient_name": ingredient_name,
            "min_amount": min_amount,
            "max_amount": max_amount,
            "unit": unit,
            "sort_by": sort_by,
            "results": comparison_data,
            "popular_ingredients": [
                "비타민C", "비타민D", "비타민B12", "오메가3", "마그네슘",
                "아연", "철분", "루테인", "코엔자임Q10", "프로바이오틱스",
            ],
        },
    )


async def ingredient_search_async(request: HttpRequest) -> HttpResponse:
    """비동기 성분 검색 (가격 정보 포함, 캐싱 적용)"""
    ingredient_name = request.GET.get("ingredient", "").strip()
    
    if not ingredient_name:
        return HttpResponse('<p class="text-gray-500 text-center py-8">성분명을 입력하세요</p>')
    
    # 캐시 키 생성
    cache_key = f"ingredient_search_{ingredient_name}"
    
    # 캐시 확인 (30분 TTL)
    cached_result = cache.get(cache_key)
    if cached_result:
        return render(
            request,
            "supplements/pages/ingredient_search/_results.html",
            cached_result,
        )
    
    # 성분명으로 검색
    supplements = list(search_by_ingredient(ingredient_name, limit=supplements_settings.MAX_INGREDIENT_SEARCH_RESULTS))
    
    if not supplements:
        return HttpResponse('<p class="text-gray-500 text-center py-8">검색 결과가 없습니다</p>')
    
    # 가격 정보 가져오기 (캐시 활용, interface.py를 통한 접근)
    prices = {}
    
    for supplement in supplements[:prices_settings.MAX_PRICE_LOOKUPS]:
        # 개별 제품 가격 캐시 확인
        price_cache_key = f"product_price_{supplement.id}"
        cached_price = cache.get(price_cache_key)
        
        if cached_price:
            prices[supplement.id] = Decimal(str(cached_price))
        else:
            try:
                search_query = f"{supplement.brand} {supplement.name}"
                price_results = await search_naver_prices(search_query, limit=1)
                if price_results:
                    price = Decimal(str(price_results[0].price))
                    prices[supplement.id] = price
                    # 개별 가격 캐시
                    cache.set(price_cache_key, float(price), timeout=prices_settings.PRICE_CACHE_TIMEOUT)
            except Exception:
                continue
    
    # 가성비 비교
    if prices:
        comparison_data = compare_by_ingredient_price(ingredient_name, prices)
    else:
        comparison_data = []
    
    result_data = {
        "results": comparison_data,
        "ingredient_name": ingredient_name,
    }
    
    # 결과 캐시 저장
    cache.set(cache_key, result_data, timeout=prices_settings.SEARCH_RESULT_CACHE_TIMEOUT)
    
    return render(
        request,
        "supplements/pages/ingredient_search/_results.html",
        result_data,
    )
