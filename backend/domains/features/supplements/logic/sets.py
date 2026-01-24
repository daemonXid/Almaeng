"""
🧬 Ingredient Sets - Value Analysis Logic

Groups products by ingredient composition and calculates value scores.

Usage:
    from .sets import (
        get_primary_ingredient,
        calculate_value_metrics,
    )
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal

from .parser import TARGET_NUTRIENTS, extract_ingredients, extract_nutrient_content

logger = logging.getLogger(__name__)


@dataclass
class ValueMetrics:
    """Value analysis result for a product."""
    
    primary_ingredient: str
    amount_per_serving: Decimal
    unit: str
    unit_cost: Decimal  # Price per mg/IU
    percentile: int  # 0-100, higher is better value
    rank_label: str  # "🏆 Top 10%", "✅ Good Value", etc.


def get_primary_ingredient(product) -> str | None:
    """
    Identify the primary (main) ingredient of a product.
    
    Strategy:
    1. Check `functionality` field for known nutrients.
    2. Fall back to first detected nutrient in `raw_materials`.
    
    Args:
        product: MFDSHealthFood instance
        
    Returns:
        Primary ingredient name or None if not identifiable.
    """
    # Priority 1: Check functionality text
    if product.functionality:
        for nutrient in TARGET_NUTRIENTS:
            if nutrient in product.functionality:
                return nutrient
    
    # Priority 2: Check raw materials
    if product.raw_materials:
        ingredients = extract_ingredients(product.raw_materials)
        if ingredients:
            return ingredients[0]  # First match (alphabetically sorted)
    
    # Priority 3: Check standard field
    if product.standard:
        for nutrient in TARGET_NUTRIENTS:
            if nutrient in product.standard:
                return nutrient
    
    return None


def get_ingredient_set_id(product) -> str:
    """
    Generate a unique Set ID from sorted ingredient list.
    
    Example: "calcium+magnesium+vitamind" or "lutein"
    """
    raw_text = f"{product.raw_materials or ''} {product.standard or ''}"
    ingredients = extract_ingredients(raw_text)
    
    if not ingredients:
        return "unknown"
    
    # Create normalized ID
    normalized = [i.lower().replace(" ", "") for i in ingredients]
    return "+".join(sorted(normalized))


def calculate_value_metrics(
    product,
    price: Decimal | int | float,
    servings: int = 30,
) -> ValueMetrics | None:
    """
    Calculate value metrics for a product.
    
    Args:
        product: MFDSHealthFood instance
        price: Product price (KRW)
        servings: Estimated number of servings (default 30 days)
        
    Returns:
        ValueMetrics with unit cost and ranking, or None if calculation fails.
    """
    if not price or price <= 0:
        return None
    
    price = Decimal(str(price))
    
    # Find primary ingredient
    primary = get_primary_ingredient(product)
    if not primary:
        logger.debug(f"No primary ingredient found for {product.product_name}")
        return None
    
    # Extract content from standard or raw_materials
    raw_text = f"{product.standard or ''} {product.raw_materials or ''}"
    content_info = extract_nutrient_content(raw_text, primary)
    
    if not content_info:
        logger.debug(f"Could not extract content for {primary} in {product.product_name}")
        return None
    
    amount = content_info["amount"]
    unit = content_info["unit"]
    
    if amount <= 0:
        return None
    
    # Calculate unit cost (price per unit of active ingredient)
    total_active = amount * servings
    unit_cost = price / total_active
    
    # Calculate percentile (MVP: simple heuristic based on unit cost)
    # Lower unit cost = better value = higher percentile
    # TODO: In production, compare against DB averages
    percentile = _estimate_percentile(unit_cost, unit)
    
    # Generate rank label
    if percentile >= 90:
        rank_label = "🏆 Top 10%"
    elif percentile >= 70:
        rank_label = "✅ 상위 30%"
    elif percentile >= 50:
        rank_label = "👍 평균 이상"
    else:
        rank_label = "📊 가성비 분석"
    
    return ValueMetrics(
        primary_ingredient=primary,
        amount_per_serving=amount,
        unit=unit,
        unit_cost=unit_cost.quantize(Decimal("0.01")),
        percentile=percentile,
        rank_label=rank_label,
    )


def _estimate_percentile(unit_cost: Decimal, unit: str) -> int:
    """
    Estimate value percentile based on unit cost.
    
    MVP: Uses simple thresholds. 
    Production: Would query DB for actual distribution.
    """
    # Heuristic thresholds (KRW per unit)
    # These are rough estimates and should be calibrated with real data
    thresholds = {
        "mg": {  # For vitamins/minerals measured in mg
            "excellent": Decimal("1"),    # < 1원/mg = top tier
            "good": Decimal("5"),         # < 5원/mg = good
            "average": Decimal("15"),     # < 15원/mg = average
        },
        "ug": {  # For vitamins measured in mcg (B12, D, etc)
            "excellent": Decimal("10"),
            "good": Decimal("50"),
            "average": Decimal("150"),
        },
        "iu": {  # For vitamins measured in IU
            "excellent": Decimal("0.5"),
            "good": Decimal("2"),
            "average": Decimal("5"),
        },
    }
    
    # Get thresholds for unit (default to mg)
    unit_lower = unit.lower()
    if unit_lower in ("mcg", "μg"):
        unit_lower = "ug"
    
    thresh = thresholds.get(unit_lower, thresholds["mg"])
    
    if unit_cost <= thresh["excellent"]:
        return 95  # Top 5%
    elif unit_cost <= thresh["good"]:
        return 75  # Top 25%
    elif unit_cost <= thresh["average"]:
        return 50  # Average
    else:
        return 25  # Below average


__all__ = [
    "ValueMetrics",
    "get_primary_ingredient",
    "get_ingredient_set_id",
    "calculate_value_metrics",
]
