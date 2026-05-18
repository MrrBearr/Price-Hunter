import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class ScrapedProduct:
    name: str
    price: float
    original_price: Optional[float] = None
    shipping_cost: float = 0.0
    shipping_time: Optional[str] = None
    url: str = ""
    image_url: Optional[str] = None
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    store_slug: str = ""


class BaseScraper(ABC):
    """Base class for all store scrapers."""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.settings = settings

    async def setup(self):
        """Initialize browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.settings.scraping_headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
            ],
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR",
        )

    async def teardown(self):
        """Close browser."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def new_page(self) -> Page:
        """Create a new page with default settings."""
        page = await self.context.new_page()
        page.set_default_timeout(self.settings.scraping_timeout)
        return page

    async def safe_navigate(self, page: Page, url: str, wait_until: str = "domcontentloaded") -> bool:
        """Safely navigate to a URL with error handling."""
        try:
            await page.goto(url, wait_until=wait_until)
            return True
        except Exception as e:
            logger.error(f"Navigation failed for {url}: {str(e)}")
            return False

    async def scrape_with_retry(self, query: str, max_retries: int = 3) -> List[ScrapedProduct]:
        """Scrape with automatic retry."""
        for attempt in range(max_retries):
            try:
                await self.setup()
                results = await self.scrape(query)
                return results
            except Exception as e:
                logger.error(f"Scrape attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
            finally:
                await self.teardown()
        return []

    @abstractmethod
    async def scrape(self, query: str) -> List[ScrapedProduct]:
        """Scrape products from store. Must be implemented by subclasses."""
        pass

    @property
    @abstractmethod
    def store_slug(self) -> str:
        """Return the store slug identifier."""
        pass

    @property
    @abstractmethod
    def store_name(self) -> str:
        """Return the store display name."""
        pass
