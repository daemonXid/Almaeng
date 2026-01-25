"""
Wishlist Template Tags
"""

from django import template

from ..interface import get_user_price_alerts

register = template.Library()


@register.simple_tag
def get_price_alerts(user_id: int, unread_only: bool = True):
    """Get price alerts for user"""
    if not user_id:
        return []
    return get_user_price_alerts(user_id, unread_only=unread_only)


@register.filter
def get_item(dictionary, key):
    """Get value from dictionary by key"""
    if dictionary is None:
        return None
    return dictionary.get(key, None)
