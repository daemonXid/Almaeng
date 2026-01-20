"""
⚙️ GenAI Module Configuration - Gemini Only

Environment variables:
    GEMINI_API_KEY: Google Gemini API key (required)
    GEMINI_MODEL: Default model to use (default: gemini-2.0-flash)
    GENAI_TIMEOUT: API timeout in seconds (default: 30)
"""

import os
from dataclasses import dataclass


@dataclass
class GenAISettings:
    """GenAI module settings - Gemini Only."""

    # API Keys
    GEMINI_API_KEY: str = ""

    # Model defaults
    DEFAULT_MODEL: str = "gemini-2.0-flash"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2048

    # API settings
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3

    def __post_init__(self):
        """Load from environment variables."""
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", self.GEMINI_API_KEY)
        self.DEFAULT_MODEL = os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL)
        self.TIMEOUT = int(os.getenv("GENAI_TIMEOUT", self.TIMEOUT))

    @property
    def has_gemini(self) -> bool:
        return bool(self.GEMINI_API_KEY)

    @property
    def is_configured(self) -> bool:
        return self.has_gemini


# Global settings instance
settings = GenAISettings()
