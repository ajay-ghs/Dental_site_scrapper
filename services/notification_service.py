from models.scraping_result import ScrapingResult
from services.base import NotificationStrategy

class ConsoleNotification(NotificationStrategy):
    async def notify(self, result: ScrapingResult):
        print(f"Scraping completed. Total products: {result.total_products}, "
              f"New products: {result.new_products}, "
              f"Updated products: {result.updated_products}")
