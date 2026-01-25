"""
🔍 Search State Models

Search history model.
"""

from django.db import models


class SearchHistory(models.Model):
    """Search history"""

    user_id = models.IntegerField(db_index=True, null=True, blank=True, verbose_name="User ID")
    query = models.TextField(verbose_name="Original Query")
    keywords = models.JSONField(default=list, verbose_name="Extracted Keywords")
    category = models.CharField(max_length=100, blank=True, verbose_name="Category")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Search History"
        verbose_name_plural = "Search History List"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.query} ({self.created_at})"
