from __future__ import annotations

import os
from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic_ai.models.openai import OpenAIModel

T = TypeVar("T", bound=BaseModel)


class AgentContext(BaseModel):
    """Context passed to agents."""

    user_id: str | None = None
    project_context: dict[str, Any] = {}


def get_pydantic_ai_model():
    """
    Get the appropriate pydantic_ai model instance based on AI_PROVIDER.

    Note: HuggingFace uses OpenAI-compatible API via Inference Endpoints.
    """
    provider = os.getenv("AI_PROVIDER", "huggingface").lower()

    if provider == "huggingface":
        # HuggingFace Inference API via OpenAI-compatible endpoint
        hf_token = os.getenv("HUGGINGFACE_API_KEY", "")
        model_id = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
        return OpenAIModel(
            model_name=model_id,
            base_url=f"https://api-inference.huggingface.co/models/{model_id}/v1",
            api_key=hf_token if hf_token else "hf_dummy",
        )
    elif provider == "deepseek":
        return OpenAIModel(
            model_name=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
        )
    elif provider == "openrouter":
        return OpenAIModel(
            model_name=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    # Fallback to OpenAI compatible if key exists
    return OpenAIModel("gpt-4o")
