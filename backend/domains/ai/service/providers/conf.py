"""
⚙️ GenAI Module Configuration

Environment variables:
    GEMINI_API_KEY: Google Gemini API key (required)
    OPENAI_API_KEY: OpenAI API key (optional, fallback)
    GENAI_DEFAULT_MODEL: Default model to use (default: gemini-pro)
    GENAI_TIMEOUT: API timeout in seconds (default: 30)
"""

import os
from dataclasses import dataclass


@dataclass
class GenAISettings:
    """GenAI module settings."""

    # API Keys
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Model defaults
    DEFAULT_MODEL: str = "gemini-pro"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2048

    # API settings
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3

    def __post_init__(self):
        """Load from environment variables."""
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", self.GEMINI_API_KEY)
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", self.OPENAI_API_KEY)
        self.DEFAULT_MODEL = os.getenv("GENAI_DEFAULT_MODEL", self.DEFAULT_MODEL)
        self.TIMEOUT = int(os.getenv("GENAI_TIMEOUT", self.TIMEOUT))

    @property
    def has_gemini(self) -> bool:
        return bool(self.GEMINI_API_KEY)

    @property
    def has_openai(self) -> bool:
        return bool(self.OPENAI_API_KEY)

    @property
    def is_configured(self) -> bool:
        return self.has_gemini or self.has_openai


# Global settings instance
settings = GenAISettings()
