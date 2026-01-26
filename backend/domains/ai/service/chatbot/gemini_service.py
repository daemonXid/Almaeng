"""
🤖 Gemini AI Service for ALMAENG Chatbot

Google Gemini API를 사용한 범용 AI 서비스.
독립적으로 존재하며, 필요한 도메인에서 interface를 통해 호출.

✅ DAEMON Pattern: Stateless, Pure AI Service
Module Version: 2026-01-26-v4 (Clean)
"""

import os
from dataclasses import dataclass

from django.conf import settings
from google import genai


@dataclass
class ChatResponse:
    """챗봇 응답 데이터"""

    answer: str
    sources: list[dict] | None = None
    is_on_topic: bool = True


class GeminiChatService:
    """
    Gemini 기반 범용 AI 챗봇 서비스

    ✅ DAEMON Pattern:
    - 독립적인 AI 서비스 (도메인 의존성 없음)
    - 컨텍스트는 호출자가 제공
    - 순수 함수형 인터페이스
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"

    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        """
        Generate response from Gemini

        ✅ Pure function: No DB, No side effects

        Args:
            prompt: User prompt
            system_instruction: System instruction (optional)

        Returns:
            Generated text
        """
        try:
            contents = prompt
            if system_instruction:
                contents = f"{system_instruction}\n\n{prompt}"

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
            )
            return response.text.strip()
        except Exception as e:
            return f"AI 응답 생성 중 오류가 발생했습니다: {e!s}"

    def chat(
        self,
        question: str,
        context: str | None = None,
        system_instruction: str | None = None,
    ) -> ChatResponse:
        """
        Chat with context

        ✅ DAEMON Pattern: Context는 호출자가 제공

        Args:
            question: User question
            context: Additional context (optional)
            system_instruction: System instruction (optional)

        Returns:
            ChatResponse
        """
        # Build prompt
        prompt_parts = []

        if system_instruction:
            prompt_parts.append(f"[System]\n{system_instruction}")

        if context:
            prompt_parts.append(f"[Context]\n{context}")

        prompt_parts.append(f"[Question]\n{question}")

        full_prompt = "\n\n".join(prompt_parts)

        # Generate response
        answer = self.generate(full_prompt)

        return ChatResponse(
            answer=answer,
            sources=None,
            is_on_topic=True,
        )


# ============================================
# Singleton Instance (Performance)
# ============================================

_gemini_service: GeminiChatService | None = None


def get_gemini_service() -> GeminiChatService:
    """
    Get Gemini service singleton

    ✅ DAEMON Pattern: Singleton Model Loader
    - Load once, use forever
    - Prevents repeated initialization
    """
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiChatService()
    return _gemini_service


# ============================================
# Public Interface Functions
# ============================================

def ask_question(
    question: str,
    context: str | None = None,
    system_instruction: str | None = None,
) -> ChatResponse:
    """
    Ask question to Gemini AI

    ✅ Public Interface: 다른 도메인에서 호출

    Args:
        question: User question
        context: Additional context (optional)
        system_instruction: System instruction (optional)

    Returns:
        ChatResponse
    """
    service = get_gemini_service()
    return service.chat(question, context, system_instruction)


def generate_text(
    prompt: str,
    system_instruction: str | None = None,
) -> str:
    """
    Generate text from Gemini AI

    ✅ Public Interface: 간단한 텍스트 생성

    Args:
        prompt: User prompt
        system_instruction: System instruction (optional)

    Returns:
        Generated text
    """
    service = get_gemini_service()
    return service.generate(prompt, system_instruction)
