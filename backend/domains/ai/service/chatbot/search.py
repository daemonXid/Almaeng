"""
🔍 Search & Answer

Combines file search with AI to answer questions.
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from dataclasses import dataclass

from domains.ai.service.providers.interface import AIResponse, get_ai_client

from .conf import settings
from .indexer import search_files
from .prompts import ANSWER_PROMPT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with file info."""

    file_path: str
    content_preview: str
    relevance: float = 1.0


@dataclass
class ChatResponse:
    """Response from the chatbot."""

    answer: str
    sources: list[str]
    raw_response: AIResponse | None = None

    @property
    def has_sources(self) -> bool:
        return len(self.sources) > 0


def search_project(query: str) -> list[SearchResult]:
    """
    Search project files for relevant content.

    Args:
        query: Search query

    Returns:
        List of search results with previews
    """
    files = search_files(query)

    results = []
    for f in files:
        # Find the best matching section
        preview = _extract_preview(f.content, query)
        results.append(
            SearchResult(
                file_path=f.path,
                content_preview=preview,
            )
        )

    return results


def _extract_preview(content: str, query: str, context_chars: int = 200) -> str:
    """Extract a preview snippet around the query match."""
    query_lower = query.lower()
    content_lower = content.lower()

    pos = content_lower.find(query_lower)
    if pos == -1:
        # Return start of content if no match
        return content[:context_chars] + "..."

    start = max(0, pos - context_chars // 2)
    end = min(len(content), pos + len(query) + context_chars // 2)

    preview = content[start:end]
    if start > 0:
        preview = "..." + preview
    if end < len(content):
        preview = preview + "..."

    return preview


def ask_question(question: str) -> ChatResponse:
    """
    Ask a question about the project.

    Uses semantic search to find relevant files,
    then uses AI to generate an answer.

    Args:
        question: User's question

    Returns:
        ChatResponse with answer and sources
    """
    # 1. Search for relevant files
    results = search_project(question)
    sources = [r.file_path for r in results]

    if not results:
        return ChatResponse(
            answer="관련 파일을 찾을 수 없습니다. 다른 키워드로 질문해주세요.",
            sources=[],
        )

    # 2. Build context from search results
    context_parts = []
    for result in results[: settings.MAX_RESULTS]:
        context_parts.append(f"### File: {result.file_path}\n```\n{result.content_preview}\n```")

    context = "\n\n".join(context_parts)

    # 3. Generate AI response
    client = get_ai_client()
    prompt = ANSWER_PROMPT.format(context=context, question=question)

    response = client.complete(
        prompt=f"{SYSTEM_PROMPT}\n\n{prompt}",
        temperature=0.3,  # Lower for factual answers
        max_tokens=1500,
    )

    if response.is_empty:
        return ChatResponse(
            answer="AI 응답을 생성할 수 없습니다. API 키를 확인해주세요.",
            sources=sources,
        )

    return ChatResponse(
        answer=response.text,
        sources=sources,
        raw_response=response,
    )


def stream_question(question: str) -> Generator[str, None, None]:
    """
    Stream a project-aware answer.
    """
    results = search_project(question)
    context_parts = []
    for result in results[: settings.MAX_RESULTS]:
        context_parts.append(f"### File: {result.file_path}\n```\n{result.content_preview}\n```")

    context = "\n\n".join(context_parts)
    client = get_ai_client()
    prompt = ANSWER_PROMPT.format(context=context, question=question)

    return client.stream(
        prompt=f"{SYSTEM_PROMPT}\n\n{prompt}",
        temperature=0.3,
        max_tokens=1500,
    )


def explain_file(file_path: str) -> ChatResponse:
    """
    Get an explanation of a specific file.

    Args:
        file_path: Path to the file

    Returns:
        ChatResponse with explanation
    """
    from .indexer import get_indexer

    indexer = get_indexer()
    indexed_file = indexer.get_file(file_path)

    if not indexed_file:
        return ChatResponse(
            answer=f"파일을 찾을 수 없습니다: {file_path}",
            sources=[],
        )

    client = get_ai_client()
    prompt = f"""Explain this file from the DAEMON-ONE project:

File: {file_path}
```
{indexed_file.content[:3000]}
```

Explain what this file does and how to use it.
"""

    response = client.complete(
        prompt=f"{SYSTEM_PROMPT}\n\n{prompt}",
        temperature=0.3,
    )

    return ChatResponse(
        answer=response.text,
        sources=[file_path],
        raw_response=response,
    )
