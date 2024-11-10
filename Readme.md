# E-commerce Product Scraper

A robust, asynchronous web scraper built with FastAPI and Playwright to extract product information from e-commerce websites. The scraper features caching, image downloading, and configurable notifications.

## Features

- 🚀 **Asynchronous Scraping**: Fast and efficient data extraction using Playwright
- 💾 **Caching System**: Redis-based caching to avoid redundant scraping
- 📦 **Product Information**: Extracts detailed product data including:
  - Product title
  - Prices (original and discounted)
  - Product images
- 🖼️ **Image Management**: Automatic download and storage of product images
- 🔒 **API Security**: Token-based authentication for API endpoints
- 📝 **Logging**: Comprehensive error logging and handling
- 🔄 **Extensible Architecture**: Easy to add new features and modify existing ones

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [project-directory]
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
playwright install
playwright install-deps
```

4. Set up Redis (for caching):
```bash
# Install Redis server on your system
# Start Redis server
```


## Usage

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Make API requests:
```bash
curl -X POST "http://localhost:8000/scrape" \
     -H "X-API-Token: your-secret-token" \
     -H "Content-Type: application/json" \
     -d '{"url": "your-target-url"}'
```

## Project Structure

```
project/
├── main.py
├── requirements.txt
├── README.md
├── images/               # Downloaded product images
├── models/              
│   ├── product.py
│   └── scraping_*.py
├── services/
│   ├── scraper_service.py
│   ├── cache_service.py
│   ├── storage_service.py
│   └── notification_service.py
└── routers/
    └── scraper.py
```

## API Endpoints

### POST /scrape
Initiates the scraping process.

**Request Headers:**
- `X-API-Token`: Authentication token

**Request Body:**
```json
{
    "proxy": "https://example.com/products",
    "page_limit": 5  // optional, default is total page number of the website
}
```

**Response:**
```json
{
  "total_products": 144,
  "new_products": 68,
  "updated_products": 76,
  "failed_pages": []
}
```

## Error Handling

The scraper includes comprehensive error handling for:
- Network issues
- Invalid HTML structures
- Missing product information
- Image download failures
- Cache operations
- Authentication errors

## Dependencies

- FastAPI
- Playwright
- Redis
- aiohttp
- pydantic
