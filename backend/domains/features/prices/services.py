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
    """현재 최저가 조회 (가격만)"""
    prices = get_current_prices(supplement_id)
    return prices[0].price if prices else None


def get_lowest_price_record(supplement_id: int) -> PriceHistory | None:
    """현재 최저가 기록 조회 (PriceHistory 객체)"""
    return PriceHistory.objects.filter(
        supplement_id=supplement_id
    ).order_by("price", "-recorded_at").first()


def get_price_history(supplement_id: int, limit: int = 10) -> list[PriceHistory]:
    """영양제의 가격 이력 조회"""
    return list(
        PriceHistory.objects.filter(supplement_id=supplement_id)
        .order_by("-recorded_at")[:limit]
    )


def get_active_alerts_count() -> int:
    """활성 가격 알림 개수"""
    return PriceAlert.objects.filter(is_active=True).count()


def get_total_price_records_count() -> int:
    """전체 가격 기록 개수"""
    return PriceHistory.objects.count()


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


# ============================================================
# Price Alert Notifications
# ============================================================


def send_price_alert_notification(alert: PriceAlert, current_price: Decimal) -> bool:
    """
    가격 알림 트리거 시 알림 발송.

    Args:
        alert: 트리거된 PriceAlert 인스턴스
        current_price: 현재 최저가

    Returns:
        성공 여부
    """
    from django.contrib.auth import get_user_model

    from domains.base.notifications.interface import notify_user

    User = get_user_model()

    try:
        user = User.objects.get(id=alert.user_id)
    except User.DoesNotExist:
        return False

    # 영양제 이름 조회 (interface.py를 통해)
    product_name = f"영양제 #{alert.supplement_id}"
    try:
        from domains.features.supplements.interface import get_supplement_name

        product_name = get_supplement_name(alert.supplement_id)
    except Exception:
        # 실패 시 기본값 유지
        pass

    # In-app 알림 생성
    notify_user(
        user=user,
        title=f"가격 알림: {product_name}",
        message=f"설정하신 목표가 {alert.target_price:,.0f}원 이하로 가격이 내려갔습니다! 현재가: {current_price:,.0f}원",
        notification_type="success",
        link=f"/supplements/{alert.supplement_id}/",
    )

    # 이메일 알림 (SMTP 설정이 있을 경우에만)
    try:
        from domains.base.notifications.email.interface import send_email

        send_email(
            to=user.email,
            subject=f"[ALMAENG] 가격 알림: {product_name}",
            template="price_alert",
            context={
                "user_name": user.get_full_name() or user.username,
                "product_name": product_name,
                "target_price": f"{alert.target_price:,.0f}",
                "current_price": f"{current_price:,.0f}",
                "product_url": f"/supplements/{alert.supplement_id}/",
            },
        )
    except Exception:
        # 이메일 발송 실패해도 in-app 알림은 성공으로 처리
        pass

    return True
