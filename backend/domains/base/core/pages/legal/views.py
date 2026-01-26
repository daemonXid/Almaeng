"""
📜 Legal Page Views
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def faq(request: HttpRequest) -> HttpResponse:
    """자주 묻는 질문"""
    return render(
        request,
        "core/pages/legal/faq.html",
        {"page_title": "자주 묻는 질문 | ALMAENG"},
    )


def terms(request: HttpRequest) -> HttpResponse:
    """이용약관"""
    return render(
        request,
        "core/pages/legal/terms.html",
        {"page_title": "이용약관 | ALMAENG"},
    )


def privacy(request: HttpRequest) -> HttpResponse:
    """개인정보처리방침"""
    return render(
        request,
        "core/pages/legal/privacy.html",
        {"page_title": "개인정보처리방침 | ALMAENG"},
    )


# 앱인토스 필수 페이지
def support(request: HttpRequest) -> HttpResponse:
    """고객센터"""
    return render(request, "core/pages/support/support.html")


def refund_policy(request: HttpRequest) -> HttpResponse:
    """환불 정책"""
    return render(request, "core/pages/policy/refund.html")


def quality_policy(request: HttpRequest) -> HttpResponse:
    """가품 방지 정책"""
    return render(request, "core/pages/policy/quality.html")
