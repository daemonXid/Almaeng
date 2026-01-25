"""
🛒 11번가 Interface

Public API for 11st integration.
"""

from .client import elevenst_client


async def search_elevenst_products(keyword: str, limit: int = 20) -> list:
    """
    11번가 상품 검색
    
    Args:
        keyword: 검색 키워드
        limit: 최대 결과 수
        
    Returns:
        list[CrawlResult]: 검색 결과 리스트
    """
    return await elevenst_client.search(keyword, limit=limit)
