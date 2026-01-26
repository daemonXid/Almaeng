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
    # 🔍 SEO - robots.txt, sitemap.xml (must be at root level)
    path("", include("domains.features.seo.urls")),
    # 🔍 Search - Home & Main Page (검색이 홈페이지)
    path("", include("domains.search.urls")),
    # 🏠 Core domain - Base pages
    path("core/", include("domains.base.core.urls")),
    # 🤖 AI Chatbot - Gemini 챗봇
    path("chat/", include("domains.ai.service.chatbot.urls")),
    # 🏥 Health checks - Kubernetes/Docker/LB probes
    path("health/", include("domains.base.health.urls")),
    # 💳 Billing - 결제
    path("billing/", include("domains.billing.urls")),
    # ❤️ Wishlist - 찜 목록
    path("wishlist/", include("domains.wishlist.urls")),
    # 💳 Toss Payments Webhook
    path("toss/webhook/", include("domains.integrations.tosspayments.urls")),
    # 🔔 Notifications
    path("notifications/", include("domains.base.notifications.urls")),
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
