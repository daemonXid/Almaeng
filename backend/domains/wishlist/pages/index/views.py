from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


def index(request: HttpRequest) -> HttpResponse:
    """
    찜 목록 페이지 (세션 기반)
    
    앱인토스 출시 시 Toss 사용자 ID 사용 예정
    현재는 세션 기반으로 간단하게 구현
    """
    # 세션에서 찜 목록 가져오기
    wishlist_items = request.session.get("wishlist", [])
    sort_by = request.GET.get("sort", "created")

    # Apply sorting
    if sort_by == "price":
        wishlist_items = sorted(wishlist_items, key=lambda x: x.get("price", 0))
    elif sort_by == "name":
        wishlist_items = sorted(wishlist_items, key=lambda x: x.get("name", "").lower())

    return render(
        request,
        "wishlist/pages/index/index.html",
        {
            "wishlist_items": wishlist_items,
            "alert_map": {},  # 가격 알림은 Phase 2
            "sort_by": sort_by,
        },
    )


@require_POST
def toggle(request: HttpRequest) -> HttpResponse:
    """찜하기 토글 (세션 기반)"""
    product_id = request.POST.get("product_id")
    platform = request.POST.get("platform")
    name = request.POST.get("name", "")
    price = int(request.POST.get("price", 0))
    image_url = request.POST.get("image_url", "")
    product_url = request.POST.get("product_url", "")

    if not product_id or not platform:
        return HttpResponse("Invalid Request", status=400)

    # 세션에서 찜 목록 가져오기
    wishlist = request.session.get("wishlist", [])
    
    # 이미 있는지 확인
    existing = next((item for item in wishlist if item["id"] == product_id and item["platform"] == platform), None)
    
    if existing:
        # 제거
        wishlist = [item for item in wishlist if not (item["id"] == product_id and item["platform"] == platform)]
        is_added = False
    else:
        # 추가
        wishlist.append({
            "id": product_id,
            "platform": platform,
            "name": name,
            "price": price,
            "image_url": image_url,
            "product_url": product_url,
        })
        is_added = True
    
    request.session["wishlist"] = wishlist

    # 변경된 버튼 상태 반환
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


@require_POST
def dismiss_alert(request: HttpRequest, alert_id: int) -> HttpResponse:
    """Dismiss price alert (Phase 2)"""
    return HttpResponse(status=200)
