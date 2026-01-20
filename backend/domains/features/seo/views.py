"""
🔍 SEO Views

robots.txt, sitemap.xml 생성.
"""

from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from domains.features.supplements.models import MFDSHealthFood


def robots_txt(request: HttpRequest) -> HttpResponse:
    """robots.txt 생성"""
    host = request.get_host()
    protocol = "https" if request.is_secure() else "http"
    base_url = f"{protocol}://{host}"

    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Disallow admin and private areas",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /cart/",
        "Disallow: /payments/",
        "Disallow: /api/",
        "",
        "# Sitemaps",
        f"Sitemap: {base_url}/sitemap.xml",
        "",
        "# Crawl-delay for politeness",
        "Crawl-delay: 1",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request: HttpRequest) -> HttpResponse:
    """sitemap.xml 생성 - 동적 URL 포함"""
    host = request.get_host()
    protocol = "https" if request.is_secure() else "http"
    base_url = f"{protocol}://{host}"
    now = timezone.now().strftime("%Y-%m-%d")

    urls = []

    # Static pages
    static_pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "daily"},
        {"loc": "/supplements/", "priority": "0.9", "changefreq": "daily"},
        {"loc": "/supplements/compare/", "priority": "0.8", "changefreq": "weekly"},
        {"loc": "/prices/search/", "priority": "0.8", "changefreq": "daily"},
        {"loc": "/recommend/", "priority": "0.7", "changefreq": "weekly"},
    ]

    for page in static_pages:
        urls.append(f"""  <url>
    <loc>{base_url}{page['loc']}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>{page['changefreq']}</changefreq>
    <priority>{page['priority']}</priority>
  </url>""")

    # Dynamic supplement pages (limit to 1000 for performance)
    supplements = MFDSHealthFood.objects.values_list("id", flat=True)[:1000]
    for supp_id in supplements:
        urls.append(f"""  <url>
    <loc>{base_url}/supplements/{supp_id}/</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>""")

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    return HttpResponse(xml_content, content_type="application/xml")


def sitemap_index(request: HttpRequest) -> HttpResponse:
    """Sitemap Index (대용량 사이트용)"""
    host = request.get_host()
    protocol = "https" if request.is_secure() else "http"
    base_url = f"{protocol}://{host}"
    now = timezone.now().strftime("%Y-%m-%d")

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>{base_url}/sitemap.xml</loc>
    <lastmod>{now}</lastmod>
  </sitemap>
</sitemapindex>"""

    return HttpResponse(xml_content, content_type="application/xml")
