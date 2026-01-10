"""
🎯 AI Recommendations Interface
"""

from .services import (
    get_ai_ingredient_analysis,
    get_health_quiz_recommendations,
    get_personalized_recommendations,
    get_similar_products,
)

__all__ = [
    "get_ai_ingredient_analysis",
    "get_health_quiz_recommendations",
    "get_personalized_recommendations",
    "get_similar_products",
]
