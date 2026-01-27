"""
🔍 SEO Models
"""

from django.db import models
from django_lifecycle import LifecycleModel


class MetaTag(LifecycleModel):
    """
    Dynamic Meta Tags for pages.
    Matches URL patterns to inject custom SEO logic.
    """

    path = models.CharField(max_length=255, unique=True, help_text="URL Path (e.g. /about)")
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.URLField(max_length=500, blank=True, help_text="OG Image URL")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "daemon_seo_metatags"
        verbose_name = "Meta Tag"
        verbose_name_plural = "Meta Tags"

    def __str__(self):
        return self.path


class SitemapItem(LifecycleModel):
    """
    Manual Sitemap entries for non-DB pages.
    """

    loc = models.CharField(max_length=255, unique=True, help_text="Full URL or Path")
    priority = models.FloatField(default=0.5, help_text="0.0 to 1.0")

    CHANGEFREQ_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]
    changefreq = models.CharField(max_length=20, choices=CHANGEFREQ_CHOICES, default="monthly")

    class Meta:
        db_table = "daemon_seo_sitemap"
        verbose_name = "Sitemap Item"
        verbose_name_plural = "Sitemap Items"
