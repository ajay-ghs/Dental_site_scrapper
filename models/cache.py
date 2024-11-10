from pydantic import BaseModel


class CacheKey(BaseModel):
    product_id: str
    original_price: float
    discounted_price: float


class RedisCache(BaseModel):
    key: str
    data: CacheKey
