from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from ...interface import get_user_wishlist, mark_alert_as_read, toggle_wishlist


def index(request: HttpRequest) -> HttpResponse:
    """찜 목록 페이지"""
    from ...interface import get_user_price_alerts

    sort_by = request.GET.get("sort", "created")  # created, price, name
    wishlist_items = list(get_user_wishlist(user_id=request.user.id))

    # Apply sorting
    if sort_by == "price":
        wishlist_items = sorted(wishlist_items, key=lambda x: x.price)
    elif sort_by == "name":
        wishlist_items = sorted(wishlist_items, key=lambda x: x.name.lower())
    # created is default (already sorted by -created_at in get_user_wishlist)

    # Get price alerts for wishlist items (only unread for display)
    price_alerts = get_user_price_alerts(request.user.id, unread_only=True)
    alert_map = {alert.wishlist_item.id: alert for alert in price_alerts if alert.wishlist_item.id}

    return render(
        request,
        "wishlist/pages/index/index.html",
        {
            "wishlist_items": wishlist_items,
            "alert_map": alert_map,
            "sort_by": sort_by,
        },
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
    is_added, _message = toggle_wishlist(
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


@login_required
@require_POST
def dismiss_alert(request: HttpRequest, alert_id: int) -> HttpResponse:
    """Dismiss price alert"""
    success = mark_alert_as_read(alert_id, request.user.id)
    return HttpResponse(status=200 if success else 404)
