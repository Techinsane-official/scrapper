"""
Base scraper class with common functionality.
"""

import re
import asyncio
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from loguru import logger
import aiohttp
from fake_useragent import UserAgent


@dataclass
class ScrapingResult:
    """Scraping result data class."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    url: Optional[str] = None


class PremiumBaseScraper(ABC):
    """Base scraper class with common functionality."""
    
    def __init__(self, retailer: str, base_url: str):
        self.retailer = retailer
        self.base_url = base_url
        self.user_agent = UserAgent()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.max_concurrent_requests = 5
        self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()
    
    async def _create_session(self):
        """Create aiohttp session."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': self.user_agent.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
                connector=aiohttp.TCPConnector(limit=100)
            )
    
    async def _close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(self, url: str, **kwargs) -> Optional[str]:
        """Make HTTP request with rate limiting and error handling."""
        async with self.semaphore:
            try:
                await asyncio.sleep(self.request_delay)
                
                if not self.session:
                    await self._create_session()
                
                async with self.session.get(url, **kwargs) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return None
                        
            except Exception as e:
                logger.error(f"Request failed for {url}: {e}")
                return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract price from text."""
        if not price_text:
            return None
        
        # Remove currency symbols and commas
        price_text = re.sub(r'[^\d.,]', '', price_text)
        
        # Handle different decimal separators
        if ',' in price_text and '.' in price_text:
            # Assume comma is thousands separator
            price_text = price_text.replace(',', '')
        elif ',' in price_text:
            # Check if comma is decimal separator
            parts = price_text.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                price_text = price_text.replace(',', '.')
            else:
                price_text = price_text.replace(',', '')
        
        try:
            return float(price_text)
        except ValueError:
            return None
    
    def _extract_rating(self, rating_text: str) -> Optional[float]:
        """Extract rating from text."""
        if not rating_text:
            return None
        
        # Look for patterns like "4.5 out of 5" or "4.5 stars"
        rating_match = re.search(r'(\d+\.?\d*)\s*(?:out of \d+|stars?)', rating_text)
        if rating_match:
            try:
                return float(rating_match.group(1))
            except ValueError:
                pass
        
        # Look for simple decimal numbers
        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
        if rating_match:
            try:
                rating = float(rating_match.group(1))
                # Normalize to 5-point scale if needed
                if rating > 5:
                    rating = rating / 2  # Assume 10-point scale
                return rating
            except ValueError:
                pass
        
        return None
    
    def _extract_review_count(self, review_text: str) -> Optional[int]:
        """Extract review count from text."""
        if not review_text:
            return None
        
        # Remove commas and extract numbers
        numbers = re.findall(r'[\d,]+', review_text)
        if numbers:
            try:
                return int(numbers[0].replace(',', ''))
            except ValueError:
                pass
        
        return None
    
    @abstractmethod
    async def _parse_product_page(self, content: str, url: str) -> Dict[str, Any]:
        """Parse product page content. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def _extract_product_urls(self, content: str) -> List[str]:
        """Extract product URLs from search results. Must be implemented by subclasses."""
        pass
    
    async def scrape_product(self, url: str) -> ScrapingResult:
        """Scrape a single product page."""
        try:
            content = await self._make_request(url)
            if not content:
                return ScrapingResult(success=False, error="Failed to fetch page", url=url)
            
            product_data = await self._parse_product_page(content, url)
            return ScrapingResult(success=True, data=product_data, url=url)
            
        except Exception as e:
            logger.error(f"Error scraping product {url}: {e}")
            return ScrapingResult(success=False, error=str(e), url=url)
    
    async def scrape_search_results(self, search_url: str, max_pages: int = 5) -> List[ScrapingResult]:
        """Scrape products from search results across multiple pages."""
        results = []
        
        try:
            for page in range(1, max_pages + 1):
                page_url = self._build_search_url(search_url, page)
                logger.info(f"Scraping page {page}: {page_url}")
                
                content = await self._make_request(page_url)
                if not content:
                    logger.warning(f"Failed to fetch page {page}")
                    continue
                
                product_urls = await self._extract_product_urls(content)
                logger.info(f"Found {len(product_urls)} products on page {page}")
                
                # Scrape each product
                for product_url in product_urls:
                    result = await self.scrape_product(product_url)
                    results.append(result)
                    
                    if not result.success:
                        logger.warning(f"Failed to scrape product: {product_url}")
                
                # Add delay between pages
                if page < max_pages:
                    await asyncio.sleep(self.request_delay * 2)
            
            logger.info(f"Scraping completed: {len(results)} products processed")
            return results
            
        except Exception as e:
            logger.error(f"Error in scrape_search_results: {e}")
            return results
    
    def _build_search_url(self, base_url: str, page: int) -> str:
        """Build search URL for specific page. Default implementation."""
        if page == 1:
            return base_url
        else:
            return f"{base_url}&page={page}"
