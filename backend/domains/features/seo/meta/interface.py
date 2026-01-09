"""
🏷️ Meta Module Interface - Public API

Usage:
    from domains.features.seo.meta.interface import generate_meta_tags

    meta = generate_meta_tags(
        title="My Page",
        description="Page description",
        image="/static/og-image.png",
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field

from django.conf import settings


@dataclass
class MetaTags:
    """SEO meta tags for a page."""

    title: str
    description: str
    canonical: str | None = None
    image: str | None = None
    type: str = "website"
    twitter_card: str = "summary_large_image"
    extra: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        """Convert to dictionary for template context."""
        return {
            "title": self.title,
            "description": self.description,
            "canonical": self.canonical,
            "og_title": self.title,
            "og_description": self.description,
            "og_image": self.image,
            "og_type": self.type,
            "twitter_card": self.twitter_card,
            **self.extra,
        }


def generate_meta_tags(
    title: str,
    description: str,
    path: str | None = None,
    image: str | None = None,
    type: str = "website",
) -> MetaTags:
    """
    Generate SEO meta tags for a page.

    Args:
        title: Page title
        description: Page description (max 160 chars recommended)
        path: Page path for canonical URL
        image: Open Graph image URL
        type: Page type (website, article, product)

    Returns:
        MetaTags object
    """
    base_url = getattr(settings, "SEO_BASE_URL", "")
    canonical = f"{base_url}{path}" if path and base_url else None

    # Truncate description if too long
    if len(description) > 160:
        description = description[:157] + "..."

    return MetaTags(
        title=title,
        description=description,
        canonical=canonical,
        image=image,
        type=type,
    )


def generate_structured_data(
    type: str,
    name: str,
    description: str | None = None,
    **kwargs,
) -> dict:
    """
    Generate JSON-LD structured data.

    Args:
        type: Schema.org type (Organization, Article, Product)
        name: Entity name
        description: Entity description
        **kwargs: Additional schema properties

    Returns:
        JSON-LD dictionary
    """
    data = {
        "@context": "https://schema.org",
        "@type": type,
        "name": name,
    }
    if description:
        data["description"] = description
    data.update(kwargs)
    return data


__all__ = ["MetaTags", "generate_meta_tags", "generate_structured_data"]
