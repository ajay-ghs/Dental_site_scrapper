from pydantic import BaseModel
from datetime import datetime

class Product(BaseModel):
    title: str
    original_price: float
    discounted_price: float = None
    image_url: str
    image_path: str = None
    product_id: str
    last_updated: datetime = None
