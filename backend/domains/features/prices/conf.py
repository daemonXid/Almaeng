"""
⚙️ Prices Domain Configuration

하드코딩된 값들을 상수로 관리.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PricesSettings:
    """Prices 도메인 설정"""
    
    # 가격 검색 설정
    DEFAULT_PRICE_SEARCH_LIMIT: int = 4  # 기본 가격 검색 결과 수
    MAX_PRICE_LOOKUPS: int = 10  # 최대 가격 조회 개수
    
    # 캐싱 설정 (초 단위)
    PRICE_CACHE_TIMEOUT: int = 3600  # 1시간
    SEARCH_RESULT_CACHE_TIMEOUT: int = 1800  # 30분
    
    # 검색 결과 설정
    DEFAULT_SEARCH_LIMIT: int = 20  # 기본 검색 결과 수
    MAX_SEARCH_RESULTS: int = 50  # 최대 검색 결과 수


# Global settings instance
settings = PricesSettings()
