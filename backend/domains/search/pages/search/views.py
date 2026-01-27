from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ...interface import get_search_suggestions, save_search_history, search_products


async def search_page(request: HttpRequest) -> HttpResponse:
    """Search page view - also serves as home page"""
    query = request.GET.get("q", "").strip()
    sort_by = request.GET.get("sort", "price")  # price, rating, name
    filter_platform = request.GET.get("platform", "")  # naver, 11st
    page = int(request.GET.get("page", 1))
    view_mode = request.GET.get("view", "list")  # list, grid
    per_page = 20

    # No query = show home page with categories
    if not query:
        return render(
            request,
            "pages/search/index.html",
            {
                "page_title": "알맹AI - 영양제 최저가",
            },
        )

    # Rate limiting check (disabled if Redis unavailable)
    try:
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
    except Exception:
        # Redis unavailable, skip rate limiting
        pass

    # Execute search (pure async)
    try:
        result = await search_products(query)
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

    # Find cheapest from filtered products
    cheapest = min(filtered_products, key=lambda x: x.price) if filtered_products else None

    # 로그인 기능 제거 (앱인토스에서는 불필요)
    wishlist_ids = set()
    product_wishlist_map = {}

    # Pagination
    total_products = len(filtered_products)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_products = filtered_products[start_idx:end_idx]
    has_next = end_idx < total_products
    has_prev = page > 1

    # Create new CompareResult with paginated products (frozen model)
    from ...logic.schemas import CompareResult
    
    paginated_result = CompareResult(
        query=result.query,
        keywords=result.keywords,
        products=paginated_products,
        recommendation=result.recommendation,
        cheapest=cheapest,
        best_rated=result.best_rated,
    )
    
    context = {
        "page_title": f'"{query}" Search Results',
        "result": paginated_result,
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

    suggestions = get_search_suggestions(query, user_id=None, limit=5)
    return render(request, "pages/search/_autocomplete.html", {"suggestions": suggestions, "query": query})


def track_click(request: HttpRequest) -> HttpResponse:
    """Redirect to product URL"""
    product_url = request.GET.get("url", "")
    if not product_url:
        return redirect("/")
    return redirect(product_url)


def explain_supplement(request: HttpRequest) -> HttpResponse:
    """
    AI 영양제 설명 (HTMX endpoint)

    키워드를 받아서 Gemini AI로 설명 생성
    """
    keyword = request.GET.get("keyword", "").strip()

    if not keyword:
        return HttpResponse(
            '<div class="text-center py-8 text-gray-500">키워드를 입력해주세요</div>'
        )

    # Gemini AI로 설명 생성
    try:
        from domains.ai.service.chatbot.interface import generate_text

        prompt = f"""영양제 "{keyword}"에 대해 간단히 설명해주세요.

다음 형식으로 작성:
1. 주요 효능 (2-3가지)
2. 권장 섭취 시간
3. 주의사항 (1-2가지)

친근하고 간결하게 (300자 이내)"""

        explanation = generate_text(
            prompt=prompt,
            system_instruction="당신은 영양제 전문가입니다. 정확하고 신뢰할 수 있는 정보를 제공하세요.",
        )

    except Exception as e:
        explanation = f"AI 설명을 불러오는 중 오류가 발생했습니다: {e!s}"

    return HttpResponse(f"""
    <div class="space-y-6">
        <!-- AI 설명 -->
        <div>
            <div class="flex items-center gap-2 mb-3">
                <span class="text-2xl">🤖</span>
                <h4 class="text-base font-bold text-gray-900 dark:text-white">AI 설명</h4>
            </div>
            <div class="prose prose-sm dark:prose-invert max-w-none">
                <p class="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">{explanation}</p>
            </div>
        </div>

        <!-- 추가 정보 -->
        <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4">
            <p class="text-xs text-yellow-800 dark:text-yellow-200">
                ⚠️ 본 정보는 AI가 생성한 참고용입니다.
                섭취 전 전문가와 상담하세요.
            </p>
        </div>

        <!-- 검색 버튼 -->
        <a href="/?q={keyword}"
            class="block w-full py-3 bg-brand-600 hover:bg-brand-700 text-white font-bold text-center rounded-xl transition-all active:scale-95">
            "{keyword}" 상품 검색하기 →
        </a>
    </div>
    """)
