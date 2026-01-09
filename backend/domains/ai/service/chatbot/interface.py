"""
🔑 Public Interface - Chatbot Module

Import from here to use the project-aware chatbot.

Usage:
    from domains.chatbot.interface import (
        ask_question,
        search_project,
        index_project,
    )
"""

from .conf import settings
from .indexer import (
    IndexedFile,
    get_indexer,
    index_project,
    search_files,
)
from .search import (
    ChatResponse,
    SearchResult,
    ask_question,
    explain_file,
    search_project,
    stream_question,
)

__all__ = [
    "ChatResponse",
    "IndexedFile",
    # Types
    "SearchResult",
    # Core functions
    "ask_question",
    "explain_file",
    "get_indexer",
    "index_project",
    # Indexer
    "search_files",
    "search_project",
    # Config
    "settings",
    "stream_question",
]
