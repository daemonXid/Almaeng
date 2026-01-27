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

    # Search from multiple platforms (parallel)
    import asyncio

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
