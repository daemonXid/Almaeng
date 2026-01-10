"""
🌐 daemon Views - HTMX Endpoints

This module provides HTMX-friendly views that return HTML fragments.
Following the HATEOAS principle: Server returns HTML, not JSON.

Usage:
    # In urls.py
    from domains.daemon.views import home, htmx_counter

    urlpatterns = [
        path("", home, name="home"),
        path("htmx/counter/", htmx_counter, name="htmx_counter"),
    ]
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

# =============================================================================
# 📄 Page Views (Full HTML)
# =============================================================================


def home(request: HttpRequest) -> HttpResponse:
    """
    ALMAENG Home page - Landing page with hero and features.
    """
    return render(
        request,
        "core/pages/home/home.html",
        {
            "page_title": "ALMAENG | 영양제 성분 비교 서비스",
        },
    )


def getting_started(request: HttpRequest) -> HttpResponse:
    """
    Getting Started documentation page.
    """
    return render(
        request,
        "core/pages/getting_started/getting_started.html",
        {
            "page_title": "Getting Started | DAEMON-ONE",
        },
    )


def modules_list(request: HttpRequest) -> HttpResponse:
    """
    Display all registered project domains categorized by purpose.
    """
    project_apps = getattr(settings, "PROJECT_APPS", [])

    categories = {
        "Identity & Access": [],
        "AI & Intelligence": [],
        "Core Infrastructure": [],
        "Business & Growth": [],
        "Custom Extensions": [],
    }

    for app in project_apps:
        app_lower = app.lower()
        if any(key in app_lower for key in ["accounts", "auth", "profile", "oauth"]):
            categories["Identity & Access"].append(app)
        elif "ai." in app_lower or "chatbot" in app_lower or "providers" in app_lower:
            categories["AI & Intelligence"].append(app)
        elif any(key in app_lower for key in ["core", "health", "tasks", "media", "registry", "monitoring"]):
            categories["Core Infrastructure"].append(app)
        elif any(key in app_lower for key in ["analytics", "seo", "marketing", "commerce", "manual"]):
            categories["Business & Growth"].append(app)
        elif "custom." in app_lower:
            categories["Custom Extensions"].append(app)
        else:
            categories["Core Infrastructure"].append(app)

    # Process names for display and remove empty categories
    processed_categories = {}
    for cat_name, apps in categories.items():
        if not apps:
            continue

        domain_list = []
        for app in apps:
            # Create a clean display name (e.g., domains.base.core -> Core, domains.ai.service.chatbot -> AI > Chatbot)
            display_name = app.replace("domains.", "").replace(".", " > ").title()
            domain_list.append(
                {
                    "path": app,
                    "display_name": display_name,
                    "is_core": any(k in app.lower() for k in ["core", "accounts", "ai", "health"]),
                }
            )
        processed_categories[cat_name] = domain_list

    return render(
        request,
        "core/pages/domains_list/domains_list.html",
        {
            "page_title": "Domains | DAEMON-ONE",
            "categories": processed_categories,
        },
    )


# =============================================================================
# ⚡ HTMX Fragment Views (Partial HTML)
# =============================================================================


@require_GET
def htmx_time(request: HttpRequest) -> HttpResponse:
    """
    Return current server time as HTML fragment.

    Usage:
        <button hx-get="/htmx/time/" hx-target="#time-display">
            Get Server Time
        </button>
        <div id="time-display"></div>
    """
    from datetime import datetime

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return HttpResponse(f"""
        <div class="glass-card" style="padding: 1rem; display: inline-block;">
            <span style="color: var(--accent-purple);">🕐</span>
            <strong>{current_time}</strong>
        </div>
    """)


@require_POST
def htmx_counter(request: HttpRequest) -> HttpResponse:
    """
    Increment/decrement counter via HTMX.

    Usage:
        <div hx-target="this" hx-swap="outerHTML">
            <button hx-post="/htmx/counter/" hx-vals='{"action": "increment", "count": 5}'>
                Count: 5
            </button>
        </div>
    """
    action = request.POST.get("action", "increment")
    count = int(request.POST.get("count", 0))

    if action == "increment":
        count += 1
    elif action == "decrement":
        count -= 1

    return HttpResponse(f"""
        <div class="glass-card" style="padding: 1rem; display: flex; gap: 1rem; align-items: center;">
            <button
                hx-post="/htmx/counter/"
                hx-vals='{{"action": "decrement", "count": {count}}}'
                hx-target="closest div"
                hx-swap="outerHTML"
                class="badge" style="cursor: pointer; padding: 0.5rem 1rem;">
                ➖
            </button>
            <span class="gradient-text" style="font-size: 1.5rem; font-weight: bold;">
                {count}
            </span>
            <button
                hx-post="/htmx/counter/"
                hx-vals='{{"action": "increment", "count": {count}}}'
                hx-target="closest div"
                hx-swap="outerHTML"
                class="badge" style="cursor: pointer; padding: 0.5rem 1rem;">
                ➕
            </button>
        </div>
    """)


@require_GET
def htmx_search(request: HttpRequest) -> HttpResponse:
    """
    Live search with HTMX.

    Usage:
        <input type="search"
               name="q"
               hx-get="/htmx/search/"
               hx-trigger="keyup changed delay:300ms"
               hx-target="#search-results">
        <div id="search-results"></div>
    """
    query = request.GET.get("q", "").strip().lower()

    # Sample data (replace with actual database query)
    items = [
        {"icon": "🐍", "name": "Python", "desc": "Backend language"},
        {"icon": "🦀", "name": "Rust", "desc": "High-performance core"},
        {"icon": "⚡", "name": "HTMX", "desc": "Hypermedia AJAX"},
        {"icon": "🏔️", "name": "Alpine.js", "desc": "Lightweight reactivity"},
        {"icon": "🎨", "name": "Tailwind", "desc": "Utility-first CSS"},
        {"icon": "🐘", "name": "PostgreSQL", "desc": "Database"},
        {"icon": "🔴", "name": "Redis", "desc": "Cache & Queue"},
    ]

    if query:
        items = [item for item in items if query in item["name"].lower() or query in item["desc"].lower()]

    if not items:
        return HttpResponse("""
            <div style="padding: 1rem; color: var(--text-secondary);">
                No results found
            </div>
        """)

    results_html = "".join(
        [
            f"""
        <div class="glass-card" style="padding: 0.75rem; margin-bottom: 0.5rem; display: flex; gap: 0.75rem; align-items: center;">
            <span style="font-size: 1.25rem;">{item["icon"]}</span>
            <div>
                <strong style="color: var(--text-primary);">{item["name"]}</strong>
                <p style="font-size: 0.75rem; color: var(--text-secondary); margin: 0;">{item["desc"]}</p>
            </div>
        </div>
        """
            for item in items
        ]
    )

    return HttpResponse(results_html)


@require_GET
def htmx_toast(request: HttpRequest) -> HttpResponse:
    """
    Trigger a toast notification via HTMX OOB swap.

    Usage:
        <button hx-get="/htmx/toast/?message=Hello&type=success">
            Show Toast
        </button>
    """
    message = request.GET.get("message", "Notification")
    toast_type = request.GET.get("type", "info")

    icons = {
        "success": "✅",
        "error": "❌",
        "info": "ℹ️",
        "warning": "⚠️",
    }
    icon = icons.get(toast_type, "ℹ️")

    # OOB = Out of Band swap (updates element outside hx-target)
    return HttpResponse(f"""
        <div id="toast-container"
             hx-swap-oob="true"
             style="
                position: fixed;
                bottom: 2rem;
                right: 2rem;
                padding: 1rem 1.5rem;
                border-radius: 0.75rem;
                background: rgba(0, 0, 0, 0.9);
                border: 1px solid var(--accent-purple);
                backdrop-filter: blur(10px);
                color: #f1f5f9;
                font-size: 0.875rem;
                z-index: 1000;
                animation: slideIn 0.3s ease;
             ">
            {icon} {message}
        </div>
        <style>
            @keyframes slideIn {{
                from {{ transform: translateX(100%); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
        </style>
    """)
