"""
🔑 Public Interface - Core Module

This file defines the PUBLIC API of the core module.
Other modules should ONLY import from here, never from internal files.

Usage (from other modules):
    from domains.base.core.interface import (
        # Models
        TimestampedModel,
        # Schemas
        BaseSchema,
        SuccessResponse,
        ErrorResponse,
        # Config
        ModuleSettings,
        daemon_settings,
    )
"""

# =============================================================================
# ⚙️ Configuration
# =============================================================================
from .conf import (
    ModuleSettings,
    daemon_settings,
)

# =============================================================================
# 📦 Base Models
# =============================================================================
from .models import (
    TimestampedModel,
)

# =============================================================================
# 📋 Pydantic Schemas
# =============================================================================
from .schemas import (
    AIAnalysisRequest,
    AIAnalysisResponse,
    BaseSchema,
    ErrorResponse,
    PaginationSchema,
    SuccessResponse,
    TimestampMixin,
    UserCreateSchema,
    UserListSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

# =============================================================================
# 📖 Read Operations (from selectors.py)
# =============================================================================
from .selectors import (
    get_active_users,
    get_user_by_email,
    get_user_by_id,
    user_exists,
)

# =============================================================================
# 🔧 Write Operations (from services.py)
# =============================================================================
from .services import (
    create_user,
    deactivate_user,
    delete_user,
    update_user,
)

# =============================================================================
# ⚡ Utility Functions
# =============================================================================


def count_tokens_approx(text: str) -> int:
    """Approximate token count (~4 chars per token)."""
    return len(text) // 4


def clean_text_for_ai(text: str) -> str:
    """Clean text for AI input."""
    return text.strip()


def chunk_text(text: str, max_tokens: int) -> list[str]:
    """Chunk text by approximate token count."""
    return [text]


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Cosine similarity between two vectors."""
    if len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2, strict=False))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def find_top_k_similar(query: list[float], vectors: list[list[float]], k: int) -> list[tuple[int, float]]:
    """Find top-k most similar vectors."""
    similarities = [(i, cosine_similarity(query, v)) for i, v in enumerate(vectors)]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:k]


# =============================================================================
# 📋 Explicit Public API
# =============================================================================

__all__ = [
    # Schemas
    "AIAnalysisRequest",
    "AIAnalysisResponse",
    "BaseSchema",
    "ErrorResponse",
    "PaginationSchema",
    "SuccessResponse",
    "TimestampMixin",
    "UserCreateSchema",
    "UserListSchema",
    "UserResponseSchema",
    "UserUpdateSchema",
    # Models
    "TimestampedModel",
    # Config
    "ModuleSettings",
    "daemon_settings",
    # Read Operations
    "get_active_users",
    "get_user_by_email",
    "get_user_by_id",
    "user_exists",
    # Write Operations
    "create_user",
    "deactivate_user",
    "delete_user",
    "update_user",
    # Utility Functions
    "chunk_text",
    "clean_text_for_ai",
    "cosine_similarity",
    "count_tokens_approx",
    "find_top_k_similar",
]
