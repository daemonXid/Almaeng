"""
👤 User Model
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django_lifecycle import AFTER_CREATE, LifecycleModel, hook


class User(LifecycleModel, AbstractUser):
    """
    Custom User model with profile image support.
    """

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
        help_text="Profile picture",
    )
    bio = models.TextField(blank=True, help_text="Short bio")

    class Meta:
        db_table = "daemon_auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    @hook(AFTER_CREATE)
    def on_create(self):
        """Logic to run after user creation."""
        # Example: Send welcome notification or initialize profile
        pass

    def get_initials(self) -> str:
        """Get user initials for avatar placeholder."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        if self.email:
            return self.email[0].upper()
        return "U"
