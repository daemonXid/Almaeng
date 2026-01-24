"""
🔍 Search Page Views

영양제 검색 페이지와 HTMX 검색 결과 파셜.
벡터 검색과 텍스트 검색을 결합한 하이브리드 검색 지원.
"""

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ...conf import settings as supplements_settings
from ...models import Supplement
from ...services import search_by_vector


def search(request: HttpRequest) -> HttpResponse:
    """영양제 검색 페이지"""
    q = request.GET.get("q", "")
    return render(
        request,
        "supplements/pages/search/search.html",
        {
            "page_title": "영양제 검색 | ALMAENG",
            "initial_query": q,
            "popular_keywords": ["오메가3", "비타민C", "유산균", "마그네슘", "루테인", "밀크씨슬", "콜라겐"],
        },
    )


def search_direct(request: HttpRequest) -> HttpResponse:
    """
    검색 결과가 있으면 첫 번째 결과의 상세 페이지로 바로 이동
    하이브리드 검색: 벡터 검색 → 텍스트 검색 순서로 시도
    """
    query = request.GET.get("q", "").strip()
    
    if not query:
        return redirect("daemon:home")
    
    supplement = None
    
    # 1. 벡터 검색 시도 (임베딩이 있는 경우)
    vector_results = search_by_vector(query, limit=1, threshold=0.6)
    if vector_results:
        supplement = vector_results[0]
    
    # 2. 벡터 검색 실패 시 텍스트 검색
    if not supplement:
        supplement = Supplement.objects.filter(
            Q(name__icontains=query) | 
            Q(brand__icontains=query) |
            Q(benefits__icontains=query)
        ).order_by("-description").first()
    
    # 3. 결과가 없으면 일반 검색으로
    if not supplement:
        supplement = Supplement.objects.filter(
            Q(name__icontains=query) | 
            Q(brand__icontains=query)
        ).order_by("-created_at").first()
    
    # 결과가 있으면 상세 페이지로 리다이렉트
    if supplement:
        return redirect("supplements:detail", product_id=supplement.id)
    
    # 결과가 없으면 홈으로
    return redirect("daemon:home")


def search_results(request: HttpRequest) -> HttpResponse:
    """
    HTMX: 검색 결과 파셜
    하이브리드 검색: 벡터 검색 + 텍스트 검색 결합
    """
    query = request.GET.get("q", "").strip()

    if not query:
        return HttpResponse('<p class="text-gray-500 text-center py-8">검색어를 입력하세요</p>')

    supplements = []
    seen_ids = set()
    
    # 1. 벡터 검색 (의미 기반 검색)
    vector_results = search_by_vector(query, limit=supplements_settings.DEFAULT_SEARCH_LIMIT, threshold=0.6)
    for supplement in vector_results:
        if supplement.id not in seen_ids:
            supplements.append(supplement)
            seen_ids.add(supplement.id)
    
    # 2. 텍스트 검색 (키워드 매칭)
    text_results = Supplement.objects.filter(
        Q(name__icontains=query) | 
        Q(brand__icontains=query) |
        Q(benefits__icontains=query)
    ).exclude(id__in=seen_ids).order_by("-description")[:supplements_settings.DEFAULT_SEARCH_LIMIT]
    
    for supplement in text_results:
        if supplement.id not in seen_ids:
            supplements.append(supplement)
            seen_ids.add(supplement.id)
    
    # 3. 결과가 없으면 일반 텍스트 검색
    if not supplements:
        supplements = list(Supplement.objects.filter(
            Q(name__icontains=query) | 
            Q(brand__icontains=query)
        ).order_by("-created_at")[:supplements_settings.DEFAULT_SEARCH_LIMIT])

    return render(
        request,
        "supplements/pages/search/_results.html",
        {"supplements": supplements, "query": query},
    )
