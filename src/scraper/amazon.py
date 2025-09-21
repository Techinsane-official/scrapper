"""
Premium Amazon scraper with advanced anti-detection.
"""

import re
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from loguru import logger

from .base import PremiumBaseScraper, ScrapingResult


class PremiumAmazonScraper(PremiumBaseScraper):
    """Premium Amazon scraper with advanced features."""
    
    def __init__(self):
        super().__init__(
            retailer="amazon",
            base_url="https://www.amazon.com"
        )
        
        # Amazon-specific settings
        self.allowed_domains = ["amazon.com", "amazon.co.uk", "amazon.ca", "amazon.de"]
        self.search_endpoints = {
            "electronics": "/s?k=electronics&page={page}",
            "home": "/s?k=home+kitchen&page={page}",
            "fashion": "/s?k=clothing&page={page}",
            "books": "/s?k=books&page={page}",
            "sports": "/s?k=sports+outdoors&page={page}",
        }
    
    async def _parse_product_page(self, content: str, url: str) -> Dict[str, Any]:
        """Parse Amazon product page with advanced extraction."""
        soup = BeautifulSoup(content, 'html.parser')
        
        try:
            # Extract ASIN from URL
            asin = self._extract_asin_from_url(url)
            
            # Basic product information
            product_data = {
                "retailer": "amazon",
                "external_id": asin,
                "url": url,
                "title": self._extract_title(soup),
                "price": self._extract_price(soup),
                "original_price": self._extract_original_price(soup),
                "rating": self._extract_rating(soup),
                "review_count": self._extract_review_count(soup),
                "availability": self._extract_availability(soup),
                "images": self._extract_images(soup),
                "description": self._extract_description(soup),
                "bullet_points": self._extract_bullet_points(soup),
                "specifications": self._extract_specifications(soup),
                "variations": self._extract_variations(soup),
                "brand": self._extract_brand(soup),
                "category": self._extract_category(soup),
                "scraped_at": self._get_current_timestamp(),
            }
            
            # Calculate discount percentage
            if product_data["price"] and product_data["original_price"]:
                discount = ((product_data["original_price"] - product_data["price"]) / product_data["original_price"]) * 100
                product_data["discount_percentage"] = round(discount, 2)
            
            logger.info(f"Successfully parsed Amazon product: {product_data['title'][:50]}...")
            return product_data
            
        except Exception as e:
            logger.error(f"Failed to parse Amazon product page: {e}")
            raise
    
    async def _extract_product_urls(self, content: str) -> List[str]:
        """Extract product URLs from Amazon search results."""
        soup = BeautifulSoup(content, 'html.parser')
        product_urls = []
        
        # Multiple selectors for different Amazon layouts
        selectors = [
            '[data-component-type="s-search-result"] h2 a',
            '.s-result-item h2 a',
            '.s-search-result h2 a',
            'h2 a[href*="/dp/"]',
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and '/dp/' in href:
                    full_url = urljoin(self.base_url, href)
                    product_urls.append(full_url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in product_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(f"Extracted {len(unique_urls)} product URLs from search results")
        return unique_urls
    
    def _build_search_url(self, base_url: str, page: int) -> str:
        """Build Amazon search URL for specific page."""
        if page == 1:
            return base_url
        else:
            return f"{base_url}&page={page}"
    
    def _extract_asin_from_url(self, url: str) -> str:
        """Extract ASIN from Amazon URL."""
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if asin_match:
            return asin_match.group(1)
        
        # Try alternative URL patterns
        asin_match = re.search(r'/product/([A-Z0-9]{10})', url)
        if asin_match:
            return asin_match.group(1)
        
        # Fallback to URL hash
        return str(hash(url))
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title."""
        title_selectors = [
            '#productTitle',
            'h1.a-size-large',
            '.product-title',
            'h1[data-automation-id="product-title"]',
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return self._clean_text(title_elem.get_text())
        
        return ""
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract current price."""
        price_selectors = [
            '.a-price-whole',
            '.a-offscreen',
            '#priceblock_dealprice',
            '#priceblock_ourprice',
            '.a-price-range .a-price-whole',
            '.a-price .a-offscreen',
            '[data-automation-id="product-price"]',
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text()
                price = self._extract_price(price_text)
                if price:
                    return price
        
        return None
    
    def _extract_original_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract original/MSRP price."""
        original_price_selectors = [
            '.a-price-was .a-offscreen',
            '.a-text-strike',
            '.a-price-range .a-price-was .a-offscreen',
            '.was-price .a-offscreen',
        ]
        
        for selector in original_price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text()
                price = self._extract_price(price_text)
                if price:
                    return price
        
        return None
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract customer rating."""
        rating_selectors = [
            '.a-icon-alt',
            '[data-automation-id="star-rating"] .a-icon-alt',
            '.a-icon-star .a-icon-alt',
            '.review-rating .a-icon-alt',
        ]
        
        for selector in rating_selectors:
            rating_elem = soup.select_one(selector)
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating = self._extract_rating(rating_text)
                if rating:
                    return rating
        
        return None
    
    def _extract_review_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract review count."""
        review_selectors = [
            '#acrCustomerReviewText',
            '[data-automation-id="review-count"]',
            '.a-size-base',
            '.review-count',
        ]
        
        for selector in review_selectors:
            review_elem = soup.select_one(selector)
            if review_elem:
                review_text = review_elem.get_text()
                count = self._extract_review_count(review_text)
                if count:
                    return count
        
        return None
    
    def _extract_availability(self, soup: BeautifulSoup) -> str:
        """Extract availability status."""
        availability_selectors = [
            '#availability span',
            '.a-size-medium.a-color-success',
            '.a-size-medium.a-color-price',
            '[data-automation-id="availability"]',
            '.availability',
        ]
        
        for selector in availability_selectors:
            avail_elem = soup.select_one(selector)
            if avail_elem:
                availability = avail_elem.get_text().strip().lower()
                if 'in stock' in availability:
                    return 'in_stock'
                elif 'out of stock' in availability:
                    return 'out_of_stock'
                elif 'pre-order' in availability:
                    return 'pre_order'
                elif 'limited' in availability:
                    return 'limited_stock'
        
        return 'unknown'
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract product images."""
        images = []
        
        # Primary image
        img_selectors = [
            '#landingImage',
            '#imgBlkFront',
            '.a-dynamic-image',
            '.product-image img',
        ]
        
        for selector in img_selectors:
            img_elem = soup.select_one(selector)
            if img_elem:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src and 'data:image' not in src:
                    # Convert to high-resolution URL
                    high_res_src = self._convert_to_high_res_image(src)
                    images.append(high_res_src)
                    break
        
        # Gallery images
        gallery_selectors = [
            '#altImages img',
            '.a-dynamic-image',
            '.imageThumbnail img',
        ]
        
        for selector in gallery_selectors:
            img_elems = soup.select(selector)
            for img_elem in img_elems:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src and 'data:image' not in src:
                    high_res_src = self._convert_to_high_res_image(src)
                    if high_res_src not in images:
                        images.append(high_res_src)
        
        return images[:10]  # Limit to 10 images
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description."""
        desc_selectors = [
            '#feature-bullets .a-list-item',
            '.product-description',
            '[data-automation-id="product-description"]',
            '.a-unordered-list .a-list-item',
        ]
        
        descriptions = []
        for selector in desc_selectors:
            desc_elems = soup.select(selector)
            for elem in desc_elems:
                text = elem.get_text().strip()
                if text and len(text) > 10:  # Filter out short/empty items
                    descriptions.append(text)
        
        return ' '.join(descriptions)
    
    def _extract_bullet_points(self, soup: BeautifulSoup) -> List[str]:
        """Extract bullet points."""
        bullet_selectors = [
            '#feature-bullets .a-list-item',
            '.a-unordered-list .a-list-item',
            '.product-features li',
        ]
        
        bullet_points = []
        for selector in bullet_selectors:
            bullet_elems = soup.select(selector)
            for elem in bullet_elems:
                text = elem.get_text().strip()
                if text and len(text) > 10:
                    bullet_points.append(text)
        
        return bullet_points[:10]  # Limit to 10 bullet points
    
    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract product specifications."""
        specs = {}
        
        # Technical details table
        spec_rows = soup.select('#prodDetails tr')
        for row in spec_rows:
            cells = row.select('td')
            if len(cells) >= 2:
                label = cells[0].get_text().strip()
                value = cells[1].get_text().strip()
                if label and value:
                    specs[label] = value
        
        # Additional specifications
        spec_sections = soup.select('.a-section table tr')
        for row in spec_sections:
            cells = row.select('td')
            if len(cells) >= 2:
                label = cells[0].get_text().strip()
                value = cells[1].get_text().strip()
                if label and value:
                    specs[label] = value
        
        return specs
    
    def _extract_variations(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract product variations."""
        variations = []
        
        # Size variations
        size_selectors = [
            '#variation_size_name .a-button-text',
            '.size-button .a-button-text',
            '[data-automation-id="size-selection"] .a-button-text',
        ]
        
        for selector in size_selectors:
            size_elems = soup.select(selector)
            for elem in size_elems:
                size = elem.get_text().strip()
                if size:
                    variations.append({
                        'type': 'size',
                        'value': size,
                        'available': True
                    })
        
        # Color variations
        color_selectors = [
            '#variation_color_name .a-button-text',
            '.color-button .a-button-text',
            '[data-automation-id="color-selection"] .a-button-text',
        ]
        
        for selector in color_selectors:
            color_elems = soup.select(selector)
            for elem in color_elems:
                color = elem.get_text().strip()
                if color:
                    variations.append({
                        'type': 'color',
                        'value': color,
                        'available': True
                    })
        
        return variations
    
    def _extract_brand(self, soup: BeautifulSoup) -> str:
        """Extract brand information."""
        brand_selectors = [
            '#bylineInfo',
            '.brand',
            '[data-automation-id="brand-name"]',
            '.a-link-normal[href*="/brand/"]',
        ]
        
        for selector in brand_selectors:
            brand_elem = soup.select_one(selector)
            if brand_elem:
                brand_text = brand_elem.get_text().strip()
                if brand_text:
                    return brand_text
        
        return ""
    
    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract product category."""
        category_selectors = [
            '#wayfinding-breadcrumbs_feature_div a',
            '.breadcrumb a',
            '[data-automation-id="breadcrumb"] a',
        ]
        
        for selector in category_selectors:
            category_elems = soup.select(selector)
            if category_elems:
                # Return the last breadcrumb item
                return category_elems[-1].get_text().strip()
        
        return ""
    
    def _convert_to_high_res_image(self, image_url: str) -> str:
        """Convert image URL to high-resolution version."""
        if not image_url:
            return image_url
        
        # Replace low-res dimensions with high-res
        high_res_url = image_url.replace('._AC_SX38_', '._AC_SX1000_')
        high_res_url = high_res_url.replace('._AC_SY38_', '._AC_SY1000_')
        high_res_url = high_res_url.replace('._AC_SX50_', '._AC_SX1000_')
        high_res_url = high_res_url.replace('._AC_SY50_', '._AC_SY1000_')
        
        return high_res_url
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def scrape_category(self, category: str, max_pages: int = 5) -> List[ScrapingResult]:
        """Scrape products from a specific category."""
        if category not in self.search_endpoints:
            logger.warning(f"Unknown category: {category}")
            return []
        
        search_url = self.base_url + self.search_endpoints[category]
        logger.info(f"Scraping Amazon category '{category}' with {max_pages} pages")
        
        return await self.scrape_search_results(search_url, max_pages)
    
    async def scrape_bestsellers(self, category: str = "electronics") -> List[ScrapingResult]:
        """Scrape bestseller products."""
        bestseller_url = f"{self.base_url}/gp/bestsellers/{category}/"
        logger.info(f"Scraping Amazon bestsellers in '{category}'")
        
        return await self.scrape_search_results(bestseller_url, max_pages=3)

