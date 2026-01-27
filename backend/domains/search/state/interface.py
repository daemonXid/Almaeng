"""
🔍 Search State Interface

DB operations for search domain.
This is the ONLY file that should import from .models
"""

from datetime import datetime

from django.db.models import Q

from .models import CoupangManualProduct, ProductCache, SearchHistory


def create_search_history(
    user_id: int | None,
    query: str,
    keywords: list[str],
    category: str = "",
) -> int:
    """
    Create search history record

    Args:
        user_id: User ID (nullable)
        query: Original query
        keywords: Extracted keywords
        category: Category (optional)

    Returns:
        Created history ID
    """
    history = SearchHistory.objects.create(
        user_id=user_id,
        query=query,
        keywords=keywords,
        category=category,
    )
    return history.id


def get_active_coupang_products(limit: int = 100) -> list[CoupangManualProduct]:
    """
    Get active Coupang manual products

    Args:
        limit: Result limit

    Returns:
        List of active products
    """
    return list(
        CoupangManualProduct.objects.filter(is_active=True).order_by("-created_at")[:limit]
    )


def get_coupang_products_by_keywords(
    keywords: list[str],
    limit: int = 20,
) -> list[CoupangManualProduct]:
    """
    Search Coupang products by keywords

    Args:
        keywords: Search keywords
        limit: Result limit

    Returns:
        Matching products
    """
    if not keywords:
        return []

    # Build OR query for keywords
    q = Q()
    for keyword in keywords:
        q |= (
            Q(name__icontains=keyword)
            | Q(category__icontains=keyword)
            | Q(keywords__icontains=keyword)
        )

    return list(
        CoupangManualProduct.objects.filter(q).filter(is_active=True).order_by("-created_at")[:limit]
    )


def get_cached_products(search_keyword: str, cache_cutoff: datetime) -> list[ProductCache]:
    """
    Get cached products by search keyword
    
    ✅ DAEMON Pattern: DB 접근은 state/interface.py를 통해서만
    
    Args:
        search_keyword: Search keyword
        cache_cutoff: Cache cutoff datetime (24시간 전)
    
    Returns:
        List of cached products
    """
    return list(
        ProductCache.objects.filter(
            search_keyword=search_keyword,
            cached_at__gte=cache_cutoff
        )[:20]
    )


def save_product_to_cache(
    platform: str,
    product_id: str,
    product_name: str,
    price: int,
    original_price: int | None,
    discount_percent: int | None,
    image_url: str,
    product_url: str,
    mall_name: str,
    rating: float | None,
    review_count: int,
    search_keyword: str,
) -> None:
    """
    Save product to cache
    
    ✅ DAEMON Pattern: DB 쓰기는 state/interface.py를 통해서만
    """
    ProductCache.objects.update_or_create(
        platform=platform,
        product_id=product_id,
        defaults={
            "product_name": product_name,
            "price": price,
            "original_price": original_price,
            "discount_percent": discount_percent,
            "image_url": image_url,
            "product_url": product_url,
            "mall_name": mall_name,
            "rating": rating,
            "review_count": review_count,
            "search_keyword": search_keyword,
        }
    )
