"""
🔍 Search Domain Interface

Public API for search functionality.
External domains should only import from this file.

✅ DAEMON Rule: This is the ONLY file external domains can import from.
"""

from .logic.schemas import CompareResult, ProductResult
from .logic.services import (
    aggregate_search_results,
    mix_search_results,
    transform_coupang_manual_results,
    transform_elevenst_results,
    transform_naver_results,
)

# State interface (DB operations)
from .state.interface import (
    create_search_history,
    get_active_coupang_products,
    get_coupang_products_by_keywords,
)

__all__ = [
    "CompareResult",
    # Schemas (Public Types)
    "ProductResult",
    "aggregate_search_results",
    # State Services (DB Operations)
    "create_search_history",
    "get_active_coupang_products",
    "get_coupang_products_by_keywords",
    "get_search_suggestions",
    "mix_search_results",
    "save_search_history",
    # High-level Services (Orchestration)
    "search_products",
    "transform_coupang_manual_results",
    "transform_elevenst_results",
    # Logic Services (Pure Functions)
    "transform_naver_results",
]


# ============================================
# High-level Orchestration Services
# ============================================

async def search_products(query: str) -> CompareResult:
    """
    Search products from multiple platforms

    ✅ DAEMON Pattern: Orchestration layer
    - Extracts keywords using Gemini AI (Intention Extraction)
    - Calls integrations (Naver, 11st, Coupang) in parallel
    - Transforms results via logic services
    - Returns frozen Pydantic model

    Args:
        query: Natural language search query (e.g., "피로 회복에 좋은 영양제")

    Returns:
        CompareResult with products from all platforms
    """
    from asgiref.sync import sync_to_async

    from domains.integrations.elevenst.interface import search_elevenst_products
    from domains.integrations.gemini.interface import extract_keywords
    from domains.integrations.naver.interface import search_naver_products

    # Step 1: Extract keywords using Gemini AI (Intention Extraction)
    keyword_result = extract_keywords(query)
    keywords = keyword_result.keywords if keyword_result.keywords else [query]
    
    # Use first keyword as main search term
    search_term = keywords[0] if keywords else query

    # Check cache first (24시간)
    from datetime import timedelta
    from django.utils import timezone
    
    # ✅ DAEMON: state/interface.py를 통한 DB 접근
    from .state.interface import get_cached_products
    
    cache_cutoff = timezone.now() - timedelta(hours=24)
    
    # Try to get cached products (graceful fallback if table doesn't exist)
    try:
        cached_products = await sync_to_async(get_cached_products)(search_term, cache_cutoff)
    except Exception:
        # Cache table doesn't exist or other DB error - skip cache
        cached_products = []
    
    # Search from multiple platforms (parallel) - 캐시 없을 때만
    import asyncio

    if cached_products:
        # 캐시 사용
        naver_products = []
        elevenst_products = []
        for cache in cached_products:
            if cache.platform == "naver":
                naver_products.append(cache)
            elif cache.platform == "11st":
                elevenst_products.append(cache)
    else:
        # API 호출
        naver_task = search_naver_products(search_term)
        elevenst_task = search_elevenst_products(search_term)

        naver_results, elevenst_results = await asyncio.gather(
            naver_task,
            elevenst_task,
            return_exceptions=True,
        )

        # Handle errors
        if isinstance(naver_results, Exception):
            naver_results = []
        if isinstance(elevenst_results, Exception):
            elevenst_results = []

        # Transform results
        naver_products = transform_naver_results(naver_results)
        elevenst_products = transform_elevenst_results(elevenst_results)
        
        # Save to cache (async-safe) - 테이블이 없으면 스킵
        async def save_to_cache(products, platform_name):
            """캐시 저장 (실패해도 검색은 계속 진행)"""
            try:
                from .state.models import ProductCache
                
                for p in products[:10]:  # 상위 10개만 캐시
                    try:
                        await sync_to_async(ProductCache.objects.update_or_create)(
                            platform=platform_name,
                            product_id=p.id,
                            defaults={
                                "product_name": p.name,
                                "price": p.price,
                                "original_price": p.original_price,
                                "discount_percent": p.discount_rate,
                                "image_url": p.image_url,
                                "product_url": p.product_url,
                                "mall_name": p.mall_name,
                                "rating": p.rating,
                                "review_count": p.review_count,
                                "search_keyword": search_term,
                            }
                        )
                    except Exception:
                        # 개별 상품 저장 실패는 무시
                        pass
            except Exception:
                # ProductCache 테이블이 없거나 다른 DB 에러 - 스킵
                pass
        
        # 백그라운드로 캐시 저장 (에러 무시)
        try:
            await asyncio.gather(
                save_to_cache(naver_products, "naver"),
                save_to_cache(elevenst_products, "11st"),
                return_exceptions=True
            )
        except Exception:
            # 캐시 저장 실패해도 검색은 계속 진행
            pass

    # Get Coupang manual products (DB 조회를 async-safe하게)
    try:
        coupang_models = await sync_to_async(get_coupang_products_by_keywords)(keywords, limit=20)
        coupang_products = transform_coupang_manual_results(coupang_models)
    except Exception:
        # DB 조회 실패 시 빈 리스트
        coupang_products = []

    # Mix results (70% Coupang, 20% Naver, 10% 11st)
    mixed_products = mix_search_results(
        coupang_products=coupang_products,
        naver_products=naver_products,
        elevenst_products=elevenst_products,
    )

    # Aggregate
    cheapest, best_rated = aggregate_search_results(mixed_products)

    # Generate AI recommendation if products found
    recommendation = f"{len(mixed_products)}개의 상품을 찾았습니다."
    if mixed_products and keyword_result.category:
        recommendation = f"{keyword_result.category} 카테고리에서 {len(mixed_products)}개의 상품을 찾았습니다."

    return CompareResult(
        query=query,
        keywords=keywords,
        products=mixed_products,
        recommendation=recommendation,
        cheapest=cheapest,
        best_rated=best_rated,
    )


def save_search_history(
    user_id: int,
    query: str,
    keywords: list[str],
    category: str = "",
) -> None:
    """
    Save search history for authenticated users

    Args:
        user_id: User ID
        query: Search query
        keywords: Extracted keywords
        category: Category (optional)
    """
    create_search_history(
        user_id=user_id,
        query=query,
        keywords=keywords,
        category=category,
    )


async def get_search_suggestions(query: str) -> list[str]:
    """
    Get search suggestions based on query

    Args:
        query: Partial query

    Returns:
        List of suggestions
    """
    # TODO: Implement autocomplete logic
    # For now, return empty list
    return []
