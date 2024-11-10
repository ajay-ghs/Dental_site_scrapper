from pydantic import BaseModel

class ScrapingResult(BaseModel):
    total_products: int
    new_products: int
    updated_products: int
    failed_pages: list[int] = []
