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

    # TODO: 실제 쿠키에서 최근 본 상품 로드
    recent_products = [
        {
            "id": "1",
            "name": "눈 건강에 좋은 루테인 지아잔틴 30캡슐",
            "price": "19,800",
            "image": "https://shopping-phinf.pstatic.net/main_4026601/40266012345.jpg?type=f300",
            "url": "#"
        },
        {
            "id": "2",
            "name": "소니 노이즈캔슬링 헤드폰 WH-1000XM5",
            "price": "458,000",
            "image": "",  # No image test
            "url": "#"
        },
        {
            "id": "3",
            "name": "시디즈 T50 서울대 의자",
            "price": "389,000",
            "image": "",
            "url": "#"
        }
    ]

    return render(
        request, 
        "accounts/pages/profile/profile.html",
        {
            "recent_products": recent_products
        }
    )
