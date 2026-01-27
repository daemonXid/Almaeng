"""
🔔 Wishlist Background Tasks

Taskiq를 사용한 비동기 태스크.
✅ DAEMON Pattern: Interface를 통한 도메인 간 통신
"""

import logging

logger = logging.getLogger(__name__)


async def check_all_wishlist_prices() -> dict[str, int]:
    """
    모든 사용자의 찜 목록 가격 체크
    
    ✅ DAEMON Pattern:
    - wishlist.interface.check_price_drops() 사용
    - 도메인 간 직접 의존성 없음
    
    Returns:
        dict: {"users_checked": int, "alerts_created": int}
    """
    from .interface import check_price_drops
    from .models import WishlistItem
    
    # 찜 목록이 있는 모든 사용자
    user_ids = WishlistItem.objects.values_list('user_id', flat=True).distinct()
    
    total_alerts = 0
    success_count = 0
    
    for user_id in user_ids:
        try:
            alerts = check_price_drops(user_id)
            total_alerts += len(alerts)
            success_count += 1
            
            if alerts:
                logger.info(f"Created {len(alerts)} price alerts for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to check prices for user {user_id}: {e}")
            continue
    
    result = {
        "users_checked": success_count,
        "alerts_created": total_alerts,
    }
    
    logger.info(f"Price check completed: {result}")
    return result
