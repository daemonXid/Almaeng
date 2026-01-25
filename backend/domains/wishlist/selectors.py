"""
📖 Selectors - Read Operations (R)

Query logic for reading data.
Optimize with select_related, prefetch_related.

Usage:
    from domains.wishlist.selectors import get_example_by_id
"""

from typing import List, Optional


# def get_example_by_id(*, example_id: int) -> Optional[Example]:
#     """
#     Get example by ID.
#
#     Args:
#         example_id: Example primary key
#
#     Returns:
#         Example instance or None
#     """
#     try:
#         return Example.objects.get(id=example_id)
#     except Example.DoesNotExist:
#         return None
