from abc import ABC, abstractmethod
from typing import List
from models.product import Product
from models.scraping_result import ScrapingResult

class StorageStrategy(ABC):
    @abstractmethod
    async def save_products(self, products: List[Product]):
        pass

    @abstractmethod
    async def load_products(self) -> List[Product]:
        pass

class NotificationStrategy(ABC):
    @abstractmethod
    async def notify(self, result: ScrapingResult):
        pass

class CacheStrategy(ABC):
    @abstractmethod
    async def get_product_prices(self, product_id: str) -> dict:
        pass

    @abstractmethod
    async def set_product_prices(self, product_id: str, original_price: float, discounted_price: float):
        pass

    @abstractmethod
    async def filter_changed_products(self, products: List[Product]) -> List[Product]:
        pass

    @abstractmethod
    async def update_prices(self, products: List[Product]):
        pass

    @abstractmethod
    async def clear_cache(self):
        pass
