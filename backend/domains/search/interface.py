"""
🔍 Search Domain Interface

Public API for search domain. This is the ONLY entry point for external domains.
"""

import asyncio
import hashlib
import json
from typing import Any

from django.core.cache import cache
from django.db import models

from domains.integrations.elevenst.interface import search_elevenst_products
from domains.integrations.gemini.interface import extract_keywords, generate_recommendation
from domains.integrations.naver.interface import search_naver_products

from .logic.schemas import CompareResult, ProductResult
from .state.interface import get_user_search_history, save_search_history


async def search_products(query: str, limit: int = 20, use_cache: bool = True) -> CompareResult:
    """
    Search products using natural language query (multi-platform)

    This is the main entry point for product search. It orchestrates:
    - Keyword extraction (Gemini AI)
    - Multi-platform product search (Naver, 11st)
    - Result aggregation and caching

    Args:
        query: User's natural language query
        limit: Maximum results per platform
        use_cache: Whether to use cache (default: True)

    Returns:
        CompareResult: Search results and recommendation message
    """
    # Check cache first
    if use_cache:
        cache_key = f"search:{hashlib.md5(query.lower().strip().encode()).hexdigest()}:{limit}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return CompareResult(**json.loads(cached_result))

    try:
        # 1. Extract keywords (via interface)
        extraction = extract_keywords(query)
        keywords = extraction.keywords

        # 2. Parallel API calls with timeout (via interfaces)
        search_keyword = keywords[0] if keywords else query
        naver_task = search_naver_products(search_keyword, limit=limit)
        elevenst_task = search_elevenst_products(search_keyword, limit=limit)

        naver_results: Any = []
        elevenst_results: Any = []

        try:
            # Set timeout for API calls (10 seconds)
            naver_results, elevenst_results = await asyncio.wait_for(
                asyncio.gather(naver_task, elevenst_task, return_exceptions=True),
                timeout=10.0,
            )
        except asyncio.TimeoutError:
            # If timeout, continue with empty results
            naver_results = []
            elevenst_results = []

        # Handle exceptions from API calls
        if isinstance(naver_results, Exception):
            naver_results = []
        if isinstance(elevenst_results, Exception):
            elevenst_results = []

        # 3. Transform results using pure functions from logic/
        from .logic.services import aggregate_search_results, transform_elevenst_results, transform_naver_results

        products: list[ProductResult] = []
        products.extend(transform_naver_results(naver_results))
        products.extend(transform_elevenst_results(elevenst_results))

        # 4. Aggregate results (find cheapest/best rated)
        cheapest, best_rated = aggregate_search_results(products)

        # 5. Generate AI recommendation message (only if products exist)
        recommendation = ""
        if products:
            try:
                products_json = json.dumps([p.model_dump() for p in products[:5]], ensure_ascii=False)
                recommendation = generate_recommendation(query, products_json)
            except Exception:
                # Fallback recommendation if AI fails
                recommendation = f"Found {len(products)} products for '{query}'. Compare prices and choose the best option."

        result = CompareResult(
            query=query,
            keywords=keywords,
            products=products,
            recommendation=recommendation,
            cheapest=cheapest,
            best_rated=best_rated,
        )

        # Cache result for 5 minutes
        if use_cache:
            cache.set(cache_key, json.dumps(result.model_dump(), default=str), 300)

        return result

    except Exception as e:
        # Return empty result on any error
        return CompareResult(
            query=query,
            keywords=[],
            products=[],
            recommendation="An error occurred while searching. Please try again.",
            cheapest=None,
            best_rated=None,
        )


def get_search_suggestions(query: str, user_id: int | None = None, limit: int = 5) -> list[str]:
    """
    Get search suggestions based on query and user history

    Args:
        query: Partial search query
        user_id: User ID (optional, for personalized suggestions)
        limit: Maximum number of suggestions

    Returns:
        list[str]: List of suggested search queries
    """
    from .state.models import SearchHistory

    query_lower = query.lower().strip()
    if not query_lower:
        return []

    suggestions: list[str] = []

    # 1. User's search history (if authenticated)
    if user_id:
        user_history = SearchHistory.objects.filter(
            user_id=user_id, query__icontains=query_lower
        ).values_list("query", flat=True).distinct()[:limit]
        suggestions.extend(user_history)

    # 2. Popular searches (all users, excluding current user's)
    popular = (
        SearchHistory.objects.exclude(user_id=user_id)
        .filter(query__icontains=query_lower)
        .values("query")
        .annotate(count=models.Count("id"))
        .order_by("-count")[:limit]
    )
    for item in popular:
        if item["query"] not in suggestions:
            suggestions.append(item["query"])

    return suggestions[:limit]


# Re-export state interface functions
__all__ = [
    "search_products",
    "save_search_history",
    "get_user_search_history",
    "get_search_suggestions",
]
