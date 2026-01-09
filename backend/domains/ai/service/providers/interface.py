"""
🤖 AI Providers Interface - Public API

This is the ONLY file that should be imported from outside this module.
Uses Google Gemini as the primary (and only) AI provider.

Usage:
    from domains.ai.service.providers.interface import get_ai_client, AIResponse

    client = get_ai_client()
    response = client.complete("Hello!")
    print(response.text)

Environment:
    GEMINI_API_KEY: Google Gemini API key (required)
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import TypeVar

from pydantic import BaseModel

from .base import AIProviderBase, AIResponse, StructuredResponse
from .gemini import GeminiProvider

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Available providers (Gemini only for simplicity)
PROVIDERS: dict[str, type[AIProviderBase]] = {
    "gemini": GeminiProvider,
}


@lru_cache(maxsize=1)
def get_provider(name: str = "gemini") -> AIProviderBase:
    """
    Get a specific AI provider by name.

    Args:
        name: Provider name (currently only "gemini")

    Returns:
        AIProviderBase instance

    Raises:
        ValueError: If provider name is unknown
    """
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDERS.keys())}")

    provider_class = PROVIDERS[name]
    return provider_class()


def get_ai_client() -> AIProviderBase:
    """
    Get the AI client (Gemini).

    Returns:
        GeminiProvider instance
    """
    provider = get_provider("gemini")
    if provider.is_available():
        logger.info("Using AI provider: Gemini")
        return provider

    logger.warning("Gemini provider is not available (check GEMINI_API_KEY)")
    return provider


# Convenience function for quick completions
def complete(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.7,
) -> AIResponse:
    """
    Quick text completion using Gemini.

    Args:
        prompt: Input prompt
        model: Optional model name (default: gemini-2.0-flash)
        temperature: Creativity (0.0-1.0)

    Returns:
        AIResponse
    """
    try:
        client = get_ai_client()
        if not client.is_available():
            logger.error("Gemini provider not available")
            return AIResponse(text="", model=model or "", provider="none")

        response = client.complete(prompt=prompt, model=model, temperature=temperature)
        return response
    except Exception as e:
        logger.error(f"Gemini completion failed: {e}")
        return AIResponse(text="", model=model or "", provider="none")


def complete_structured(
    prompt: str,
    schema: type[T],
    temperature: float = 0.3,
) -> StructuredResponse[T]:
    """
    Quick structured completion using Gemini.

    Args:
        prompt: Input prompt
        schema: Pydantic model class for validation
        temperature: Creativity (lower recommended)

    Returns:
        StructuredResponse[T]
    """
    client = get_ai_client()
    return client.complete_structured(prompt=prompt, schema=schema, temperature=temperature)


# --- Pydantic AI Agents ---
from .agents.architect import get_architect_agent
from .agents.base import AgentContext

# Re-export for convenience
__all__ = [
    "PROVIDERS",
    "AIProviderBase",
    "AIResponse",
    "AgentContext",
    "GeminiProvider",
    "StructuredResponse",
    "complete",
    "complete_structured",
    "get_ai_client",
    "get_architect_agent",
    "get_provider",
]
