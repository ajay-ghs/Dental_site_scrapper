from typing import List
from models.product import Product
from services.base import StorageStrategy
import json
from pathlib import Path

class JsonFileStorage(StorageStrategy):
    def __init__(self, storage_path: str = "data/products.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    async def save_products(self, products: List[Product]):
        product_data = [product.model_dump() for product in products]
        with self.storage_path.open("w") as f:
            json.dump(product_data, f, indent=2, default=str)

    async def load_products(self) -> List[Product]:
        if self.storage_path.exists():
            with self.storage_path.open("r") as f:
                product_data = json.load(f)
            return [Product(**data) for data in product_data]
        return []
