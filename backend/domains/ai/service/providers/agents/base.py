"""
🤖 Pydantic AI Agent Base - Gemini Only

Provides Gemini model for pydantic-ai agents.
"""

from __future__ import annotations

import os
from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic_ai.models.gemini import GeminiModel


T = TypeVar("T", bound=BaseModel)


class AgentContext(BaseModel):
    """Context passed to agents."""

    user_id: str | None = None
    project_context: dict[str, Any] = {}


def get_pydantic_ai_model() -> GeminiModel:
    """
    Get the Gemini model for pydantic_ai.

    Returns:
        GeminiModel instance using GEMINI_API_KEY from environment.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required")

    return GeminiModel(
        model_name=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        api_key=api_key,
    )
