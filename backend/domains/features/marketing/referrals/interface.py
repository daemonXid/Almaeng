"""
🎁 Referrals Module Interface - Public API

Usage:
    from domains.features.marketing.referrals.interface import generate_referral_code

    code = generate_referral_code(user_id=1)
    is_valid = validate_referral_code(code)
"""

from __future__ import annotations

import hashlib
import logging
import os

from django.conf import settings

logger = logging.getLogger(__name__)


def generate_referral_code(user_id: int | str) -> str:
    """
    Generate a unique referral code for a user.

    Args:
        user_id: User identifier

    Returns:
        Referral code string
    """
    salt = getattr(settings, "MARKETING_REFERRAL_SALT", os.getenv("MARKETING_REFERRAL_SALT", "daemon"))
    data = f"{user_id}:{salt}".encode()
    return hashlib.sha256(data).hexdigest()[:8].upper()


def validate_referral_code(code: str) -> bool:
    """
    Validate a referral code format.

    Args:
        code: Referral code to validate

    Returns:
        True if valid format
    """
    if not code:
        return False
    return len(code) == 8 and code.isalnum()


def apply_referral(
    new_user_id: int,
    referral_code: str,
) -> bool:
    """
    Apply a referral code to a new user registration.

    Args:
        new_user_id: New user's ID
        referral_code: Referral code used

    Returns:
        True if applied successfully
    """
    if not validate_referral_code(referral_code):
        logger.warning(f"Invalid referral code: {referral_code}")
        return False

    logger.info(f"Referral applied: user {new_user_id}, code {referral_code}")
    # TODO: Link referrer and referred user, apply rewards
    return True


__all__ = ["apply_referral", "generate_referral_code", "validate_referral_code"]
