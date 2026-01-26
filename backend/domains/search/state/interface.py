"""
🔍 Search State Interface

DB operations for search domain.
This is the ONLY file that should import from .models
"""

from django.db.models import Q

from .models import CoupangManualProduct, SearchHistory


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
