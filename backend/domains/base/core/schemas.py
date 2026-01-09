"""
📋 Pydantic Schemas - API Data Validation

This module demonstrates the Pydantic schema patterns for DAEMON-ONE.
Use these patterns for API input/output validation.

Key Principles:
1. Strict validation - reject invalid data early
2. Separate Input vs Output schemas
3. Use ConfigDict(from_attributes=True) for ORM objects

Usage:
    from domains.daemon.schemas import (
        UserCreateSchema,
        UserResponseSchema,
    )

    # Validate input
    data = UserCreateSchema(email="test@example.com", password="secret")

    # Convert ORM to response
    response = UserResponseSchema.model_validate(user_instance)
"""

from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

# =============================================================================
# 🔒 Base Schemas (Inherit from these)
# =============================================================================


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        # Allow population from ORM objects
        from_attributes=True,
        # Strip whitespace from strings
        str_strip_whitespace=True,
        # Validate on assignment
        validate_assignment=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamped models."""

    created_at: datetime
    updated_at: datetime


# =============================================================================
# 📥 Input Schemas (API Request)
# =============================================================================


class UserCreateSchema(BaseSchema):
    """
    Schema for creating a new user.

    Example:
        data = UserCreateSchema(
            email="user@example.com",
            password="securepassword123",
            first_name="John",
        )
    """

    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]
    first_name: str | None = None
    last_name: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Ensure password meets security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if v.isdigit():
            raise ValueError("Password cannot be all digits")
        if v.isalpha():
            raise ValueError("Password must contain at least one number")
        return v


class UserUpdateSchema(BaseSchema):
    """Schema for updating user profile."""

    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        """Ensure at least one field is provided."""
        if not any([self.first_name, self.last_name, self.email]):
            raise ValueError("At least one field must be provided")
        return self


# =============================================================================
# 📤 Output Schemas (API Response)
# =============================================================================


class UserResponseSchema(BaseSchema, TimestampMixin):
    """
    Schema for user API response.

    Example:
        user = User.objects.get(id=1)
        response = UserResponseSchema.model_validate(user)
    """

    id: int
    email: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True

    @property
    def full_name(self) -> str:
        """Computed property for full name."""
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or "Anonymous"


class UserListSchema(BaseSchema):
    """Schema for paginated user list."""

    items: list[UserResponseSchema]
    total: int
    page: int = 1
    page_size: int = 20

    @property
    def has_next(self) -> bool:
        return self.page * self.page_size < self.total

    @property
    def has_prev(self) -> bool:
        return self.page > 1


# =============================================================================
# 🧠 AI Schemas (Gen AI Integration)
# =============================================================================


class AIAnalysisRequest(BaseSchema):
    """
    Schema for AI analysis input.

    Use with GenAIClient.complete_structured()
    """

    content: str = Field(..., min_length=1, max_length=10000)
    analysis_type: str = Field(default="general")
    language: str = Field(default="ko")


class AIAnalysisResponse(BaseSchema):
    """
    Schema for AI analysis output.

    AI generates JSON matching this schema.
    Always validate AI output with strict Pydantic schema.

    Example:
        from domains.daemon.cortex import GenAIClient

        client = GenAIClient()
        result = client.complete_structured(
            "Analyze this text...",
            schema=AIAnalysisResponse,
        )
        if result.is_valid:
            print(result.data.summary)
    """

    summary: str = Field(..., max_length=500)
    score: float = Field(..., ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Limit number of tags."""
        return v[:10]  # Max 10 tags


# =============================================================================
# 📋 Common Patterns
# =============================================================================


class PaginationSchema(BaseSchema):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SuccessResponse(BaseSchema):
    """Generic success response."""

    success: bool = True
    message: str = "Operation completed successfully"


class ErrorResponse(BaseSchema):
    """Generic error response."""

    success: bool = False
    error: str
    detail: str | None = None


# =============================================================================
# 📦 Module Exports
# =============================================================================

__all__ = [
    # AI
    "AIAnalysisRequest",
    "AIAnalysisResponse",
    # Base
    "BaseSchema",
    "ErrorResponse",
    # Common
    "PaginationSchema",
    "SuccessResponse",
    "TimestampMixin",
    # User
    "UserCreateSchema",
    "UserListSchema",
    "UserResponseSchema",
    "UserUpdateSchema",
]
