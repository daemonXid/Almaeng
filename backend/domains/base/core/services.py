"""
🔧 Services - Write Operations (Command Layer)

Services are responsible for:
- Creating, Updating, Deleting data
- Business logic and validation
- Transaction management
- Side effects (emails, notifications, etc.)

Usage:
    from domains.daemon.services import create_user

    user = create_user(email="user@example.com", password="secret")

Note:
    - Use @transaction.atomic for data consistency
    - Keep business logic here, not in views
    - Call selectors for reading, not direct ORM queries
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction

User = get_user_model()


@transaction.atomic
def create_user(
    *,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    is_active: bool = True,
) -> User:
    """
    Create a new user.

    Args:
        email: User email (unique)
        password: Plain text password (will be hashed)
        first_name: First name
        last_name: Last name
        is_active: Whether user is active

    Returns:
        Created User instance

    Raises:
        ValueError: If email already exists
    """
    if User.objects.filter(email=email).exists():
        raise ValueError(f"User with email {email} already exists")

    user = User.objects.create(
        username=email,  # Using email as username
        email=email,
        password=make_password(password),
        first_name=first_name,
        last_name=last_name,
        is_active=is_active,
    )

    # Side effects can be added here
    # send_welcome_email(user)
    # create_default_settings(user)

    return user


@transaction.atomic
def update_user(
    *,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
) -> User:
    """
    Update user profile.

    Args:
        user_id: User ID to update
        first_name: New first name (optional)
        last_name: New last name (optional)

    Returns:
        Updated User instance
    """
    user = User.objects.get(id=user_id)

    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name

    user.save()
    return user


@transaction.atomic
def deactivate_user(*, user_id: int) -> User:
    """
    Soft delete user by deactivating.

    Args:
        user_id: User ID to deactivate

    Returns:
        Deactivated User instance
    """
    user = User.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return user


@transaction.atomic
def delete_user(*, user_id: int) -> None:
    """
    Hard delete user.

    Args:
        user_id: User ID to delete

    Warning:
        This permanently removes the user. Consider deactivate_user instead.
    """
    User.objects.filter(id=user_id).delete()
