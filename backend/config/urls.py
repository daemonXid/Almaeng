"""
😈 ALMAENG URL Configuration

Routes are organized as:
- /           → daemon module (home, htmx endpoints)
- /admin/     → Django admin
- /api/       → Ninja API (for external integrations)
- /accounts/  → Allauth authentication
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from ninja_extra import NinjaExtraAPI

# API for external integrations (3rd party, mobile apps)
api = NinjaExtraAPI(
    title="ALMAENG API",
    description="External API endpoints for ALMAENG",
    version="0.1.0",
)

urlpatterns = [
    # 😈 Core domain - Home & HTMX endpoints
    path("", include("domains.base.core.urls")),
    # 🏥 Health checks - Kubernetes/Docker/LB probes
    path("health/", include("domains.base.health.urls")),
    # 🤖 AI Chatbot - Project-aware AI assistant
    path("chatbot/", include("domains.ai.service.chatbot.urls")),
    # 📊 Analytics domain
    path("analytics/", include("domains.base.analytics.urls")),
    # Admin
    path("admin/", admin.site.urls),
    # External API (Ninja)
    path("api/", api.urls),
    # 👤 Custom auth views (profile, etc.)
    path("accounts/", include("domains.base.accounts.urls")),
    # Authentication (Allauth)
    path("accounts/", include("allauth.urls")),
]


# Development-only routes
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
