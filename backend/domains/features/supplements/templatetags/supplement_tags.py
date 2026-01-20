from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

@register.filter
@stringfilter
def format_functionality(value):
    """
    Formats the functionality text by adding line breaks before numbered items.
    Converts "1. AAA 2. BBB" to:
    1. AAA
    2. BBB
    """
    if not value:
        return ""
    
    # Replace "1. ", "2. " (at start or preceded by space) with "\n1. "
    # But strictly, the user data might be "1.기능성...2.기능성..."
    # Regex: Look for digit + dot + space/content
    # Try to maximize readability
    
    # 1. Split by pattern `(\d+\.)`
    parts = re.split(r'(\d+\.)', value)
    
    if len(parts) <= 1:
        return value
        
    # Reassemble with newlines
    result = []
    
    # The first part is usually empty if string starts with "1."
    # parts: ['', '1.', ' content...', '2.', ' content...']
    
    current_line = ""
    for i, part in enumerate(parts):
        if re.match(r'\d+\.', part):
            # It's a number bullet
            if current_line:
                result.append(current_line.strip())
            current_line = part
        else:
            # It's content
            current_line += " " + part
            
    if current_line:
        result.append(current_line.strip())
        
    return "\n".join(result)
