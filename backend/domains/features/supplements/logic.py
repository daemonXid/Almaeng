import re
from decimal import Decimal
from typing import Optional

def extract_nutrient_content(raw_materials: str, target_nutrient: str) -> Optional[dict]:
    """
    Extracts nutrient content from raw material string.
    
    Args:
        raw_materials: "Magnesium Oxide (Magnesium 300mg), Zinc..."
        target_nutrient: "Magnesium" or "마그네슘"
        
    Returns:
        {
            "amount": Decimal("300"),
            "unit": "mg",
            "source": "Magnesium Oxide"
        }
    """
    if not raw_materials:
        return None
        
    # Pattern 1: Nutrient followed by amount in parenthesis
    # Ex: "Magnesium Oxide (Magnesium 300mg)"
    # Regex: (Nutrient)\s*(\d+(?:\.\d+)?)\s*(mg|g|mcg|ug)
    
    # We need to map English/Korean if needed, but let's assume raw text query
    # Simple regex for "Nutrient Amount Unit" inside parens
    
    # Check for "Name (AmountUnit)" pattern often found in MFDS
    # e.g., "비타민C(100mg)"
    
    pattern = re.compile(rf"{target_nutrient}\s*\(?.*?(\d+(?:\.\d+)?)\s*(mg|g|mcg|ug)\)?", re.IGNORECASE)
    
    # Scan whole string? 
    # Usually structure is "Source (Nutrient Amount)"
    # Regex: `\([^\)]*?Nutrient\s+(\d+)\s*(mg)[^\)]*?\)`
    # Or just look for `Nutrient\s+(\d+)\s*(mg)`?
    # Risk: "Total weight 500mg" vs "Magnesium 300mg"
    # Safety: Look for the specific nutrient name nearby.
    
    matches = re.search(rf"({target_nutrient})[^,)]*?(\d+(?:\.\d+)?)\s*(mg|g|mcg|ug)", raw_materials, re.IGNORECASE)
    
    if matches:
        amount_str = matches.group(2)
        unit = matches.group(3).lower()
        return {
            "amount": Decimal(amount_str),
            "unit": unit,
            "match": matches.group(0)
        }
    
    return None

def calculate_unit_cost(price: Decimal, total_servings: int, content_per_serving: Decimal) -> Decimal:
    """
    Calculates cost per 1 unit (e.g., 100mg/1g) of active ingredient.
    """
    if content_per_serving <= 0 or total_servings <= 0:
        return Decimal(0)
    
    # Total active amount in bottle
    total_active_amount = content_per_serving * total_servings
    
    # Cost per 1 unit of active amount
    # e.g. 20,000 KRW / (300mg * 60 servings) = 20000 / 18000 = 1.11 KRW per mg
    return (price / total_active_amount).quantize(Decimal("0.01"))
