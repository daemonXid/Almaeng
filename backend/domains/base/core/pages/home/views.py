"""
🏠 Core Home Views - PRD v2

AI 쇼핑 도우미 메인 랜딩 페이지.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """
    AI 쇼핑 도우미 - 메인 랜딩 페이지

    PRD v2: 홈페이지는 랜딩 페이지로 표시, 검색은 /search/에서 처리
    """
    return render(
        request,
        "core/pages/home/home.html",
        {
            "page_title": "AI 쇼핑 도우미 | 자연어로 검색하고, 최저가로 구매하세요",
        },
    )


def landing(request: HttpRequest) -> HttpResponse:
    """
    랜딩 페이지 (마케팅용)
    """
    return render(
        request,
        "core/pages/home/home.html",
        {
            "page_title": "AI 쇼핑 도우미 | 자연어로 검색하고, 최저가로 구매하세요",
            "features": [
                {
                    "icon": "🗣️",
                    "title": "자연어 검색",
                    "desc": '"눈 피로에 좋은 영양제 3만원 이하" 처럼 자연스럽게 검색',
                },
                {
                    "icon": "⚖️",
                    "title": "가격 비교",
                    "desc": "네이버쇼핑, 11번가 실시간 가격 비교",
                },
                {
                    "icon": "💳",
                    "title": "원클릭 결제",
                    "desc": "토스페이로 간편하게 결제",
                },
            ],
            "platforms": [
                {"name": "네이버쇼핑", "status": "active"},
                {"name": "11번가", "status": "active"},
            ],
        },
    )
