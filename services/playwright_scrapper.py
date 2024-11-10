import hashlib
import os
from datetime import datetime
import aiohttp

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from typing import List, Optional
import asyncio
from models.product import Product
from models.scraping_settings import ScrapingSettings
import logging
import re


class PlaywrightScraper:
    def __init__(self, settings: ScrapingSettings):
        self.settings = settings
        self.browser = None
        self.context = None
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    async def setup(self):
        playwright = await async_playwright().start()
        browser_args = {
            "headless": False,
        }
        if self.settings.proxy:
            browser_args["proxy"] = {
                "server": self.settings.proxy
            }
        self.browser = await playwright.chromium.launch(**browser_args)
        self.context = await self.browser.new_context()

    async def cleanup(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def download_and_save_image(self, image_url: str, product_name: str) -> str:
        try:
            # Create images directory if it doesn't exist
            images_dir = "images"
            os.makedirs(images_dir, exist_ok=True)

            # Create safe filename
            safe_filename = "".join(x for x in product_name if x.isalnum() or x in (' ', '-', '_')).rstrip()
            image_path = os.path.join(images_dir, f"{safe_filename}.jpg")

            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, ssl=False) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(image_path, 'wb') as f:
                            f.write(content)
                        return image_path

        except Exception as e:
            logging.error(f"Error downloading image: {str(e)}")
            return None

    async def get_image_url(self, img_element):
        # Try data-lazy-src first (for lazy loaded images)
        image_url = await img_element.get_attribute('data-lazy-src')

        # If no lazy-src, try data-src
        if not image_url:
            image_url = await img_element.get_attribute('data-src')

        # If still no URL, fall back to regular src
        if not image_url:
            image_url = await img_element.get_attribute('src')

        # Check if it's an SVG placeholder
        if image_url and image_url.startswith('data:image/svg+xml'):
            # Try other attributes or return None
            return None

        return image_url

    async def _extract_product_info(self, product_element) -> Optional[Product]:
        try:
            # Get image element
            img_element = product_element.locator('img.attachment-woocommerce_thumbnail')

            # Get image URL and alt text
            image_url = await self.get_image_url(img_element)
            product_name = await img_element.get_attribute('alt')

            # Download image
            image_path = await self.download_and_save_image(image_url, product_name)

            # Remove " - Dentalstall India" from product name if present
            if product_name:
                product_name = product_name.replace(' - Dentalstall India', '')

            price_elements = product_element.locator('span.amount').all()
            prices = [await price.inner_text() for price in await price_elements]

            # First price will typically be the current/discounted price
            price, discounted_price = float(0), float(0)
            if prices:
                price = float(prices[0].replace('₹', '').strip())

            if len(prices) > 1:
                discounted_price = float(prices[1].replace('₹', '').strip())


            return Product(
                title=product_name,
                image_url=image_url,
                image_path=image_path,
                product_id=generate_product_id(product_name),
                original_price=max(price, discounted_price),
                discounted_price=min(price, discounted_price),
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        except Exception as e:
            logging.error(f"Error extracting product info: {str(e)}")
            return None

    async def _scrape_page(self, page_number: int) -> List[Product]:
        page = await self.context.new_page()
        products = []

        try:
            url = f"https://dentalstall.com/shop/page/{page_number}/"
            await page.goto(url, wait_until="networkidle")

            # Wait for product grid to load
            await page.wait_for_selector('.product', timeout=10000)

            # Get all product elements
            product_elements = await page.locator('.product').all()

            # Extract information from each product
            for product_element in product_elements:
                product = await self._extract_product_info(product_element)
                if product:
                    products.append(product)

        except PlaywrightTimeout:
            logging.error(f"Timeout while scraping page {page_number}")
        except Exception as e:
            logging.error(f"Error scraping page {page_number}: {str(e)}")
        finally:
            await page.close()

        return products

    async def _get_total_pages(self) -> int:
        page = await self.context.new_page()
        try:
            await page.goto("https://dentalstall.com/shop/", wait_until="networkidle")

            # Find the pagination element and get the last page number
            all_elements = await page.locator('.page-numbers').all()
            second_last = await all_elements[-2].text_content()

            return int(second_last)
        finally:
            await page.close()

    async def scrape_with_retry(self, page_number: int) -> List[Product]:
        for attempt in range(self.max_retries):
            try:
                return await self._scrape_page(page_number)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logging.error(f"Failed to scrape page {page_number} after {self.max_retries} attempts")
                    return []
                await asyncio.sleep(self.retry_delay)

    async def scrape(self) -> List[Product]:
        await self.setup()
        all_products = []

        try:
            total_pages = await self._get_total_pages()
            if self.settings.max_pages:
                total_pages = min(total_pages, self.settings.max_pages)

            # Create tasks for each page
            tasks = [self.scrape_with_retry(page_num) for page_num in range(1, total_pages + 1)]

            # Run tasks concurrently with a semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent pages

            async def scrape_with_semaphore(task):
                async with semaphore:
                    return await task

            results = await asyncio.gather(*[scrape_with_semaphore(task) for task in tasks])

            # Flatten results
            for page_products in results:
                all_products.extend(page_products)

        finally:
            await self.cleanup()

        return all_products


def generate_product_id(title):
    return hashlib.sha256(title.encode('utf-8')).hexdigest()
