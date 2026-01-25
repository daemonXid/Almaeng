from .models import PriceAlert, WishlistItem
from .selectors import get_wishlist_by_user
from .services import toggle_wishlist_item


def toggle_wishlist(
    user_id: int,
    product_id: str,
    platform: str,
    name: str = "",
    price: int = 0,
    image_url: str = "",
    product_url: str = "",
) -> tuple[bool, str]:
    """Expose wishlist toggle logic"""
    return toggle_wishlist_item(
        user_id=user_id,
        product_id=product_id,
        platform=platform,
        name=name,
        price=price,
        image_url=image_url,
        product_url=product_url,
    )


def get_user_wishlist(user_id: int):
    """Expose wishlist listing logic"""
    return get_wishlist_by_user(user_id=user_id)


def check_price_drops(user_id: int) -> list[PriceAlert]:
    """
    Check for price drops in user's wishlist items

    Args:
        user_id: User ID

    Returns:
        list[PriceAlert]: List of new price alerts created
    """
    from domains.integrations.naver.interface import search_naver_products
    from domains.integrations.elevenst.interface import search_elevenst_products
    import asyncio

    wishlist_items = WishlistItem.objects.filter(user_id=user_id)
    alerts: list[PriceAlert] = []

    for item in wishlist_items:
        try:
            # Search for current price
            if item.platform == "naver":
                # Extract product ID from URL or use name
                results = asyncio.run(search_naver_products(item.name, limit=1))
                if results and len(results) > 0:
                    current_price = int(results[0].price)
                else:
                    continue
            elif item.platform == "11st":
                results = asyncio.run(search_elevenst_products(item.name, limit=1))
                if results and len(results) > 0:
                    current_price = int(results[0].price)
                else:
                    continue
            else:
                continue

            # Check if price dropped (more than 5%)
            if current_price < item.price:
                price_drop_percent = ((item.price - current_price) / item.price) * 100

                if price_drop_percent >= 5.0:  # Only alert if drop is >= 5%
                    # Create alert if not exists
                    alert, created = PriceAlert.objects.get_or_create(
                        wishlist_item=item,
                        defaults={
                            "user_id": user_id,
                            "original_price": item.price,
                            "current_price": current_price,
                            "price_drop_percent": price_drop_percent,
                        },
                    )

                    if created:
                        alerts.append(alert)
                        # Update wishlist item price
                        item.price = current_price
                        item.save(update_fields=["price"])

        except Exception:
            # Skip items that fail to check
            continue

    return alerts


def get_user_price_alerts(user_id: int, unread_only: bool = False) -> list[PriceAlert]:
    """
    Get price alerts for user

    Args:
        user_id: User ID
        unread_only: Return only unread alerts

    Returns:
        list[PriceAlert]: List of price alerts
    """
    queryset = PriceAlert.objects.filter(user_id=user_id)
    if unread_only:
        queryset = queryset.filter(is_read=False)
    return list(queryset.order_by("-created_at"))


def mark_alert_as_read(alert_id: int, user_id: int) -> bool:
    """
    Mark price alert as read

    Args:
        alert_id: Alert ID
        user_id: User ID (for security)

    Returns:
        bool: Success status
    """
    try:
        alert = PriceAlert.objects.get(id=alert_id, user_id=user_id)
        alert.is_read = True
        alert.save(update_fields=["is_read"])
        return True
    except PriceAlert.DoesNotExist:
        return False
