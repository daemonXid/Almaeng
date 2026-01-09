"""
🤖 Gemini Provider - Google Gemini AI Integration

Uses Google's Gemini API with Free Tier support.
Implements the AIProviderBase interface.

Model Options:
- gemini-2.0-flash (default, fast, free tier)
- gemini-1.5-pro (higher quality)
- gemini-1.5-flash (balanced)

Environment:
    GEMINI_API_KEY: Google Gemini API key (required)
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Generator
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import AIProviderBase, AIResponse, StructuredResponse

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Default model for Gemini
DEFAULT_MODEL = "gemini-2.0-flash"


class GeminiProvider(AIProviderBase):
    """
    Google Gemini AI Provider.

    Uses the google-generativeai SDK for text generation,
    structured output, and embeddings.

    Example:
        from domains.ai.service.providers.interface import get_ai_client

        client = get_ai_client()
        response = client.complete("Hello!")
        print(response.text)
    """

    provider_name = "gemini"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._client = None

    def _get_client(self) -> Any:
        """Get or create Gemini client."""
        if self._client is None and self.api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                logger.warning("google-generativeai not installed. Run: uv add google-generativeai")
        return self._client

    def is_available(self) -> bool:
        """Check if Gemini is configured and available."""
        return bool(self.api_key and self._get_client())

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def complete(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AIResponse:
        """
        Generate text completion using Gemini.

        Args:
            prompt: Input prompt
            model: Model name (default: gemini-2.0-flash)
            temperature: Creativity (0.0-1.0)
            max_tokens: Maximum response length

        Returns:
            AIResponse with generated text
        """
        model = model or DEFAULT_MODEL
        gemini = self._get_client()

        if not gemini:
            logger.error("Gemini client not available")
            return AIResponse(text="", model=model, provider=self.provider_name)

        try:
            gen_model = gemini.GenerativeModel(model)
            response = gen_model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            return AIResponse(
                text=response.text,
                model=model,
                provider=self.provider_name,
                usage={},
                raw=response,
            )
        except Exception as e:
            logger.error(f"Gemini completion error: {e}")
            return AIResponse(text="", model=model, provider=self.provider_name)

    def complete_structured(
        self,
        prompt: str,
        schema: type[T],
        model: str | None = None,
        temperature: float = 0.3,
    ) -> StructuredResponse[T]:
        """
        Generate structured output validated by Pydantic schema.

        Implements "Data-Driven UI" pattern:
        - AI generates JSON only
        - Output is validated against strict schema
        - Invalid output is rejected, not rendered

        Args:
            prompt: Input prompt
            schema: Pydantic model class for validation
            model: Model name
            temperature: Creativity (lower recommended)

        Returns:
            StructuredResponse with validated data or error
        """
        schema_json = schema.model_json_schema()

        enhanced_prompt = f"""
{prompt}

Respond ONLY with valid JSON matching this schema:
{json.dumps(schema_json, indent=2)}

Do not include any text before or after the JSON.
"""

        response = self.complete(prompt=enhanced_prompt, model=model, temperature=temperature)

        if response.is_empty:
            return StructuredResponse(
                data=None,
                raw_text=response.text,
                error="Empty response from AI",
            )

        # Parse JSON
        try:
            text = response.text.strip()
            # Handle markdown code blocks
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            json_data = json.loads(text)
        except json.JSONDecodeError as e:
            return StructuredResponse(
                data=None,
                raw_text=response.text,
                error=f"Invalid JSON: {e}",
            )

        # Validate with Pydantic
        try:
            validated = schema.model_validate(json_data)
            return StructuredResponse(
                data=validated,
                raw_text=response.text,
            )
        except ValidationError as e:
            return StructuredResponse(
                data=None,
                raw_text=response.text,
                error=f"Schema validation failed: {e}",
            )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def embed(self, text: str) -> list[float]:
        """
        Generate text embedding using Gemini.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (768 dimensions)
        """
        gemini = self._get_client()
        if not gemini:
            return []

        try:
            result = gemini.embed_content(
                model="models/embedding-001",
                content=text,
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Gemini embedding error: {e}")
            return []

    def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Generator[str, None, None]:
        """
        Stream text completion chunks.

        Args:
            prompt: Input prompt
            model: Model name
            temperature: Creativity
            max_tokens: Max tokens

        Yields:
            Text chunks as they are generated
        """
        model = model or DEFAULT_MODEL
        gemini = self._get_client()

        if not gemini:
            logger.error("Gemini client not available")
            return

        try:
            gen_model = gemini.GenerativeModel(model)
            response = gen_model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
                stream=True,
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            yield ""
