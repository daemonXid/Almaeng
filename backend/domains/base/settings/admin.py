"""
⚙️ Site Settings Admin

Integrates with Django Unfold for modern admin UI.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    """Admin for site settings with Unfold styling."""

    list_display = ("site_name", "maintenance_mode", "allow_registration", "updated_at")

    fieldsets = (
        (
            "🏷️ Branding",
            {
                "fields": ("site_name", "site_description", "logo", "favicon"),
            },
        ),
        (
            "🔍 SEO Defaults",
            {
                "fields": ("meta_title", "meta_description", "meta_keywords"),
            },
        ),
        (
            "📧 Contact",
            {
                "fields": ("contact_email", "support_email"),
            },
        ),
        (
            "🌐 Social Links",
            {
                "fields": ("twitter_handle", "github_url", "discord_url"),
            },
        ),
        (
            "🎛️ Feature Flags",
            {
                "fields": ("maintenance_mode", "allow_registration", "enable_ai_features"),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False
