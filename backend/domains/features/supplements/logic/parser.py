"""
🧬 Ingredient Regex Parser

MFDS Raw Data (Unstructured Text) -> Structured Ingredient List
"""

import re

# Key Nutrients to extracting (MVP List)
TARGET_NUTRIENTS = [
    "비타민A", "비타민B1", "비타민B2", "비타민B6", "비타민B12", "비타민C", "비타민D", "비타민E", "비타민K",
    "엽산", "나이아신", "판토텐산", "비오틴",
    "칼슘", "마그네슘", "철", "아연", "구리", "셀레늄", "요오드", "망간", "몰리브덴", "칼륨",
    "오메가3", "EPA", "DHA", "루테인", "밀크씨슬", "실리마린", "프로바이오틱스", "유산균", "가르시니아",
    "코엔자임Q10", "히알루론산", "MSM", "글루코사민", "쏘팔메토", "테아닌",
]


def extract_ingredients(raw_text: str) -> list[str]:
    """
    Extract target nutrients from raw material text string.
    
    Args:
        raw_text (str): "비타민C, 결정셀룰로스, 스테아린산마그네슘"
    
    Returns:
        list[str]: ["비타민C"] (Unique list)
    """
    if not raw_text:
        return []

    found = set()
    
    # Normalize text (remove whitespace around commas, etc)
    # But simple contains check is robust enough for now
    
    for nutrient in TARGET_NUTRIENTS:
        # Check if the nutrient name exists in the text
        if nutrient in raw_text:
            found.add(nutrient)
            
    return sorted(list(found))


def extract_nutrient_content(raw_materials: str, target_nutrient: str) -> dict | None:
    """
    Extracts nutrient content from raw material string using Regex.
    
    Returns:
        {
            "amount": Decimal("300"),
            "unit": "mg",
            "match": "Magnesium Oxide (Magnesium 300mg)"
        }
    """
    if not raw_materials:
        return None
        
    from decimal import Decimal
    
    # Enhanced Regex for MFDS Formats
    # Common Patterns:
    # 1. "Magnesium (as Oxide) 300mg"
    # 2. "Magnesium Oxide (Magnesium 300mg)"
    # 3. "비타민C(100mg)"
    # 4. "칼슘 (700 mg)"
    # 5. "비타민 D (25ug)"
    
    # Regex Parts:
    # ({target_nutrient}) : Capture name
    # [^0-9()]*? : Skip clutter (non-digits/parens) lazily
    # (?:\([^)]+\))? : Optional inner parens ignored
    # \s*[(]? : Optional opening paren
    # (\d+(?:\.\d+)?) : Capture Amount (Float supported)
    # \s* : Optional space
    # (mg|g|mcg|ug|iu|μg) : Capture Unit
    
    # Try multiple patterns for robustness
    patterns = [
        # Pattern 1: Nutrient ... (Amount Unit) -> 비타민C (100mg)
        rf"({target_nutrient})[^0-9]*?\((\d+(?:\.\d+)?)\s*(mg|g|mcg|ug|iu|μg)\)",
        
        # Pattern 2: Nutrient ... Amount Unit -> 비타민C 100mg (no parens)
        rf"({target_nutrient})[^0-9]*?(\d+(?:\.\d+)?)\s*(mg|g|mcg|ug|iu|μg)",
    ]
    
    for pattern in patterns:
        matches = re.search(pattern, raw_materials, re.IGNORECASE)
        if matches:
            amount_str = matches.group(2)
            unit = matches.group(3).lower()
            if unit == "μg":
                unit = "ug"
                
            return {
                "amount": Decimal(amount_str),
                "unit": unit,
                "match": matches.group(0)
            }
    
    return None


def parse_serving_info(intake_method: str, product_form: str) -> dict:
    """
    Parses intake method and form to estimate servings.
    
    Args:
        intake_method: "1일 1회, 1회 1정 섭취"
        product_form: "캡슐"
        
    Returns:
        {
            "daily_count": 1, 
            "unit": "정",
            "days_supply": 30 (Default guess if unknown)
        }
    """
    if not intake_method:
        return {"daily_count": 1, "unit": "회", "days_supply": 30}
        
    # Extract "1회 X정" or "1회 X캡슐"
    # Regex: 1회\s*(\d+)(정|캡슐|포|g|ml)
    count_match = re.search(r"1회\s*(\d+)\s*(정|캡슐|포|알|g|ml)", intake_method)
    
    daily_count = 1
    unit = "회"
    
    if count_match:
        daily_count = int(count_match.group(1))
        unit = count_match.group(2)
    
    # Try to find "X일 섭취량" or frequency
    # "1일 1회" -> 1 time per day
    # "1일 2회" -> 2 times per day
    freq_match = re.search(r"1일\s*(\d+)회", intake_method)
    daily_freq = int(freq_match.group(1)) if freq_match else 1
    
    total_daily_count = daily_count * daily_freq
    
    return {
        "daily_count": total_daily_count,
        "unit": unit,
        "days_supply": 30 # Default assumption for MVP
    }


def calculate_unit_cost(price: 0, total_servings: int, content_per_serving: 0) -> 0:
    """
    Calculates cost per 1 unit (e.g., 100mg/1g) of active ingredient.
    """
    from decimal import Decimal
    
    p = Decimal(str(price)) if not isinstance(price, Decimal) else price
    content = Decimal(str(content_per_serving)) if not isinstance(content_per_serving, Decimal) else content_per_serving
    
    if content <= 0 or total_servings <= 0:
        return Decimal(0)
    
    # Total active amount in bottle
    total_active_amount = content * total_servings
    
    # Cost per 1 unit of active amount
    return (p / total_active_amount)
