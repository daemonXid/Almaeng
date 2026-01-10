"""
💰 Prices Services

비즈니스 로직: 가격 비교, 추이 분석, 알림 체크.
"""

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from .models import PriceAlert, PriceHistory
from .schemas import PriceCompareSchema, PriceHistorySchema, PriceTrendSchema


def get_current_prices(supplement_id: int) -> list[PriceHistorySchema]:
    """각 플랫폼의 최신 가격 조회"""
    platforms = PriceHistory.objects.filter(supplement_id=supplement_id).values_list("platform", flat=True).distinct()

    prices = []
    for platform in platforms:
        latest = (
            PriceHistory.objects.filter(supplement_id=supplement_id, platform=platform).order_by("-recorded_at").first()
        )
        if latest:
            prices.append(
                PriceHistorySchema(
                    id=latest.id,
                    supplement_id=latest.supplement_id,
                    platform=latest.platform,
                    price=latest.price,
                    original_price=latest.original_price,
                    discount_percent=latest.discount_percent,
                    url=latest.url,
                    is_in_stock=latest.is_in_stock,
                    recorded_at=latest.recorded_at,
                )
            )

    return sorted(prices, key=lambda x: x.price)


def compare_prices(supplement_id: int) -> PriceCompareSchema | None:
    """플랫폼별 가격 비교"""
    prices = get_current_prices(supplement_id)

    if not prices:
        return None

    total = sum(p.price for p in prices)

    return PriceCompareSchema(
        supplement_id=supplement_id,
        platforms=prices,
        lowest_price=prices[0].price,
        lowest_platform=prices[0].platform,
        average_price=Decimal(total / len(prices)).quantize(Decimal("1")),
    )


def get_price_trend(supplement_id: int, platform: str, days: int = 30) -> PriceTrendSchema:
    """가격 추이 조회 (차트용)"""
    since = timezone.now() - timedelta(days=days)

    history = (
        PriceHistory.objects.filter(supplement_id=supplement_id, platform=platform, recorded_at__gte=since)
        .order_by("recorded_at")
        .values("recorded_at", "price")
    )

    dates = [h["recorded_at"].strftime("%m/%d") for h in history]
    prices = [h["price"] for h in history]

    return PriceTrendSchema(dates=dates, prices=prices, platform=platform)


def get_lowest_price(supplement_id: int) -> Decimal | None:
    """현재 최저가 조회"""
    prices = get_current_prices(supplement_id)
    return prices[0].price if prices else None


def check_alerts(supplement_id: int) -> list[PriceAlert]:
    """조건을 만족하는 알림 체크"""
    current_lowest = get_lowest_price(supplement_id)
    if not current_lowest:
        return []

    alerts = PriceAlert.objects.filter(
        supplement_id=supplement_id,
        is_active=True,
        target_price__gte=current_lowest,
        triggered_at__isnull=True,
    )

    return list(alerts)


def calculate_price_per_serving(price: Decimal, servings_count: int) -> Decimal:
    """1회분당 가격 계산"""
    if servings_count <= 0:
        return Decimal(0)
    return (price / servings_count).quantize(Decimal("0.01"))
