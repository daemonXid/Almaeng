"""
📦 Product Detail Views

MFDS Data Display + Real-time Naver Price Lookup (HTMX)
"""

from decimal import Decimal
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from ...logic.parser import extract_ingredients, extract_nutrient_content, calculate_unit_cost, TARGET_NUTRIENTS
from ...logic.sets import calculate_value_metrics
from django.db.models import Q
from ...models import Supplement
from ....prices.models import PriceHistory

def product_detail(request: HttpRequest, product_id: int) -> HttpResponse:
    """제품 상세 페이지 (SSR)"""
    # 1. Supplement 모델 사용 (없으면 404)
    # 기존 MFDS ID와의 호환성은 고려하지 않음 (완전 전환)
    try:
        product = Supplement.objects.get(id=product_id)
    except Supplement.DoesNotExist:
        # 혹시 MFDS ID로 들어왔을 경우를 대비해 예외 처리 등 가능하나 일단 404
        return render(request, "404.html", status=404)
    
    # 2. Wishlist status
    in_wishlist = False
    if request.user.is_authenticated:
        from domains.features.wishlist.interface import is_in_wishlist
        in_wishlist = is_in_wishlist(request.user.id, product_id)

    # 3. Similar Products (Logic: Same Brand or Random for now)
    # 추후 AI 분석 결과(benefits) 기반으로 고도화
    # 3. Similar Products (Logic: Same Brand -> Random)
    similar_products = Supplement.objects.filter(brand=product.brand).exclude(id=product_id)[:4]
    
    if not similar_products:
        similar_products = Supplement.objects.exclude(id=product_id).order_by("?")[:4]

    # 4. Price History (최저가 확인)
    lowest_price = PriceHistory.objects.filter(supplement_id=product.id).order_by("price").first()

    return render(
        request,
        "supplements/pages/detail/detail_page.html",
        {
            "product": product,
            "page_title": f"{product.name} | ALMAENG",
            "in_wishlist": in_wishlist,
            "similar_products": similar_products,
            "lowest_price": lowest_price,
        },
    )


async def product_prices(request: HttpRequest, product_id: int) -> HttpResponse:
    """HTMX: 실시간 가격 조회 (Naver API)"""
    try:
        product = await MFDSHealthFood.objects.aget(id=product_id)
        
        # Crawler Orchestrator would be better, but direct use for MVP is fine
        crawler = NaverCrawler()
        
        # Search query strategy
        # 1. First try: "{Company} {Product}"
        # Filter out common legal suffixes from company name for better match
        company_clean = product.company_name.replace("(주)", "").replace("주식회사", "").strip()
        search_query_1 = f"{company_clean} {product.product_name}"
        
        print(f"[DEBUG] Naver search query (Primary): {search_query_1}")
        result = await crawler.search(search_query_1)
        
        # 2. Fallback: "{Product}" only if primary fails
        if not result:
            print(f"[DEBUG] Primary search failed. Trying fallback: {product.product_name}")
            result = await crawler.search(product.product_name)
            
        print(f"[DEBUG] Final Naver search results count: {len(result)}")
        
        # --- 🧬 Value Metrics Calculation ---
        value_metrics = None
        if result and result[0].price:
            value_metrics = calculate_value_metrics(
                product=product,
                price=result[0].price,
                servings=30,  # Default assumption
            )
            if value_metrics:
                print(f"[DEBUG] Value Metrics: {value_metrics}")

        # --- 🧠 AI Unit Cost Analysis (Legacy, kept for compatibility) ---
        unit_analysis = None
        
        # 1. Identify Target Nutrient
        target_nutrient = None
        parsed_list = extract_ingredients(product.raw_materials)
        if parsed_list:
            target_nutrient = parsed_list[0]
        else:
            # Fallback scan
            for nutrient in TARGET_NUTRIENTS:
                if nutrient in product.raw_materials:
                    target_nutrient = nutrient
                    break
                    
        # 2. Extract & Calculate
        if target_nutrient:
            content_info = extract_nutrient_content(product.raw_materials, target_nutrient)
            
            # Parse Serving Info (New!)
            from ...logic.parser import parse_serving_info
            serving_info = parse_serving_info(product.intake_method, product.product_form)
            
            if content_info:
                unit_analysis = {
                    "nutrient": target_nutrient,
                    "amount": content_info["amount"],
                    "unit": content_info["unit"],
                    "match_text": content_info["match"],
                    "daily_count": serving_info["daily_count"],
                    "count_unit": serving_info["unit"],
                }
                
                # Daily Amount
                daily_intake_amount = content_info["amount"] * serving_info["daily_count"]
                unit_analysis["daily_total_amount"] = daily_intake_amount

        return render(
            request,
            "supplements/pages/detail/_price_list.html",
            {
                "prices": result, 
                "product": product, 
                "unit_analysis": unit_analysis,
                "value_metrics": value_metrics,
            },
        )
    except Exception as e:
        import traceback
        print(f"[ERROR] product_prices exception: {e}")
        traceback.print_exc()
        return HttpResponse(
            f'<div class="text-red-500 text-sm p-4 text-center">가격 정보를 불러오는데 실패했습니다.<br><span class="text-xs text-gray-400">{str(e)}</span></div>'
        )

