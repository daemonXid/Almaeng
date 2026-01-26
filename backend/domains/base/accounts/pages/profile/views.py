"""
🌐 Auth Views

Custom views for user profile.
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """User profile page with image upload."""
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_image" and request.FILES.get("profile_image"):
            request.user.profile_image = request.FILES["profile_image"]
            request.user.save(update_fields=["profile_image"])
            return redirect("auth:profile")

    # 세션에서 최근 본 상품 로드
    recent_products = request.session.get("recent_products", [])

    # 찜 목록 개수 조회
    from domains.wishlist.interface import get_user_wishlist

    wishlist_count = get_user_wishlist(request.user.id).count()

    # 검색 히스토리 조회
    from domains.search.interface import get_user_search_history

    search_history = get_user_search_history(request.user.id, limit=10)

    return render(
        request,
        "accounts/pages/profile/profile.html",
        {
            "recent_products": recent_products,
            "wishlist_count": wishlist_count,
            "search_history": search_history,
        },
    )
