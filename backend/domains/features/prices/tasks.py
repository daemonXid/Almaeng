"""
⏰ Price Crawling Tasks

Taskiq 기반 배치 작업 - 가격 수집, 알림 체크.
"""

import asyncio
from decimal import Decimal

from django.utils import timezone

from .integrations import get_orchestrator
from .models import PriceHistory
from .services import check_alerts, get_lowest_price, send_price_alert_notification


async def crawl_all_prices():
    """모든 영양제 가격 수집 (배치 작업)"""
    from domains.features.supplements.models import Supplement

    orchestrator = get_orchestrator()
    results = []

    # 모든 영양제 조회
    supplements = Supplement.objects.all()

    for supplement in supplements:
        # 각 영양제의 저장된 플랫폼 URL 가져오기
        # (실제로는 별도 테이블에서 URL 관리 필요)
        latest_prices = PriceHistory.objects.filter(supplement_id=supplement.id).values("platform", "url").distinct()

        urls = {p["platform"]: p["url"] for p in latest_prices if p["url"]}

        if urls:
            try:
                saved = await orchestrator.crawl_and_save(supplement.id, urls)
                results.extend(saved)
            except Exception:
                continue

    await orchestrator.close_all()
    return results


def check_all_price_alerts():
    """모든 가격 알림 체크 및 발송"""
    from domains.features.supplements.models import Supplement

    triggered_alerts = []
    supplements = Supplement.objects.all()

    for supplement in supplements:
        alerts = check_alerts(supplement.id)
        current_price = get_lowest_price(supplement.id)

        for alert in alerts:
            # 알림 발송
            if current_price:
                send_price_alert_notification(alert, current_price)

            # 알림 트리거 처리 (1회성)
            alert.triggered_at = timezone.now()
            alert.is_active = False  # 트리거 후 비활성화
            alert.save()
            triggered_alerts.append(alert)

    return triggered_alerts


def update_price_history(supplement_id: int, platform: str, price: Decimal, url: str = ""):
    """단일 가격 업데이트"""
    return PriceHistory.objects.create(
        supplement_id=supplement_id,
        platform=platform,
        price=price,
        url=url,
        recorded_at=timezone.now(),
    )


# Taskiq 태스크 정의 (broker 설정 필요)
def run_crawl_all_prices():
    """동기 래퍼 - 전체 가격 수집"""
    return asyncio.run(crawl_all_prices())


def run_check_all_alerts():
    """동기 래퍼 - 전체 알림 체크"""
    return check_all_price_alerts()
