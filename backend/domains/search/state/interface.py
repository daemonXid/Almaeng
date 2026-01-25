"""
🔍 Search State Interface

Public API for search history.
"""

from .models import SearchHistory


def save_search_history(user_id: int | None, query: str, keywords: list[str], category: str = "") -> SearchHistory:
    """
    검색 히스토리 저장
    
    Args:
        user_id: 사용자 ID (로그인 시)
        query: 원본 질문
        keywords: 추출된 키워드
        category: 카테고리
        
    Returns:
        SearchHistory: 저장된 검색 히스토리
    """
    return SearchHistory.objects.create(
        user_id=user_id,
        query=query,
        keywords=keywords,
        category=category,
    )


def get_user_search_history(user_id: int, limit: int = 20) -> list[SearchHistory]:
    """
    사용자 검색 히스토리 조회
    
    Args:
        user_id: 사용자 ID
        limit: 최대 결과 수
        
    Returns:
        list[SearchHistory]: 검색 히스토리 리스트
    """
    return list(SearchHistory.objects.filter(user_id=user_id).order_by("-created_at")[:limit])
