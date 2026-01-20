"""
🏗️ Abstract Base Models - DAEMON Core

These models are designed to be inherited by all other domains.
They provide common fields like timestamps and soft delete.

Usage:
    from domains.base.core.models import TimestampedModel, SoftDeleteModel

    class MyModel(TimestampedModel):
        name = models.CharField(max_length=100)
"""

from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Abstract model with created_at and updated_at timestamps.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



