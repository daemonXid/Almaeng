"""
🚪 Accounts Interface - Type-Safe Domain Boundary
Protocol: All domain communication must happen through Pydantic schemas.
"""

from pydantic import BaseModel

from .models import User

# --- Schemas ---


class UserSchema(BaseModel):
    """Clean representation of a User for other domains."""

    id: int
    email: str
    username: str
    is_active: bool
    profile_image_url: str | None = None

    class Config:
        from_attributes = True


# --- Public API ---


def get_user_by_id(user_id: int) -> UserSchema | None:
    """Retrieve a type-safe user representation."""
    try:
        user = User.objects.get(id=user_id)
        return UserSchema.model_validate(user)
    except User.DoesNotExist:
        return None


def get_user_by_email(email: str) -> UserSchema | None:
    """Search for a user by email."""
    try:
        user = User.objects.get(email=email)
        return UserSchema.model_validate(user)
    except User.DoesNotExist:
        return None


def notify_user(user_id: int, message: str) -> bool:
    """
    Interface for cross-domain notifications.
    Implementation detail is hidden within this domain.
    """
    # TODO: Connect to notifications domain or email service
    print(f"🔔 Notification for User {user_id}: {message}")
    return True


__all__ = [
    "UserSchema",
    "get_user_by_email",
    "get_user_by_id",
    "notify_user",
]
