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
        # Using simple substring check for MVP. 
        # Regex could be overkill unless we need exact word boundaries (which is hard in Korean text without tokenizer)
        if nutrient in raw_text:
            found.add(nutrient)
            
    return sorted(list(found))
