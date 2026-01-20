"""
🔍 SEO URL Configuration

robots.txt, sitemap.xml 엔드포인트.
"""

from django.urls import path

from .views import robots_txt, sitemap_xml, sitemap_index

app_name = "seo"

urlpatterns = [
    path("robots.txt", robots_txt, name="robots"),
    path("sitemap.xml", sitemap_xml, name="sitemap"),
    path("sitemap-index.xml", sitemap_index, name="sitemap_index"),
]
