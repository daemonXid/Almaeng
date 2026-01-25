from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from ...interface import toggle_wishlist, get_user_wishlist
from ...selectors import is_product_in_wishlist


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """찜 목록 페이지"""
    wishlist_items = get_user_wishlist(user_id=request.user.id)
    return render(
        request,
        "wishlist/pages/index/index.html",
        {"wishlist_items": wishlist_items},
    )


@login_required
@require_POST
def toggle(request: HttpRequest) -> HttpResponse:
    """찜하기 토글 (HTMX 전용)"""
    product_id = request.POST.get("product_id")
    platform = request.POST.get("platform")
    name = request.POST.get("name", "")
    price = int(request.POST.get("price", 0))
    image_url = request.POST.get("image_url", "")
    product_url = request.POST.get("product_url", "")

    if not product_id or not platform:
        return HttpResponse("Invalid Request", status=400)

    # 토글 실행
    is_added, message = toggle_wishlist(
        user_id=request.user.id,
        product_id=product_id,
        platform=platform,
        name=name,
        price=price,
        image_url=image_url,
        product_url=product_url,
    )

    # 변경된 버튼 상태 반환 (HTMX)
    return render(
        request,
        "wishlist/pages/index/_wishlist_button.html",
        {
            "is_in_wishlist": is_added,
            "product": {
                "id": product_id,
                "platform": platform,
                "name": name,
                "price": price,
                "image_url": image_url,
                "product_url": product_url,
            },
        },
    )
