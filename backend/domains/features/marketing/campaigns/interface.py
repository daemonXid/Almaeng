"""
📣 Campaigns Module Interface - Public API

Usage:
    from domains.features.marketing.campaigns.interface import create_campaign, track_click

    campaign = create_campaign(name="Summer Sale", source="email")
    track_click(campaign_id=campaign.id, user_id=1)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Campaign:
    """Marketing campaign data."""

    id: str
    name: str
    source: str
    medium: str | None = None
    content: str | None = None
    created_at: datetime | None = None
    clicks: int = 0
    conversions: int = 0


def create_campaign(
    name: str,
    source: str,
    medium: str | None = None,
    content: str | None = None,
) -> Campaign:
    """
    Create a new marketing campaign.

    Args:
        name: Campaign name
        source: Traffic source (email, social, ads)
        medium: Marketing medium (cpc, banner, email)
        content: Content identifier for A/B testing

    Returns:
        Campaign object
    """
    import uuid

    campaign = Campaign(
        id=str(uuid.uuid4())[:8],
        name=name,
        source=source,
        medium=medium,
        content=content,
        created_at=datetime.now(),
    )
    logger.info(f"Campaign created: {campaign.name} ({campaign.id})")
    return campaign


def generate_utm_url(
    base_url: str,
    campaign: Campaign,
) -> str:
    """
    Generate a URL with UTM parameters.

    Args:
        base_url: Base URL to append UTM params
        campaign: Campaign object

    Returns:
        URL with UTM parameters
    """
    params = [
        f"utm_source={campaign.source}",
        f"utm_campaign={campaign.name.replace(' ', '_').lower()}",
    ]
    if campaign.medium:
        params.append(f"utm_medium={campaign.medium}")
    if campaign.content:
        params.append(f"utm_content={campaign.content}")

    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{'&'.join(params)}"


def track_click(campaign_id: str, user_id: int | None = None) -> bool:
    """
    Track a campaign click.

    Args:
        campaign_id: Campaign ID
        user_id: Optional user ID

    Returns:
        True if tracked successfully
    """
    logger.info(f"Campaign click: {campaign_id}, user: {user_id}")
    return True


__all__ = ["Campaign", "create_campaign", "generate_utm_url", "track_click"]
