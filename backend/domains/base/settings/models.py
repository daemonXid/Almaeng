"""
⚙️ Site Settings Model

Single-row table for site-wide configuration.
Use the SiteSettings.get() method to retrieve the singleton instance.
"""

from django.core.cache import cache
from django.db import models


class SiteSettings(models.Model):
    """
    Singleton model for site-wide settings.

    Usage:
        settings = SiteSettings.get()
        print(settings.site_name)
    """

    # --- Branding ---
    site_name = models.CharField(
        max_length=100,
        default="DAEMON-ONE",
        help_text="Site display name",
    )
    site_description = models.TextField(
        blank=True,
        default="AI-First Django Template",
        help_text="Short site description",
    )
    logo = models.ImageField(
        upload_to="settings/",
        blank=True,
        null=True,
        help_text="Site logo image",
    )
    favicon = models.ImageField(
        upload_to="settings/",
        blank=True,
        null=True,
        help_text="Favicon image (32x32)",
    )

    # --- SEO Defaults ---
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        default="DAEMON-ONE",
        help_text="Default meta title for pages",
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        default="AI-First Django Template with Hypermedia-Driven Architecture",
        help_text="Default meta description",
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated keywords",
    )

    # --- Contact ---
    contact_email = models.EmailField(
        blank=True,
        help_text="Public contact email",
    )
    support_email = models.EmailField(
        blank=True,
        help_text="Support email address",
    )

    # --- Social ---
    twitter_handle = models.CharField(max_length=50, blank=True)
    github_url = models.URLField(blank=True)
    discord_url = models.URLField(blank=True)

    # --- Feature Flags ---
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Enable maintenance mode",
    )
    allow_registration = models.BooleanField(
        default=True,
        help_text="Allow new user registration",
    )
    enable_ai_features = models.BooleanField(
        default=True,
        help_text="Enable AI-powered features",
    )

    # --- Timestamps ---
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return f"Site Settings ({self.site_name})"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
        # Invalidate cache
        cache.delete("site_settings")

    @classmethod
    def get(cls) -> "SiteSettings":
        """
        Get the singleton SiteSettings instance.

        Creates default settings if none exist.
        Uses caching for performance.
        """
        cached = cache.get("site_settings")
        if cached:
            return cached

        settings, _ = cls.objects.get_or_create(pk=1)
        cache.set("site_settings", settings, timeout=300)  # 5 minutes
        return settings
