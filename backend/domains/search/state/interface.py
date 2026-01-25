"""
🔍 Search State Interface

Public API for search history.
"""

from .models import SearchHistory


def save_search_history(user_id: int | None, query: str, keywords: list[str], category: str = "") -> SearchHistory:
    """
    Save search history

    Args:
        user_id: User ID (if logged in)
        query: Original query
        keywords: Extracted keywords
        category: Category

    Returns:
        SearchHistory: Saved search history
    """
    return SearchHistory.objects.create(
        user_id=user_id,
        query=query,
        keywords=keywords,
        category=category,
    )


def get_user_search_history(user_id: int, limit: int = 20) -> list[SearchHistory]:
    """
    Get user search history

    Args:
        user_id: User ID
        limit: Maximum results

    Returns:
        list[SearchHistory]: Search history list
    """
    return list(SearchHistory.objects.filter(user_id=user_id).order_by("-created_at")[:limit])
