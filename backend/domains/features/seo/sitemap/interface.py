"""
🗺️ Sitemap Module Interface - Public API

Usage:
    from domains.features.seo.sitemap.interface import generate_sitemap

    sitemap_xml = generate_sitemap(urls=[
        {"loc": "/", "priority": 1.0},
        {"loc": "/about/", "priority": 0.8},
    ])
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from django.conf import settings


@dataclass
class SitemapEntry:
    """A single sitemap entry."""

    loc: str
    lastmod: datetime | None = None
    changefreq: Literal["always", "hourly", "daily", "weekly", "monthly", "yearly", "never"] = "weekly"
    priority: float = 0.5


def generate_sitemap(
    entries: list[SitemapEntry | dict],
    base_url: str | None = None,
) -> str:
    """
    Generate an XML sitemap.

    Args:
        entries: List of sitemap entries
        base_url: Base URL for the site

    Returns:
        XML sitemap string
    """
    base_url = base_url or getattr(settings, "SEO_BASE_URL", "https://example.com")

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for entry in entries:
        if isinstance(entry, dict):
            entry = SitemapEntry(**entry)

        url = f"{base_url}{entry.loc}" if not entry.loc.startswith("http") else entry.loc

        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")

        if entry.lastmod:
            lines.append(f"    <lastmod>{entry.lastmod.strftime('%Y-%m-%d')}</lastmod>")

        lines.append(f"    <changefreq>{entry.changefreq}</changefreq>")
        lines.append(f"    <priority>{entry.priority}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")

    return "\n".join(lines)


def get_static_pages() -> list[SitemapEntry]:
    """
    Get list of static pages for sitemap.

    Returns:
        List of SitemapEntry for static pages
    """
    return [
        SitemapEntry(loc="/", priority=1.0, changefreq="daily"),
        SitemapEntry(loc="/getting-started/", priority=0.9, changefreq="weekly"),
        SitemapEntry(loc="/domains/", priority=0.8, changefreq="weekly"),
        SitemapEntry(loc="/health/", priority=0.5, changefreq="daily"),
    ]


__all__ = ["SitemapEntry", "generate_sitemap", "get_static_pages"]
