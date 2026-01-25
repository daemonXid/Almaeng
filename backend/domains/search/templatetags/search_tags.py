"""
🔍 Search Template Tags
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get value from dictionary by key"""
    if dictionary is None:
        return False
    return dictionary.get(str(key), False)
