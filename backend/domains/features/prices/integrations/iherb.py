"""
🕷️ iHerb Crawler

아이허브 정적 HTML 크롤러.
"""

from decimal import Decimal

from selectolax.parser import HTMLParser

from .base import BaseCrawler, CrawlResult


class IHerbCrawler(BaseCrawler):
    """iHerb 크롤러"""

    PLATFORM_NAME = "iherb"
    BASE_URL = "https://kr.iherb.com"

    async def search(self, keyword: str) -> list[CrawlResult]:
        """키워드로 제품 검색"""
        search_url = f"{self.BASE_URL}/search?kw={keyword}"
        html = await self.fetch(search_url)

        if not html:
            return []

        results = []
        parser = HTMLParser(html)

        # 제품 카드들 파싱
        for product in parser.css(".product-cell-container"):
            try:
                # 제품명
                name_el = product.css_first(".product-title")
                name = name_el.text(strip=True) if name_el else ""

                # 가격
                price_el = product.css_first(".price")
                price_text = price_el.text(strip=True) if price_el else "0"
                price = self.parse_price(price_text)

                # 원가 (할인 전)
                orig_el = product.css_first(".discount-badge .original-price")
                original_price = self.parse_price(orig_el.text()) if orig_el else None

                # URL
                link_el = product.css_first("a.product-link")
                url = f"{self.BASE_URL}{link_el.attrs.get('href', '')}" if link_el else ""

                # 재고 여부
                out_of_stock = product.css_first(".out-of-stock")
                is_in_stock = out_of_stock is None

                discount = self.calculate_discount(original_price, price) if original_price else None

                results.append(
                    CrawlResult(
                        product_name=name,
                        price=price,
                        original_price=original_price,
                        discount_percent=discount,
                        url=url,
                        is_in_stock=is_in_stock,
                        platform=self.PLATFORM_NAME,
                    )
                )
            except Exception:
                continue

        return results

    async def get_price(self, product_url: str) -> CrawlResult | None:
        """제품 상세 페이지에서 가격 추출"""
        html = await self.fetch(product_url)

        if not html:
            return None

        try:
            parser = HTMLParser(html)

            # 제품명
            name_el = parser.css_first("h1#name")
            name = name_el.text(strip=True) if name_el else ""

            # 현재 가격
            price_el = parser.css_first("span.price")
            price = self.parse_price(price_el.text()) if price_el else Decimal(0)

            # 원가
            orig_el = parser.css_first(".old-price")
            original_price = self.parse_price(orig_el.text()) if orig_el else None

            # 재고
            out_of_stock = parser.css_first(".out-of-stock-container")
            is_in_stock = out_of_stock is None

            discount = self.calculate_discount(original_price, price) if original_price else None

            return CrawlResult(
                product_name=name,
                price=price,
                original_price=original_price,
                discount_percent=discount,
                url=product_url,
                is_in_stock=is_in_stock,
                platform=self.PLATFORM_NAME,
            )
        except Exception as e:
            return CrawlResult(
                product_name="",
                price=Decimal(0),
                url=product_url,
                platform=self.PLATFORM_NAME,
                error=str(e),
            )
