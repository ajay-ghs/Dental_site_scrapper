from typing import Optional, List
from models.product import Product
import redis
from services.base import CacheStrategy


class CacheService(CacheStrategy):
    def __init__(self):
        self.redis = redis.from_url("redis://localhost")
        self.key_prefix = "product:"
        self.ttl = 60 * 60 * 24  # 24 hours cache TTL

    async def get_product_prices(self, product_id: str) -> Optional[dict]:
        key = f"{self.key_prefix}{product_id}"
        cached = self.redis.hgetall(key)
        # Convert byte dictionary to string dictionary
        cache_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in cached.items()}
        if cache_data:
            return {
                'original_price': float(cache_data['original_price']),
                'discounted_price': float(cache_data['discounted_price']) if cache_data.get('discounted_price') else None
            }
        return None

    async def set_product_prices(self, product_id: str, original_price: float, discounted_price: Optional[float]):
        key = f"{self.key_prefix}{product_id}"
        values = {
            'original_price': str(original_price),
            'discounted_price': str(discounted_price) if discounted_price else ''
        }
        self.redis.hset(key, mapping=values)
        self.redis.expire(key, self.ttl)

    async def filter_changed_products(self, products: List[Product]) -> List[Product]:
        changed_products = []
        
        for product in products:
            cached_prices = await self.get_product_prices(product.product_id)
            
            if not cached_prices:
                changed_products.append(product)
                continue
                
            if (cached_prices['original_price'] != product.original_price or 
                cached_prices['discounted_price'] != product.discounted_price):
                changed_products.append(product)
                
        return changed_products

    async def update_prices(self, products: List[Product]):
        for product in products:
            await self.set_product_prices(
                product.product_id,
                product.original_price,
                product.discounted_price
            )

    async def clear_cache(self):
        keys = await self.redis.keys(f"{self.key_prefix}*")
        if keys:
            await self.redis.delete(*keys)
