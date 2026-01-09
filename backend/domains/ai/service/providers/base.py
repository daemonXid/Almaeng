"""
🤖 AI Provider Base - Abstract Interface (v5.0)

All AI providers must implement this interface.
Strategy: Gemini Only (Google Generative AI)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass
class AIResponse:
    """Standard response from any AI Provider."""

    text: str
    model: str
    provider: str
    usage: dict[str, int] = field(default_factory=dict)
    raw: Any = None

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()


@dataclass
class StructuredResponse(Generic[T]):
    """Structured response with Pydantic validation."""

    data: T | None
    raw_text: str
    error: str | None = None

    @property
    def is_valid(self) -> bool:
        return self.data is not None and self.error is None


class AIProviderBase(ABC):
    """
    Abstract base class for AI providers.

    All providers must implement:
    - complete(): Text generation
    - complete_structured(): JSON generation with Pydantic validation
    """

    provider_name: str = "base"

    @abstractmethod
    def complete(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AIResponse:
        """Generate text completion."""
        pass

    @abstractmethod
    def complete_structured(
        self,
        prompt: str,
        schema: type[T],
        model: str | None = None,
        temperature: float = 0.3,
    ) -> StructuredResponse[T]:
        """Generate structured output validated by Pydantic schema."""
        pass

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate text embedding."""
        pass

    @abstractmethod
    def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Generator[str, None, None]:
        """Stream text completion chunks."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and available."""
        pass
