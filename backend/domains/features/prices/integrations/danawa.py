"""
🕷️ Danawa Crawler

다나와 가격비교 크롤러.
"""

from decimal import Decimal

from selectolax.parser import HTMLParser

from .base import BaseCrawler, CrawlResult


class DanawaCrawler(BaseCrawler):
    """다나와 크롤러"""

    PLATFORM_NAME = "danawa"
    BASE_URL = "https://search.danawa.com"

    async def search(self, keyword: str) -> list[CrawlResult]:
        """키워드로 제품 검색"""
        search_url = f"{self.BASE_URL}/dsearch.php?query={keyword}&tab=goods"
        html = await self.fetch(search_url)

        if not html:
            return []

        results = []
        parser = HTMLParser(html)

        # 제품 리스트 파싱
        for product in parser.css(".product_list > li.prod_item"):
            try:
                # 제품명
                name_el = product.css_first(".prod_name a")
                name = name_el.text(strip=True) if name_el else ""

                # 가격 (최저가)
                price_el = product.css_first(".price_sect .price")
                price_text = price_el.text(strip=True) if price_el else "0"
                price = self.parse_price(price_text)

                # URL
                link_el = product.css_first(".prod_name a")
                href = link_el.attrs.get("href", "") if link_el else ""
                url = href if href.startswith("http") else f"https://prod.danawa.com{href}"

                results.append(
                    CrawlResult(
                        product_name=name,
                        price=price,
                        url=url,
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
            name_el = parser.css_first(".prod_tit")
            name = name_el.text(strip=True) if name_el else ""

            # 최저가
            price_el = parser.css_first(".lowest_price .lwst_prc")
            price = self.parse_price(price_el.text()) if price_el else Decimal(0)

            return CrawlResult(
                product_name=name,
                price=price,
                url=product_url,
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
