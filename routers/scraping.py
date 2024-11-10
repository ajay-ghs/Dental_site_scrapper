from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from models.scraping_result import ScrapingResult
from models.scraping_settings import ScrapingSettings
from services.cache_service import CacheService
from services.notification_service import ConsoleNotification
from services.scraper_service import ScraperService
from services.storage_service import JsonFileStorage

# Create API key header schema
api_key_header = APIKeyHeader(name="X-API-Token")

# Your static token
API_TOKEN = "your-secret-token-here"  # Store this securely in environment variables

# Authentication dependency
async def verify_token(api_key: str = Security(api_key_header)) -> bool:
    if api_key != API_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Invalid API token"
        )
    return True

router = APIRouter()

@router.post("/", response_model=ScrapingResult, dependencies=[Depends(verify_token)])
async def start_scraping(
        settings: ScrapingSettings,
        scraper_service: ScraperService = Depends(
            lambda: ScraperService(
                cache_strategy=CacheService(),
                storage_strategy=JsonFileStorage(),
                notification_strategy=ConsoleNotification()
            )
        )
):
    # Fetch the latest products from the website
    products = await scraper_service.scrape(settings)

    # Process the scraped products
    result = await scraper_service.process_scraped_products(products)

    return result