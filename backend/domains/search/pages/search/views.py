from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ...interface import get_search_suggestions, save_search_history, search_products


def search_page(request: HttpRequest) -> HttpResponse:
    """Search page view"""
    query = request.GET.get("q", "").strip()
    sort_by = request.GET.get("sort", "price")  # price, rating, name
    filter_platform = request.GET.get("platform", "")  # naver, 11st
    page = int(request.GET.get("page", 1))
    view_mode = request.GET.get("view", "list")  # list, grid
    per_page = 20

    if not query:
        return render(
            request,
            "pages/search/search.html",
            {
                "page_title": "AI Shopping Assistant | Search",
            },
        )

    # Rate limiting check (simple IP-based)
    ip_address = request.META.get("REMOTE_ADDR", "")
    rate_limit_key = f"search_rate_limit:{ip_address}"
    request_count = cache.get(rate_limit_key, 0)
    if request_count >= 30:  # Max 30 requests per minute
        return render(
            request,
            "pages/search/search.html",
            {
                "page_title": "AI Shopping Assistant | Search",
                "error": "Too many requests. Please wait a moment and try again.",
            },
        )
    cache.set(rate_limit_key, request_count + 1, 60)  # 1 minute window

    # Execute search (async wrapper)
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(search_products(query))
    except Exception:
        import logging

        logger = logging.getLogger(__name__)
        logger.exception(f"Search failed for query: {query}")

        from ...logic.schemas import CompareResult

        return render(
            request,
            "pages/search/results.html",
            {
                "page_title": f'"{query}" Search Results',
                "result": CompareResult(
                    query=query,
                    keywords=[],
                    products=[],
                    recommendation="검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    cheapest=None,
                    best_rated=None,
                ),
                "wishlist_ids": set(),
                "product_wishlist_map": {},
                "total_products": 0,
                "page": 1,
                "has_next": False,
                "has_prev": False,
                "start_idx": 0,
                "end_idx": 0,
                "sort_by": sort_by,
                "filter_platform": filter_platform,
                "error": "검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            },
        )

    # Apply filters
    filtered_products = result.products
    if filter_platform:
        filtered_products = [p for p in filtered_products if p.platform.lower() == filter_platform.lower()]

    # Apply sorting
    if sort_by == "price":
        filtered_products = sorted(filtered_products, key=lambda x: x.price)
    elif sort_by == "rating":
        filtered_products = sorted(filtered_products, key=lambda x: x.rating if x.rating else 0, reverse=True)
    elif sort_by == "name":
        filtered_products = sorted(filtered_products, key=lambda x: x.name.lower())

    # Update result with filtered/sorted products
    result.products = filtered_products
    if filtered_products:
        result.cheapest = min(filtered_products, key=lambda x: x.price)

    # Save search history (authenticated users)
    if request.user.is_authenticated and result.products:
        try:
            save_search_history(
                user_id=request.user.id,
                query=query,
                keywords=result.keywords,
                category=result.products[0].platform if result.products else "",
            )
        except Exception:
            # Don't fail if history save fails
            pass

    # Get wishlist IDs (authenticated users)
    wishlist_ids = set()
    if request.user.is_authenticated:
        try:
            from domains.wishlist.interface import get_user_wishlist

            wishlist_ids = {str(item.product_id) for item in get_user_wishlist(request.user.id)}
        except Exception:
            # Don't fail if wishlist fetch fails
            pass

    # Pre-calculate wishlist status for each product (for template use)
    product_wishlist_map = {}
    if result.products:
        for product in result.products:
            product_wishlist_map[str(product.id)] = str(product.id) in wishlist_ids
    if result.cheapest and str(result.cheapest.id) not in product_wishlist_map:
        product_wishlist_map[str(result.cheapest.id)] = str(result.cheapest.id) in wishlist_ids

    # Pagination (before updating result.products)
    total_products = len(filtered_products)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_products = filtered_products[start_idx:end_idx]
    has_next = end_idx < total_products
    has_prev = page > 1

    # Update result with paginated products
    result.products = paginated_products

    context = {
        "page_title": f'"{query}" Search Results',
        "result": result,
        "wishlist_ids": wishlist_ids,
        "product_wishlist_map": product_wishlist_map,
        "sort_by": sort_by,
        "filter_platform": filter_platform,
        "page": page,
        "has_next": has_next,
        "has_prev": has_prev,
        "total_products": total_products,
        "start_idx": start_idx,
        "end_idx": min(end_idx, total_products),
    }

    # HTMX request: return only product list fragment
    if hasattr(request, "htmx") and request.htmx and page > 1:
        if view_mode == "grid":
            return render(request, "pages/search/_product_item_grid.html", context)
        else:
            return render(request, "pages/search/_product_item_list.html", context)

    return render(request, "pages/search/results.html", context)


def autocomplete(request: HttpRequest) -> HttpResponse:
    """Search autocomplete suggestions (HTMX endpoint)"""
    query = request.GET.get("q", "").strip()
    if not query or len(query) < 2:
        return render(request, "pages/search/_autocomplete.html", {"suggestions": [], "query": ""})

    user_id = request.user.id if request.user.is_authenticated else None
    suggestions = get_search_suggestions(query, user_id=user_id, limit=5)

    return render(request, "pages/search/_autocomplete.html", {"suggestions": suggestions, "query": query})


@login_required
def track_click(request: HttpRequest) -> HttpResponse:
    """Save product to recent views and redirect"""
    product_data = {
        "id": request.GET.get("id"),
        "name": request.GET.get("name"),
        "price": request.GET.get("price"),
        "image": request.GET.get("image"),
        "url": request.GET.get("url"),
    }

    if not product_data["url"]:
        return redirect("daemon:home")

    # Get recent products from session
    recent_products = request.session.get("recent_products", [])

    # Remove duplicates (move to front if exists)
    recent_products = [p for p in recent_products if p.get("id") != product_data["id"]]
    recent_products.insert(0, product_data)

    # Keep maximum 10 items
    request.session["recent_products"] = recent_products[:10]

    return redirect(product_data["url"])
