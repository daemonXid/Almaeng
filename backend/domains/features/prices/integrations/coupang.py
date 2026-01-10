"""
🕷️ Coupang Crawler

쿠팡 크롤러 (Playwright 기반 - JS 렌더링 필요).
"""

from decimal import Decimal

from playwright.async_api import async_playwright

from .base import BaseCrawler, CrawlResult


class CoupangCrawler(BaseCrawler):
    """쿠팡 크롤러 (Playwright 기반)"""

    PLATFORM_NAME = "coupang"
    BASE_URL = "https://www.coupang.com"

    async def search(self, keyword: str) -> list[CrawlResult]:
        """키워드로 제품 검색"""
        results = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.USER_AGENTS[0],
                locale="ko-KR",
            )
            page = await context.new_page()

            try:
                search_url = f"{self.BASE_URL}/np/search?component=&q={keyword}"
                await page.goto(search_url, wait_until="networkidle", timeout=30000)

                # 제품 카드들
                products = await page.query_selector_all("li.search-product")

                for product in products[:20]:  # 상위 20개만
                    try:
                        # 제품명
                        name_el = await product.query_selector(".name")
                        name = await name_el.inner_text() if name_el else ""

                        # 가격
                        price_el = await product.query_selector(".price-value")
                        price_text = await price_el.inner_text() if price_el else "0"
                        price = self.parse_price(price_text)

                        # 원가
                        orig_el = await product.query_selector(".base-price")
                        original_price = None
                        if orig_el:
                            orig_text = await orig_el.inner_text()
                            original_price = self.parse_price(orig_text)

                        # URL
                        link_el = await product.query_selector("a.search-product-link")
                        href = await link_el.get_attribute("href") if link_el else ""
                        url = f"{self.BASE_URL}{href}" if href else ""

                        discount = self.calculate_discount(original_price, price) if original_price else None

                        results.append(
                            CrawlResult(
                                product_name=name.strip(),
                                price=price,
                                original_price=original_price,
                                discount_percent=discount,
                                url=url,
                                platform=self.PLATFORM_NAME,
                            )
                        )
                    except Exception:
                        continue

            finally:
                await browser.close()

        await self.delay()
        return results

    async def get_price(self, product_url: str) -> CrawlResult | None:
        """제품 상세 페이지에서 가격 추출"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.USER_AGENTS[0],
                locale="ko-KR",
            )
            page = await context.new_page()

            try:
                await page.goto(product_url, wait_until="networkidle", timeout=30000)

                # 제품명
                name_el = await page.query_selector(".prod-buy-header__title")
                name = await name_el.inner_text() if name_el else ""

                # 현재 가격
                price_el = await page.query_selector(".total-price strong")
                price = Decimal(0)
                if price_el:
                    price_text = await price_el.inner_text()
                    price = self.parse_price(price_text)

                # 원가
                orig_el = await page.query_selector(".origin-price")
                original_price = None
                if orig_el:
                    orig_text = await orig_el.inner_text()
                    original_price = self.parse_price(orig_text)

                # 재고
                sold_out = await page.query_selector(".oos-label")
                is_in_stock = sold_out is None

                discount = self.calculate_discount(original_price, price) if original_price else None

                return CrawlResult(
                    product_name=name.strip(),
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
            finally:
                await browser.close()
