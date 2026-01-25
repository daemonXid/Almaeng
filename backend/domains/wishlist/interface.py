"""
🔑 Public Interface - Wishlist Domain

Other domains should ONLY import from here, never from internal files.
Uses Pydantic schemas for type-safe inter-domain communication.

Usage:
    from domains.wishlist.interface import (
        # your exports here
    )
"""

from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


# =============================================================================
# 📋 Pydantic Schemas
# =============================================================================

class WishlistSchema(BaseModel):
    """Schema for wishlist data transfer."""
    id: int
    name: str
    # Add fields as needed

    class Config:
        from_attributes = True


# =============================================================================
# 📖 Read Operations (from selectors.py)
# =============================================================================

# from .selectors import (
#     # Export read functions here
# )


# =============================================================================
# 🔧 Write Operations (from services.py)
# =============================================================================

# from .services import (
#     # Export write functions here
# )


# =============================================================================
# 📋 Explicit Public API
# =============================================================================

__all__ = [
    "WishlistSchema",
    # Add public functions
]
