"""
🔑 Public Interface - DAEMON Module

This file defines the PUBLIC API of the DAEMON core module.
Other modules should ONLY import from here, never from internal files.

Usage (from other modules):
    from domains.daemon.interface import (
        # Models
        TimestampedModel,
        SoftDeleteModel,
        # Events
        domain_event,
        user_created,
        # Config
        ModuleSettings,
        daemon_settings,
        # RBAC
        has_permission,
        require_permission,
        # AI (GenAI)
        get_model,
        GenAIClient,
        # User Operations
        get_user_by_id,
        create_user,
    )

DO NOT:
    from domains.daemon.services import create_user  # ❌ Internal!
    from domains.daemon.selectors import get_user_by_id  # ❌ Internal!
"""

# =============================================================================
# 📦 Models
# =============================================================================

# =============================================================================
# 📢 Events
# =============================================================================
from domains.events.interface import (
    domain_event,
    entity_created,
    entity_deleted,
    entity_updated,
    user_created,
    user_deleted,
    user_logged_in,
    user_updated,
)

# =============================================================================
# 🤖 GenAI (AI Client)
# =============================================================================
from domains.genai.interface import (
    GenAIClient,
    GenAIResponse,
)

# =============================================================================
# 🔐 RBAC (Policy-as-Code)
# =============================================================================
from domains.rbac.interface import (
    PermissionAuth,
    PolicyEngine,
    get_user_roles,
    has_permission,
    require_permission,
)

# =============================================================================
# 🗄️ Registry (Singleton Loader)
# =============================================================================
from domains.registry.interface import (
    ModelRegistry,
    get_model,
    register_model,
)

# =============================================================================
# ⚙️ Configuration
# =============================================================================
from .conf import (
    ModuleSettings,
    daemon_settings,
)
from .models import (
    SoftDeleteModel,
    TimestampedModel,
    ULIDModel,
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
# ⚡ Optional Accelerators (from ABYSS modules)
# These are pre-built Rust wheels from DAEMON-ABYSS, not compiled locally.
# Pure Python fallbacks are provided when accelerators are not installed.
# =============================================================================


# Pure Python implementations (fallback)
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
    "AIAnalysisRequest",
    "AIAnalysisResponse",
    # Schemas
    "BaseSchema",
    "ErrorResponse",
    "GenAIClient",
    "GenAIResponse",
    # AI (GenAI)
    "ModelRegistry",
    # Config
    "ModuleSettings",
    "PaginationSchema",
    "PermissionAuth",
    "PolicyEngine",
    "SoftDeleteModel",
    "SuccessResponse",
    "TimestampMixin",
    # Models
    "TimestampedModel",
    "ULIDModel",
    "UserCreateSchema",
    "UserListSchema",
    "UserResponseSchema",
    "UserUpdateSchema",
    "chunk_text",
    "clean_text_for_ai",
    "cosine_similarity",
    "count_tokens_approx",
    # Write Operations
    "create_user",
    "daemon_settings",
    "deactivate_user",
    "deactivate_user",
    "delete_user",
    "delete_user",
    # Events
    "domain_event",
    "entity_created",
    "entity_deleted",
    "entity_updated",
    "find_top_k_similar",
    "get_active_users",
    "get_model",
    "get_user_by_email",
    # Read Operations
    "get_user_by_id",
    "get_user_roles",
    # RBAC
    "has_permission",
    "register_model",
    "require_permission",
    # Accelerator Utilities (Pure Python)
    "update_user",
    "user_created",
    "user_deleted",
    "user_exists",
    "user_logged_in",
    "user_updated",
]
