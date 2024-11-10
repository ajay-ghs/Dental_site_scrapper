# services/scraper_service.py
from typing import List
from models.product import Product
from models.scraping_result import ScrapingResult
from services.base import StorageStrategy, CacheStrategy, NotificationStrategy
from services.playwright_scrapper import PlaywrightScraper
from models.scraping_settings import ScrapingSettings


class ScraperService:
    def __init__(
            self,
            cache_strategy: CacheStrategy,
            storage_strategy: StorageStrategy,
            notification_strategy: NotificationStrategy
    ):
        self.cache = cache_strategy
        self.storage = storage_strategy
        self.notification = notification_strategy

    async def scrape(self, settings: ScrapingSettings) -> List[Product]:
        scraper = PlaywrightScraper(settings)
        return await scraper.scrape()

    async def process_scraped_products(self, products: List[Product]) -> ScrapingResult:
        changed_products = await self.cache.filter_changed_products(products)

        if changed_products:
            await self.storage.save_products(changed_products)

        await self.cache.update_prices(products)

        scraping_result = ScrapingResult(
            total_products=len(products),
            new_products=len(changed_products),
            updated_products= len(products) - len(changed_products)
        )

        await self.notification.notify(scraping_result)

        return scraping_result
