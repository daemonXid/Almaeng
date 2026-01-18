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

    # Safe defaults in case DB is not ready
    defaults = {
        "site": {
            "name": "ALMAENG",
            "description": "AI-Driven Nutrient Comparison",
            "logo": None,
            "favicon": None,
            "meta_title": "ALMAENG",
            "meta_description": "AI-Driven Nutrient Comparison & Price Tracker",
            "contact_email": "",
            "twitter": "",
            "github": "",
            "discord": "",
            "maintenance_mode": False,
            "allow_registration": True,
            "ai_enabled": True,
        },
        "DEBUG": django_settings.DEBUG,
    }

    try:
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
    except Exception:
        # Return defaults if DB is not ready (migrations not run yet)
        return defaults
