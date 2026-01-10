"""
📈 Price History Page Views

가격 히스토리 페이지와 차트 파셜.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ...services import compare_prices, get_price_trend


def history(request: HttpRequest, supplement_id: int) -> HttpResponse:
    """가격 히스토리 페이지"""
    price_compare = compare_prices(supplement_id)

    return render(
        request,
        "prices/pages/history/history.html",
        {
            "page_title": "가격 비교 | ALMAENG",
            "supplement_id": supplement_id,
            "price_compare": price_compare,
        },
    )


def price_chart(request: HttpRequest, supplement_id: int) -> HttpResponse:
    """HTMX: 가격 추이 차트 데이터"""
    platform = request.GET.get("platform", "iherb")
    days = int(request.GET.get("days", 30))

    trend = get_price_trend(supplement_id, platform, days)

    return render(
        request,
        "prices/pages/history/_chart.html",
        {"trend": trend},
    )
