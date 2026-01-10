"""
❤️ Wishlist Page Views
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from ...services import get_user_wishlist, toggle_wishlist


@login_required
def wishlist_page(request: HttpRequest) -> HttpResponse:
    """찜 목록 페이지"""
    items = get_user_wishlist(request.user.id)

    return render(
        request,
        "wishlist/pages/wishlist/wishlist.html",
        {
            "page_title": "찜 목록 | ALMAENG",
            "items": items,
        },
    )


@require_POST
def toggle_wishlist_item(request: HttpRequest, supplement_id: int) -> HttpResponse:
    """HTMX: 찜 토글"""
    if not request.user.is_authenticated:
        return HttpResponse("""
            <button class="text-gray-400" disabled>
                ❤️
            </button>
        """)

    _added, is_in = toggle_wishlist(request.user.id, supplement_id)

    if is_in:
        return HttpResponse(f"""
            <button hx-post="/wishlist/toggle/{supplement_id}/"
                    hx-swap="outerHTML"
                    class="text-rose-500 hover:scale-110 transition-transform">
                ❤️
            </button>
        """)
    else:
        return HttpResponse(f"""
            <button hx-post="/wishlist/toggle/{supplement_id}/"
                    hx-swap="outerHTML"
                    class="text-gray-400 hover:text-rose-500 hover:scale-110 transition-all">
                🤍
            </button>
        """)
