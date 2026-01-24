"""
⚙️ Supplements Domain Configuration

하드코딩된 값들을 상수로 관리.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SupplementsSettings:
    """Supplements 도메인 설정"""
    
    # 서빙 설정
    DEFAULT_SERVINGS: int = 30  # 기본 서빙 수 (일 단위)
    
    # 검색 설정
    DEFAULT_SEARCH_LIMIT: int = 20  # 기본 검색 결과 수
    MAX_SEARCH_RESULTS: int = 50  # 최대 검색 결과 수
    
    # 성분 검색 설정
    MAX_INGREDIENT_SEARCH_RESULTS: int = 20  # 성분 검색 최대 결과 수


# Global settings instance
settings = SupplementsSettings()
