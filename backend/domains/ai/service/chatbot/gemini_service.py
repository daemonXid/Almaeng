"""
🤖 Gemini AI Service for ALMAENG Chatbot

Google Gemini API를 사용한 영양제 전용 챗봇 서비스.
"""

import os
from dataclasses import dataclass

import google.generativeai as genai
from django.conf import settings

from domains.features.supplements.models import Ingredient, Supplement

from .prompts import ANSWER_PROMPT, OFF_TOPIC_RESPONSE, SYSTEM_PROMPT, TOPIC_CHECK_PROMPT


@dataclass
class ChatResponse:
    """챗봇 응답 데이터"""

    answer: str
    sources: list[dict] | None = None
    is_on_topic: bool = True


class GeminiChatService:
    """Gemini 기반 영양제 챗봇 서비스"""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def _check_topic(self, question: str) -> bool:
        """질문이 영양제 관련인지 확인"""
        try:
            prompt = TOPIC_CHECK_PROMPT.format(question=question)
            response = self.model.generate_content(prompt)
            result = response.text.strip().lower()
            return "related" in result
        except Exception:
            # 에러 시 일단 관련 있다고 처리 (너그럽게)
            return True

    def _get_supplement_context(self, question: str) -> tuple[str, list[dict]]:
        """PostgreSQL에서 관련 영양제 정보 조회"""
        sources = []
        context_parts = []

        # 키워드 추출 (간단한 방식)
        keywords = [word for word in question.split() if len(word) > 1]

        # 영양제 검색
        supplements = Supplement.objects.filter(name__icontains=question[:20])[:5]

        if not supplements and keywords:
            for keyword in keywords[:3]:
                supplements = supplements | Supplement.objects.filter(name__icontains=keyword)[:3]

        for supp in supplements[:5]:
            ingredients = Ingredient.objects.filter(supplement=supp)[:10]
            ingredient_list = ", ".join([f"{i.name} {i.amount}{i.unit}" for i in ingredients])

            context_parts.append(f"""
제품: {supp.name}
브랜드: {supp.brand}
카테고리: {supp.category}
1회 섭취량: {supp.serving_size}
총 횟수: {supp.servings_count}회
성분: {ingredient_list}
""")
            sources.append({"id": supp.id, "name": supp.name, "brand": supp.brand})

        # 성분 직접 검색
        if keywords:
            for keyword in keywords[:3]:
                ingredients = Ingredient.objects.filter(name__icontains=keyword).select_related("supplement")[:5]
                for ing in ingredients:
                    if ing.supplement and ing.supplement.id not in [s["id"] for s in sources]:
                        context_parts.append(f"""
성분 '{ing.name}' 포함 제품: {ing.supplement.name}
함량: {ing.amount}{ing.unit}
""")

        if not context_parts:
            context_parts.append("관련 제품 정보가 데이터베이스에 없습니다.")

        return "\n".join(context_parts), sources

    def ask(self, question: str) -> ChatResponse:
        """질문에 대한 응답 생성"""
        # 1. 주제 체크
        is_on_topic = self._check_topic(question)
        if not is_on_topic:
            return ChatResponse(answer=OFF_TOPIC_RESPONSE, is_on_topic=False)

        # 2. 데이터베이스에서 컨텍스트 조회
        context, sources = self._get_supplement_context(question)

        # 3. Gemini로 답변 생성
        try:
            full_prompt = f"{SYSTEM_PROMPT}\n\n{ANSWER_PROMPT.format(context=context, question=question)}"
            response = self.model.generate_content(full_prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = f"앗, 잠시 문제가 생겼어요! 다시 물어봐주세요~ 🐤 (에러: {e!s})"

        return ChatResponse(answer=answer, sources=sources, is_on_topic=True)


# 싱글톤 인스턴스
_chat_service: GeminiChatService | None = None


def get_chat_service() -> GeminiChatService:
    """챗봇 서비스 인스턴스 반환"""
    global _chat_service
    if _chat_service is None:
        _chat_service = GeminiChatService()
    return _chat_service


def ask_supplement_question(question: str) -> ChatResponse:
    """영양제 질문에 대한 답변 (외부 인터페이스)"""
    service = get_chat_service()
    return service.ask(question)
