"""
💪 Calculator Domain Interface

Public API for body calculator functionality.
External domains should only import from this file.
"""

from .logic.schemas import (
    ActivityLevel,
    BodyInput,
    Gender,
    Goal,
    NutritionResult,
)
from .logic.services import calculate_nutrition

__all__ = [
    "ActivityLevel",
    # Schemas (Public Types)
    "BodyInput",
    "Gender",
    "Goal",
    "NutritionResult",
    # Services (Public Functions)
    "calculate_nutrition",
]
