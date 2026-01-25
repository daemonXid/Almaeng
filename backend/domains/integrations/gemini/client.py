"""
🤖 Gemini Client

Google Gemini API 클라이언트 (PRD v2).
google-genai SDK 사용 (새로운 통합 SDK).
"""

import json
import logging
from dataclasses import dataclass

from django.conf import settings

try:
    from google import genai
except ImportError:
    genai = None

from .prompts import KEYWORD_EXTRACTION_PROMPT, RECOMMENDATION_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class KeywordExtractionResult:
    """키워드 추출 결과"""

    keywords: list[str]
    category: str
    price_min: int | None = None
    price_max: int | None = None


class GeminiClient:
    """Gemini AI 클라이언트 (Singleton)"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is not None:
            return

        api_key = getattr(settings, "GEMINI_API_KEY", "")
        if not api_key or genai is None:
            logger.warning("Gemini API key not configured or google-genai not installed")
            return

        self._client = genai.Client(api_key=api_key)

    def extract_keywords(self, query: str) -> KeywordExtractionResult:
        """
        자연어 질문에서 검색 키워드 추출

        Args:
            query: 사용자 자연어 질문

        Returns:
            KeywordExtractionResult: 추출된 키워드, 카테고리, 가격 범위
        """
        if self._client is None:
            # Fallback: 원본 쿼리를 키워드로 사용
            return KeywordExtractionResult(
                keywords=[query],
                category="",
            )

        try:
            prompt = KEYWORD_EXTRACTION_PROMPT.format(query=query)
            response = self._client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            text = response.text.strip()

            # JSON 파싱
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            data = json.loads(text)

            price_range = data.get("price_range")
            return KeywordExtractionResult(
                keywords=data.get("keywords", [query]),
                category=data.get("category", ""),
                price_min=price_range.get("min") if price_range else None,
                price_max=price_range.get("max") if price_range else None,
            )
        except Exception as e:
            logger.exception(f"Gemini keyword extraction failed: {e}")
            return KeywordExtractionResult(
                keywords=[query],
                category="",
            )

    def generate_recommendation(self, query: str, products_json: str) -> str:
        """
        검색 결과를 바탕으로 추천 메시지 생성

        Args:
            query: 사용자 질문 (검색어)
            products_json: 상품 검색 결과 JSON 문자열

        Returns:
            str: 추천 메시지
        """
        if self._client is None:
            return "검색 결과를 확인해보세요."

        try:
            prompt = RECOMMENDATION_PROMPT.format(query=query, products_json=products_json)
            response = self._client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.exception(f"Gemini recommendation failed: {e}")
            return "검색 결과를 확인해보세요."


# Singleton instance
gemini_client = GeminiClient()
