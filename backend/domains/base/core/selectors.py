"""
📖 Selectors - Read Operations (Query Layer)

Selectors are responsible for:
- Reading data from database
- Query optimization (select_related, prefetch_related)
- Filtering and aggregation
- NO side effects (pure reads)

Note:
    - Use selectors for ALL read operations
    - Keep queries optimized (avoid N+1)
    - Return typed results
"""

from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_by_id(*, user_id: int) -> User | None:
    """
    Get user by ID.

    Args:
        user_id: User primary key

    Returns:
        User instance or None
    """
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


def get_user_by_email(*, email: str) -> User | None:
    """
    Get user by email address.

    Args:
        email: User email

    Returns:
        User instance or None
    """
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def get_active_users() -> list[User]:
    """
    Get all active users.

    Returns:
        List of active User instances
    """
    return list(User.objects.filter(is_active=True))


def user_exists(*, email: str) -> bool:
    """
    Check if user exists by email.

    Args:
        email: Email to check

    Returns:
        True if user exists
    """
    return User.objects.filter(email=email).exists()
