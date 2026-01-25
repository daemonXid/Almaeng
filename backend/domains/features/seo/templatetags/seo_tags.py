"""
🔍 SEO Template Tags

JSON-LD 구조화 데이터 생성.
"""

import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def jsonld_website(context):
    """WebSite 스키마 (홈페이지용)"""
    request = context.get("request")
    base_url = request.build_absolute_uri("/") if request else "https://almaeng.daemonx.cc"

    data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "ALMAENG",
        "alternateName": "알맹",
        "url": base_url,
        "description": "AI 기반 영양제 가격 비교 및 추천 서비스",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {"@type": "EntryPoint", "urlTemplate": f"{base_url}supplements/?q={{search_term_string}}"},
            "query-input": "required name=search_term_string",
        },
    }

    return mark_safe(f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>')


@register.simple_tag(takes_context=True)
def jsonld_organization(context):
    """Organization 스키마"""
    request = context.get("request")
    base_url = request.build_absolute_uri("/") if request else "https://almaeng.daemonx.cc"

    data = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "ALMAENG",
        "url": base_url,
        "logo": f"{base_url}static/img/logo.png",
        "sameAs": ["https://github.com/daemonxid"],
    }

    return mark_safe(f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>')


@register.simple_tag(takes_context=True)
def jsonld_product(context, product):
    """Product 스키마 (영양제 상세 페이지용)"""
    request = context.get("request")
    base_url = request.build_absolute_uri("/") if request else "https://almaeng.daemonx.cc"

    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": getattr(product, "product_name", getattr(product, "name", "Unknown")),
        "description": getattr(product, "functionality", "")[:200] if hasattr(product, "functionality") else "",
        "brand": {"@type": "Brand", "name": getattr(product, "company_name", getattr(product, "brand", "Unknown"))},
        "category": "Health Supplements",
        "url": f"{base_url}supplements/{product.id}/",
    }

    # 가격 정보가 있으면 추가
    price = context.get("lowest_price")
    if price:
        data["offers"] = {
            "@type": "Offer",
            "price": str(price),
            "priceCurrency": "KRW",
            "availability": "https://schema.org/InStock",
        }

    return mark_safe(f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>')


@register.simple_tag(takes_context=True)
def jsonld_breadcrumb(context, items):
    """BreadcrumbList 스키마

    Usage: {% jsonld_breadcrumb breadcrumbs %}
    breadcrumbs = [{"name": "홈", "url": "/"}, {"name": "영양제", "url": "/supplements/"}]
    """
    request = context.get("request")
    base_url = request.build_absolute_uri("/") if request else "https://almaeng.daemonx.cc"

    item_list = []
    for i, item in enumerate(items, 1):
        item_list.append(
            {
                "@type": "ListItem",
                "position": i,
                "name": item.get("name", ""),
                "item": f"{base_url.rstrip('/')}{item.get('url', '/')}",
            }
        )

    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": item_list}

    return mark_safe(f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>')


@register.simple_tag(takes_context=True)
def jsonld_faq(context, faqs):
    """FAQPage 스키마

    Usage: {% jsonld_faq faq_list %}
    faq_list = [{"question": "Q1", "answer": "A1"}, ...]
    """
    qa_list = []
    for faq in faqs:
        qa_list.append(
            {
                "@type": "Question",
                "name": faq.get("question", ""),
                "acceptedAnswer": {"@type": "Answer", "text": faq.get("answer", "")},
            }
        )

    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": qa_list}

    return mark_safe(f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>')
