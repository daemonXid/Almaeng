"""
⚙️ Site Settings Context Processor

Adds site settings to all template contexts.
"""


def site_settings(request):
    """
    Add site settings to template context.

    Usage in template:
        {{ site.name }}
        {{ site.description }}
        {% if site.maintenance_mode %}...{% endif %}
    """
    from django.conf import settings as django_settings

    from .models import SiteSettings

    settings = SiteSettings.get()

    return {
        "site": {
            "name": settings.site_name,
            "description": settings.site_description,
            "logo": settings.logo,
            "favicon": settings.favicon,
            "meta_title": settings.meta_title,
            "meta_description": settings.meta_description,
            "contact_email": settings.contact_email,
            "twitter": settings.twitter_handle,
            "github": settings.github_url,
            "discord": settings.discord_url,
            "maintenance_mode": settings.maintenance_mode,
            "allow_registration": settings.allow_registration,
            "ai_enabled": settings.enable_ai_features,
        },
        "DEBUG": django_settings.DEBUG,
    }
