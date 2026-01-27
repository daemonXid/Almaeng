"""
🛒 AI 쇼핑 도우미 URL Configuration

Routes are organized as:
- /           → Home page (검색 UI)
- /search/    → Search domain (자연어 검색 API)
- /compare/   → Compare domain (가격 비교)
- /billing/   → Billing domain (결제)
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
    title="AI 쇼핑 도우미 API",
    description="External API endpoints for AI Shopping Assistant",
    version="1.0.0",
)

urlpatterns = [
    # 🔍 SEO - robots.txt, sitemap.xml
    path("", include("domains.features.seo.urls")),
    # 🔍 Search - Home & Main Page
    path("", include("domains.search.urls")),
    # 🏠 Core - Policies
    path("core/", include("domains.base.core.urls")),
    # 🤖 AI Chatbot
    path("chat/", include("domains.ai.service.chatbot.urls")),
    # 🏥 Health Check
    path("health/", include("domains.base.health.urls")),
    # ❤️ Wishlist
    path("wishlist/", include("domains.wishlist.urls")),
    # Admin
    path("admin/", admin.site.urls),
    # External API
    path("api/", api.urls),
]


# Development-only routes
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
