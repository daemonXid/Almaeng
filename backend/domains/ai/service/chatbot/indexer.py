"""
🗂️ Project Indexer

Indexes project files for semantic search.
Builds an in-memory index of file contents.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from .conf import settings

logger = logging.getLogger(__name__)


@dataclass
class IndexedFile:
    """Represents an indexed file."""

    path: str
    content: str
    extension: str
    size: int

    @property
    def relative_path(self) -> str:
        """Get path relative to project root."""
        return self.path

    def get_chunks(self, chunk_size: int = 1000) -> list[str]:
        """Split content into chunks for search."""
        chunks = []
        for i in range(0, len(self.content), chunk_size):
            chunks.append(self.content[i : i + chunk_size])
        return chunks


class ProjectIndexer:
    """
    Indexes project files for search.

    Usage:
        indexer = ProjectIndexer()
        indexer.index()
        files = indexer.get_all_files()
    """

    def __init__(self, root_path: str | None = None):
        self.root_path = Path(root_path or settings.INDEX_ROOT)
        self._index: dict[str, IndexedFile] = {}
        self._indexed = False

    def index(self) -> int:
        """
        Index all project files.

        Returns:
            Number of files indexed
        """
        self._index.clear()
        count = 0

        for file_path in self._iter_files():
            try:
                indexed = self._index_file(file_path)
                if indexed:
                    self._index[str(file_path)] = indexed
                    count += 1
            except Exception as e:
                logger.warning(f"Failed to index {file_path}: {e}")

        self._indexed = True
        logger.info(f"📚 Indexed {count} files")
        return count

    def _iter_files(self) -> Iterator[Path]:
        """Iterate over indexable files."""
        for ext in settings.INDEXED_EXTENSIONS:
            for file_path in self.root_path.rglob(f"*{ext}"):
                # Check exclusions
                if self._should_exclude(file_path):
                    continue
                yield file_path

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        path_str = str(path)
        for excluded in settings.EXCLUDED_DIRS:
            if excluded in path_str:
                return True
        return False

    def _index_file(self, path: Path) -> IndexedFile | None:
        """Index a single file."""
        if path.stat().st_size > settings.MAX_FILE_SIZE:
            return None

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return None

        return IndexedFile(
            path=str(path.relative_to(self.root_path.parent)),
            content=content,
            extension=path.suffix,
            size=len(content),
        )

    def get_all_files(self) -> list[IndexedFile]:
        """Get all indexed files."""
        if not self._indexed:
            self.index()
        return list(self._index.values())

    def get_file(self, path: str) -> IndexedFile | None:
        """Get a specific indexed file."""
        return self._index.get(path)

    def search_content(self, query: str) -> list[IndexedFile]:
        """
        Simple text search across all files.

        Args:
            query: Search query

        Returns:
            List of matching files
        """
        if not self._indexed:
            self.index()

        query_lower = query.lower()
        results = []

        for indexed_file in self._index.values():
            if query_lower in indexed_file.content.lower():
                results.append(indexed_file)

        return results[: settings.MAX_RESULTS]


# Global indexer instance
_indexer: ProjectIndexer | None = None


def get_indexer() -> ProjectIndexer:
    """Get or create project indexer."""
    global _indexer
    if _indexer is None:
        _indexer = ProjectIndexer()
    return _indexer


def index_project() -> int:
    """Index the project files."""
    return get_indexer().index()


def search_files(query: str) -> list[IndexedFile]:
    """Search indexed files."""
    return get_indexer().search_content(query)
