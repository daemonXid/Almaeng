"""
🤖 Gemini AI Service for ALMAENG Chatbot

Google Gemini API를 사용한 영양제 전용 챗봇 서비스.
식약처 MFDSHealthFood 데이터 (43,878건) 기반 검색.
Module Version: 2026-01-20-v2 (Force reload)
"""

import os
from dataclasses import dataclass

from django.db.models import Q
from django.conf import settings
from google import genai

from domains.features.supplements.models import Ingredient, Supplement, MFDSHealthFood

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

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"

    def _check_topic(self, question: str) -> bool:
        """질문이 영양제 관련인지 확인"""
        try:
            prompt = TOPIC_CHECK_PROMPT.format(question=question)
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            result = response.text.strip().lower()
            return "related" in result
        except Exception:
            # 에러 시 일단 관련 있다고 처리 (너그럽게)
            return True

    def _get_supplement_context(self, question: str) -> tuple[str, list[dict]]:
        """PostgreSQL에서 관련 영양제 정보 조회 (Supplement + MFDSHealthFood)"""
        sources = []
        context_parts = []

        # 키워드 추출 (간단한 방식)
        keywords = [word for word in question.split() if len(word) > 1]
        
        # 키워드가 없으면 전체 질문을 키워드로 사용
        if not keywords:
            keywords = [question.strip()[:30]]
        
        print(f"[DEBUG] Chatbot search - Question: {question}, Keywords: {keywords}")

        # ========================================
        # 1. MFDSHealthFood 검색 (식약처 데이터)
        # ========================================
        q = Q()
        for keyword in keywords[:3]:
            q |= (
                Q(product_name__icontains=keyword) |
                Q(functionality__icontains=keyword) |
                Q(raw_materials__icontains=keyword) |
                Q(company_name__icontains=keyword)
            )
        mfds_results = list(MFDSHealthFood.objects.filter(q)[:5])
        
        print(f"[DEBUG] MFDS results count: {len(mfds_results)}")

        for mfds in mfds_results:
            context_parts.append(f"""
[식약처 인증 제품]
제품명: {mfds.product_name}
제조사: {mfds.company_name}
주요 기능: {mfds.functionality[:200] if mfds.functionality else '정보 없음'}
섭취 방법: {mfds.intake_method[:100] if mfds.intake_method else '정보 없음'}
주의사항: {mfds.cautions[:100] if mfds.cautions else '정보 없음'}
""")
            sources.append({
                "id": mfds.id,
                "name": mfds.product_name[:50],
                "brand": mfds.company_name
            })

        # ========================================
        # 2. Supplement 검색 (사용자 등록 제품)
        # ========================================
        if len(sources) < 5:  # MFDS에서 충분히 못 찾으면 Supplement도 검색
            supplements = Supplement.objects.filter(name__icontains=question[:20])[:3]

            if not supplements and keywords:
                for keyword in keywords[:2]:
                    supplements = supplements | Supplement.objects.filter(name__icontains=keyword)[:2]

            for supp in supplements[:3]:
                if supp.id not in [s.get("id") for s in sources]:
                    ingredients = Ingredient.objects.filter(supplement=supp)[:10]
                    ingredient_list = ", ".join([f"{i.name} {i.amount}{i.unit}" for i in ingredients])

                    context_parts.append(f"""
[등록 제품]
제품명: {supp.name}
브랜드: {supp.brand}
1회 섭취량: {supp.serving_size}
성분: {ingredient_list if ingredient_list else '정보 없음'}
""")
                    sources.append({"id": f"supp_{supp.id}", "name": supp.name, "brand": supp.brand})

        # ========================================
        # 3. 결과 없음 처리
        # ========================================
        if not context_parts:
            context_parts.append("관련 제품 정보가 데이터베이스에 없습니다. 일반적인 영양제 정보로 답변해주세요.")

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
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
            )
            answer = response.text.strip()
        except Exception as e:
            answer = f"앗, 잠시 문제가 생겼어요! 다시 물어봐주세요~ 🐤 (에러: {e!s})"

        return ChatResponse(answer=answer, sources=sources, is_on_topic=True)


def get_chat_service() -> GeminiChatService:
    """챗봇 서비스 인스턴스 반환 (매 호출 시 새 인스턴스)"""
    return GeminiChatService()


def ask_supplement_question(question: str) -> ChatResponse:
    """영양제 질문에 대한 답변 (외부 인터페이스)"""
    service = get_chat_service()
    return service.ask(question)
