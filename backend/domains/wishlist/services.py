"""
🔧 Services - Write Operations (CUD)

Business logic for creating, updating, deleting data.
Use @transaction.atomic for data consistency.

Usage:
    from domains.wishlist.services import create_example
"""

from typing import Optional
from django.db import transaction


# @transaction.atomic
# def create_example(*, name: str, description: str = "") -> Example:
#     """
#     Create a new example.
#
#     Args:
#         name: Example name
#         description: Optional description
#
#     Returns:
#         Created Example instance
#     """
#     return Example.objects.create(name=name, description=description)
