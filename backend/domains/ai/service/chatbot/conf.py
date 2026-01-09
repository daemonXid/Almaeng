"""
⚙️ Chatbot Module Configuration

Settings for project file indexing and search.
"""

import os
from dataclasses import dataclass, field


@dataclass
class ChatbotSettings:
    """Chatbot module settings."""

    # Indexing settings
    INDEX_ROOT: str = "backend/"
    INDEXED_EXTENSIONS: list[str] = field(
        default_factory=lambda: [".py", ".html", ".md", ".js", ".css", ".yaml", ".yml"]
    )
    EXCLUDED_DIRS: list[str] = field(
        default_factory=lambda: [
            "__pycache__",
            "node_modules",
            ".git",
            ".venv",
            "migrations",
            "static/dist",
            "static/css/output.css",
        ]
    )
    MAX_FILE_SIZE: int = 50000  # 50KB max per file

    # Search settings
    MAX_RESULTS: int = 5
    CHUNK_SIZE: int = 1000  # Characters per chunk

    # AI settings
    CONTEXT_MAX_TOKENS: int = 4000

    def __post_init__(self):
        """Load from environment."""
        self.INDEX_ROOT = os.getenv("CHATBOT_INDEX_ROOT", self.INDEX_ROOT)
        self.MAX_RESULTS = int(os.getenv("CHATBOT_MAX_RESULTS", self.MAX_RESULTS))


# Global settings instance
settings = ChatbotSettings()
