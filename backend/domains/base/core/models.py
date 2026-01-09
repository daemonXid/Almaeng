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


class SoftDeleteManager(models.Manager):
    """Manager that filters out soft-deleted records by default."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(TimestampedModel):
    """
    Abstract model with soft delete capability.
    Records are not actually deleted, just marked with deleted_at.
    """

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Includes deleted records

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete: set deleted_at instead of actual deletion."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """Actually delete the record from database."""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at", "updated_at"])

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class ULIDModel(models.Model):
    """
    Abstract model using ULID as primary key.
    Provides sortable, unique identifiers.
    """

    # Note: Requires django-ulid package
    # id = ULIDField(primary_key=True, editable=False)

    class Meta:
        abstract = True
