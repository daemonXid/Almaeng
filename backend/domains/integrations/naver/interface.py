"""
🛍️ Naver Shopping Interface

Public API for Naver Shopping integration.
"""

from decimal import Decimal

from .client import naver_client


async def search_naver_products(keyword: str, limit: int = 20) -> list:
    """
    네이버 쇼핑 검색
    
    Args:
        keyword: 검색 키워드
        limit: 최대 결과 수
        
    Returns:
        list[CrawlResult]: 검색 결과 리스트
    """
    return await naver_client.search(keyword, limit=limit)
