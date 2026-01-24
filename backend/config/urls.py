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

# Register domain routers
from domains.features.payments.api import router as payments_router
from ninja import ConfigError

# Prevent duplicate router registration
try:
    api.add_router("/payments/", payments_router)
except ConfigError:
    # Router already registered, skip silently
    pass

urlpatterns = [
    # 🔍 SEO - robots.txt, sitemap.xml (must be at root level)
    path("", include("domains.features.seo.urls")),
    # 😈 Core domain - Home & HTMX endpoints
    path("", include("domains.base.core.urls")),
    # 🏥 Health checks - Kubernetes/Docker/LB probes
    path("health/", include("domains.base.health.urls")),
    # 🤖 AI Chatbot - Project-aware AI assistant
    path("chatbot/", include("domains.ai.service.chatbot.urls")),
    # 🎯 AI Recommendations - Personalized supplement suggestions
    path("recommend/", include("domains.ai.recommendations.urls")),
    # 📊 Analytics domain
    path("analytics/", include("domains.base.analytics.urls")),
    # 💊 Supplements - Products, ingredients, OCR
    path("supplements/", include("domains.features.supplements.urls")),
    # 💰 Prices - Price tracking, history, alerts
    path("prices/", include("domains.features.prices.urls")),
    # 🛒 Cart - Shopping cart
    path("cart/", include("domains.features.cart.urls")),
    # ❤️ Wishlist - Favorites
    path("wishlist/", include("domains.features.wishlist.urls")),
    # 💳 Payments - Toss checkout
    path("payments/", include("domains.features.payments.urls")),
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
