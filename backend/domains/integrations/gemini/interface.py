"""
🤖 Gemini Interface

Public API for Gemini AI integration.
"""

from .client import gemini_client


def extract_keywords(query: str):
    """
    자연어 질문에서 검색 키워드 추출
    
    Args:
        query: 사용자 자연어 질문
        
    Returns:
        KeywordExtractionResult: 추출된 키워드, 카테고리, 가격 범위
    """
    return gemini_client.extract_keywords(query)


def generate_recommendation(query: str, products_json: str) -> str:
    """
    검색 결과를 바탕으로 추천 메시지 생성
    
    Args:
        query: 사용자 질문
        products_json: 상품 검색 결과 JSON 문자열
        
    Returns:
        str: 추천 메시지
    """
    return gemini_client.generate_recommendation(query, products_json)
