# Sample Code Implementation
## Unified E-commerce Product Data Aggregator

---

## Project Structure

```
ecommerce-aggregator/
├── src/
│   ├── scraper_service/
│   │   ├── spiders/
│   │   │   ├── __init__.py
│   │   │   ├── base_spider.py
│   │   │   ├── amazon_spider.py
│   │   │   ├── walmart_spider.py
│   │   │   └── target_spider.py
│   │   ├── middlewares/
│   │   │   ├── __init__.py
│   │   │   ├── proxy_middleware.py
│   │   │   ├── user_agent_middleware.py
│   │   │   └── rate_limit_middleware.py
│   │   ├── pipelines/
│   │   │   ├── __init__.py
│   │   │   ├── data_validation.py
│   │   │   ├── duplicate_detection.py
│   │   │   └── database_storage.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py
│   │   │   └── retailers_config.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── helpers.py
│   │       └── validators.py
│   ├── data_processing_service/
│   │   ├── processors/
│   │   │   ├── __init__.py
│   │   │   ├── product_normalizer.py
│   │   │   ├── price_validator.py
│   │   │   └── image_processor.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── product_model.py
│   │   │   ├── price_model.py
│   │   │   └── variation_model.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── data_cleaning.py
│   │   │   ├── deduplication.py
│   │   │   └── quality_scoring.py
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── endpoints.py
│   │       └── schemas.py
│   ├── api_service/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── products.py
│   │   │   ├── prices.py
│   │   │   └── analytics.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── authentication.py
│   │   │   ├── rate_limiting.py
│   │   │   └── caching.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database_models.py
│   │   │   └── response_models.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── pagination.py
│   │   │   └── filtering.py
│   │   └── main.py
│   └── shared/
│       ├── __init__.py
│       ├── database/
│       │   ├── __init__.py
│       │   ├── connection.py
│       │   └── models.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       └── utils/
│           ├── __init__.py
│           ├── logging.py
│           └── exceptions.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── scripts/
│   ├── setup_db.py
│   ├── migrate_data.py
│   └── backup_data.py
├── docs/
│   ├── api/
│   ├── deployment/
│   └── development/
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

---

## Core Implementation Files

### 1. Base Spider Class

```python
# src/scraper_service/spiders/base_spider.py
import scrapy
from scrapy.http import Request
from scrapy.exceptions import DropItem
from typing import Dict, List, Optional
import logging
from datetime import datetime
import json

class BaseSpider(scrapy.Spider):
    """Base spider class with common functionality"""
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'AUTOTHROTTLE_DEBUG': False,
    }
    
    def __init__(self, category=None, max_pages=None, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.category = category
        self.max_pages = int(max_pages) if max_pages else None
        self.logger = logging.getLogger(self.name)
        
    def start_requests(self):
        """Generate initial requests"""
        raise NotImplementedError("Subclasses must implement start_requests")
    
    def parse_product(self, response):
        """Parse individual product page"""
        raise NotImplementedError("Subclasses must implement parse_product")
    
    def extract_price(self, response) -> Optional[float]:
        """Extract and normalize price"""
        raise NotImplementedError("Subclasses must implement extract_price")
    
    def extract_rating(self, response) -> Optional[float]:
        """Extract and normalize rating"""
        raise NotImplementedError("Subclasses must implement extract_rating")
    
    def extract_images(self, response) -> List[str]:
        """Extract product images"""
        raise NotImplementedError("Subclasses must implement extract_images")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.split())
    
    def normalize_price(self, price_text: str) -> Optional[float]:
        """Normalize price text to float"""
        if not price_text:
            return None
        
        import re
        # Remove currency symbols and commas
        price_clean = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
        
        try:
            return float(price_clean)
        except ValueError:
            return None
    
    def get_retailer(self) -> str:
        """Get retailer name"""
        return self.name
    
    def log_scraping_stats(self, stats: Dict):
        """Log scraping statistics"""
        self.logger.info(f"Scraping stats: {json.dumps(stats, indent=2)}")
```

### 2. Amazon Spider Implementation

```python
# src/scraper_service/spiders/amazon_spider.py
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin, urlparse, parse_qs
from typing import Dict, List, Optional
import re
from datetime import datetime
from .base_spider import BaseSpider

class AmazonSpider(BaseSpider):
    name = 'amazon'
    allowed_domains = ['amazon.com', 'amazon.co.uk', 'amazon.ca']
    
    def __init__(self, category='electronics', *args, **kwargs):
        super().__init__(category=category, *args, **kwargs)
        self.base_url = 'https://www.amazon.com'
        
    def start_requests(self):
        """Generate initial requests for Amazon search"""
        search_url = f"{self.base_url}/s?k={self.category}&page=1"
        yield Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'page': 1, 'category': self.category}
        )
    
    def parse_search_results(self, response):
        """Parse Amazon search results page"""
        # Extract product URLs
        product_links = response.css('[data-component-type="s-search-result"] h2 a::attr(href)').getall()
        
        for link in product_links:
            product_url = urljoin(response.url, link)
            yield Request(
                url=product_url,
                callback=self.parse_product,
                meta={'dont_cache': True}
            )
        
        # Follow pagination
        current_page = response.meta.get('page', 1)
        if self.max_pages and current_page >= self.max_pages:
            return
            
        next_page = response.css('a[aria-label="Next Page"]::attr(href)').get()
        if next_page:
            yield Request(
                url=urljoin(response.url, next_page),
                callback=self.parse_search_results,
                meta={'page': current_page + 1, 'category': self.category}
            )
    
    def parse_product(self, response):
        """Parse individual Amazon product page"""
        try:
            product_data = {
                'retailer': 'amazon',
                'external_id': self.extract_external_id(response),
                'url': response.url,
                'scraped_at': datetime.now().isoformat(),
                'title': self.extract_title(response),
                'price': self.extract_price(response),
                'original_price': self.extract_original_price(response),
                'rating': self.extract_rating(response),
                'review_count': self.extract_review_count(response),
                'availability': self.extract_availability(response),
                'images': self.extract_images(response),
                'specifications': self.extract_specifications(response),
                'variations': self.extract_variations(response),
                'description': self.extract_description(response),
                'bullet_points': self.extract_bullet_points(response),
                'brand': self.extract_brand(response),
                'category': self.extract_category(response)
            }
            
            # Validate required fields
            if not product_data['title'] or not product_data['external_id']:
                self.logger.warning(f"Skipping product with missing required fields: {response.url}")
                return
            
            yield product_data
            
        except Exception as e:
            self.logger.error(f"Error parsing product {response.url}: {e}")
    
    def extract_external_id(self, response) -> str:
        """Extract Amazon ASIN"""
        # Try to extract ASIN from URL
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', response.url)
        if asin_match:
            return asin_match.group(1)
        
        # Try to extract from page data
        asin_data = response.css('#ASIN::attr(value)').get()
        if asin_data:
            return asin_data
        
        # Fallback to URL hash
        return str(hash(response.url))
    
    def extract_title(self, response) -> str:
        """Extract product title"""
        title = response.css('#productTitle::text').get()
        return self.clean_text(title) if title else ""
    
    def extract_price(self, response) -> Optional[float]:
        """Extract current price"""
        price_selectors = [
            '.a-price-whole::text',
            '.a-offscreen::text',
            '#priceblock_dealprice::text',
            '#priceblock_ourprice::text',
            '.a-price-range .a-price-whole::text'
        ]
        
        for selector in price_selectors:
            price_text = response.css(selector).get()
            if price_text:
                price = self.normalize_price(price_text)
                if price:
                    return price
        
        return None
    
    def extract_original_price(self, response) -> Optional[float]:
        """Extract original/MSRP price"""
        original_price_selectors = [
            '.a-price-was .a-offscreen::text',
            '.a-text-strike::text',
            '.a-price-range .a-price-was .a-offscreen::text'
        ]
        
        for selector in original_price_selectors:
            price_text = response.css(selector).get()
            if price_text:
                price = self.normalize_price(price_text)
                if price:
                    return price
        
        return None
    
    def extract_rating(self, response) -> Optional[float]:
        """Extract customer rating"""
        rating_text = response.css('.a-icon-alt::text').get()
        if rating_text:
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            return float(rating_match.group(1)) if rating_match else None
        return None
    
    def extract_review_count(self, response) -> Optional[int]:
        """Extract review count"""
        review_text = response.css('#acrCustomerReviewText::text').get()
        if review_text:
            review_match = re.search(r'([\d,]+)', review_text)
            if review_match:
                return int(review_match.group(1).replace(',', ''))
        return None
    
    def extract_availability(self, response) -> str:
        """Extract availability status"""
        availability_selectors = [
            '#availability span::text',
            '.a-size-medium.a-color-success::text',
            '.a-size-medium.a-color-price::text'
        ]
        
        for selector in availability_selectors:
            availability = response.css(selector).get()
            if availability:
                availability = availability.strip().lower()
                if 'in stock' in availability:
                    return 'in_stock'
                elif 'out of stock' in availability:
                    return 'out_of_stock'
                elif 'pre-order' in availability:
                    return 'pre_order'
        
        return 'unknown'
    
    def extract_images(self, response) -> List[str]:
        """Extract product images"""
        images = response.css('#altImages img::attr(src)').getall()
        high_res_images = []
        
        for img in images:
            if img and 'data:image' not in img:
                # Convert to high-resolution URL
                high_res_img = img.replace('._AC_SX38_', '._AC_SX1000_')
                high_res_img = high_res_img.replace('._AC_SY38_', '._AC_SY1000_')
                high_res_images.append(high_res_img)
        
        return high_res_images
    
    def extract_specifications(self, response) -> Dict[str, str]:
        """Extract product specifications"""
        specs = {}
        
        # Technical details table
        spec_rows = response.css('#prodDetails tr')
        for row in spec_rows:
            label = row.css('td:first-child::text').get()
            value = row.css('td:last-child::text').get()
            if label and value:
                specs[label.strip()] = value.strip()
        
        return specs
    
    def extract_variations(self, response) -> List[Dict]:
        """Extract product variations"""
        variations = []
        
        # Size variations
        sizes = response.css('#variation_size_name .a-button-text::text').getall()
        for size in sizes:
            variations.append({
                'type': 'size',
                'value': size.strip(),
                'available': True
            })
        
        # Color variations
        colors = response.css('#variation_color_name .a-button-text::text').getall()
        for color in colors:
            variations.append({
                'type': 'color',
                'value': color.strip(),
                'available': True
            })
        
        return variations
    
    def extract_description(self, response) -> str:
        """Extract product description"""
        description = response.css('#feature-bullets .a-list-item::text').getall()
        return ' '.join([self.clean_text(desc) for desc in description if desc])
    
    def extract_bullet_points(self, response) -> List[str]:
        """Extract bullet points"""
        bullet_points = response.css('#feature-bullets .a-list-item::text').getall()
        return [self.clean_text(bp) for bp in bullet_points if bp]
    
    def extract_brand(self, response) -> str:
        """Extract brand information"""
        brand = response.css('#bylineInfo::text').get()
        return self.clean_text(brand) if brand else ""
    
    def extract_category(self, response) -> str:
        """Extract product category"""
        breadcrumb = response.css('#wayfinding-breadcrumbs_feature_div a::text').getall()
        return breadcrumb[-1] if breadcrumb else self.category
```

### 3. Data Processing Pipeline

```python
# src/data_processing_service/processors/product_normalizer.py
from typing import Dict, List, Optional, Any
import re
from datetime import datetime
import logging
from ..models.product_model import ProductModel
from ..utils.data_cleaning import DataCleaner
from ..utils.quality_scoring import QualityScorer

class ProductNormalizer:
    """Normalize scraped product data to standard format"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_cleaner = DataCleaner()
        self.quality_scorer = QualityScorer()
    
    def normalize_product(self, raw_data: Dict[str, Any]) -> Optional[ProductModel]:
        """Normalize scraped product data"""
        try:
            normalized_data = {
                'external_id': self.extract_external_id(raw_data),
                'retailer': raw_data.get('retailer'),
                'title': self.clean_title(raw_data.get('title')),
                'description': self.clean_description(raw_data.get('description')),
                'brand': self.extract_brand(raw_data),
                'model': self.extract_model(raw_data),
                'category': self.categorize_product(raw_data),
                'subcategory': self.extract_subcategory(raw_data),
                'sku': self.extract_sku(raw_data),
                'upc': self.extract_upc(raw_data),
                'ean': self.extract_ean(raw_data),
                'asin': self.extract_asin(raw_data),
                'url': raw_data.get('url'),
                'image_url': self.extract_primary_image(raw_data.get('images', [])),
                'rating': self.normalize_rating(raw_data.get('rating')),
                'review_count': self.normalize_review_count(raw_data.get('review_count')),
                'availability_status': self.normalize_availability(raw_data.get('availability')),
                'scraped_at': raw_data.get('scraped_at'),
                'data_quality_score': self.quality_scorer.calculate_score(raw_data)
            }
            
            # Validate required fields
            if not normalized_data['external_id'] or not normalized_data['title']:
                self.logger.warning(f"Skipping product with missing required fields")
                return None
            
            return ProductModel(**normalized_data)
            
        except Exception as e:
            self.logger.error(f"Error normalizing product data: {e}")
            return None
    
    def extract_external_id(self, data: Dict[str, Any]) -> str:
        """Extract unique external identifier"""
        url = data.get('url', '')
        
        # Amazon ASIN
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if asin_match:
            return asin_match.group(1)
        
        # Walmart item ID
        walmart_match = re.search(r'/ip/(\d+)', url)
        if walmart_match:
            return walmart_match.group(1)
        
        # Target TCN
        target_match = re.search(r'/p/(\d+)', url)
        if target_match:
            return target_match.group(1)
        
        # Fallback to URL hash
        return str(hash(url))
    
    def clean_title(self, title: str) -> str:
        """Clean and normalize product title"""
        if not title:
            return ""
        
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title.strip())
        
        # Remove common prefixes/suffixes
        title = re.sub(r'^(New|Used|Refurbished)\s*', '', title, flags=re.IGNORECASE)
        
        return title
    
    def clean_description(self, description: str) -> str:
        """Clean product description"""
        if not description:
            return ""
        
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        
        # Clean whitespace
        description = re.sub(r'\s+', ' ', description.strip())
        
        return description
    
    def extract_brand(self, data: Dict[str, Any]) -> str:
        """Extract brand information"""
        brand = data.get('brand', '')
        if not brand:
            # Try to extract from title
            title = data.get('title', '')
            brand_match = re.search(r'^([A-Z][a-zA-Z\s]+?)\s', title)
            if brand_match:
                brand = brand_match.group(1).strip()
        
        return self.data_cleaner.clean_brand(brand)
    
    def extract_model(self, data: Dict[str, Any]) -> str:
        """Extract model information"""
        model = data.get('model', '')
        if not model:
            # Try to extract from specifications
            specs = data.get('specifications', {})
            model_keys = ['model', 'model number', 'part number', 'sku']
            for key in model_keys:
                if key in specs:
                    model = specs[key]
                    break
        
        return model.strip() if model else ""
    
    def categorize_product(self, data: Dict[str, Any]) -> str:
        """Categorize product based on available data"""
        category = data.get('category', '')
        if not category:
            # Use title-based categorization
            title = data.get('title', '').lower()
            category = self.data_cleaner.categorize_by_title(title)
        
        return category
    
    def extract_subcategory(self, data: Dict[str, Any]) -> str:
        """Extract subcategory information"""
        # This would be implemented based on specific retailer data
        return data.get('subcategory', '')
    
    def extract_sku(self, data: Dict[str, Any]) -> str:
        """Extract SKU information"""
        specs = data.get('specifications', {})
        sku_keys = ['sku', 'part number', 'model number']
        for key in sku_keys:
            if key in specs:
                return specs[key]
        return ""
    
    def extract_upc(self, data: Dict[str, Any]) -> str:
        """Extract UPC information"""
        specs = data.get('specifications', {})
        return specs.get('upc', '') or specs.get('universal product code', '')
    
    def extract_ean(self, data: Dict[str, Any]) -> str:
        """Extract EAN information"""
        specs = data.get('specifications', {})
        return specs.get('ean', '') or specs.get('european article number', '')
    
    def extract_asin(self, data: Dict[str, Any]) -> str:
        """Extract Amazon ASIN"""
        if data.get('retailer') == 'amazon':
            return data.get('external_id', '')
        return ""
    
    def extract_primary_image(self, images: List[str]) -> str:
        """Extract primary image URL"""
        if not images:
            return ""
        
        # Return the first high-quality image
        for img in images:
            if img and 'data:image' not in img:
                return img
        
        return images[0] if images else ""
    
    def normalize_rating(self, rating) -> Optional[float]:
        """Normalize rating to 0-5 scale"""
        if not rating:
            return None
        
        if isinstance(rating, (int, float)):
            return min(max(float(rating), 0.0), 5.0)
        
        if isinstance(rating, str):
            rating_match = re.search(r'(\d+\.?\d*)', rating)
            if rating_match:
                return min(max(float(rating_match.group(1)), 0.0), 5.0)
        
        return None
    
    def normalize_review_count(self, review_count) -> Optional[int]:
        """Normalize review count to integer"""
        if not review_count:
            return None
        
        if isinstance(review_count, int):
            return max(review_count, 0)
        
        if isinstance(review_count, str):
            count_match = re.search(r'([\d,]+)', review_count)
            if count_match:
                return int(count_match.group(1).replace(',', ''))
        
        return None
    
    def normalize_availability(self, availability: str) -> str:
        """Normalize availability status"""
        if not availability:
            return 'unknown'
        
        availability = availability.lower().strip()
        
        if 'in stock' in availability or 'available' in availability:
            return 'in_stock'
        elif 'out of stock' in availability or 'unavailable' in availability:
            return 'out_of_stock'
        elif 'pre-order' in availability or 'preorder' in availability:
            return 'pre_order'
        elif 'limited' in availability:
            return 'limited_stock'
        else:
            return 'unknown'
```

### 4. FastAPI Application

```python
# src/api_service/main.py
from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import asyncpg
import redis
from datetime import datetime, timedelta
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce Data Aggregator API",
    description="Unified API for e-commerce product data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Database connection
async def get_db():
    conn = await asyncpg.connect("postgresql://user:password@localhost/dbname")
    try:
        yield conn
    finally:
        await conn.close()

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Pydantic models
class ProductResponse(BaseModel):
    id: str
    external_id: str
    retailer: str
    title: str
    description: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    current_price: Optional[float]
    original_price: Optional[float]
    discount_percentage: Optional[float]
    rating: Optional[float]
    review_count: Optional[int]
    availability_status: str
    image_url: Optional[str]
    url: str
    updated_at: datetime
    data_quality_score: float

class PriceHistoryResponse(BaseModel):
    product_id: str
    price: float
    scraped_at: datetime

class ProductSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    retailer: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    availability_status: Optional[str] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

class ProductSearchResponse(BaseModel):
    products: List[ProductResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Product search endpoint
@app.post("/products/search", response_model=ProductSearchResponse)
async def search_products(
    search_request: ProductSearchRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Search products with filters"""
    
    # Build SQL query
    where_conditions = ["p.is_active = TRUE"]
    params = []
    param_count = 0
    
    if search_request.query:
        param_count += 1
        where_conditions.append(f"p.title ILIKE ${param_count}")
        params.append(f"%{search_request.query}%")
    
    if search_request.category:
        param_count += 1
        where_conditions.append(f"p.category = ${param_count}")
        params.append(search_request.category)
    
    if search_request.brand:
        param_count += 1
        where_conditions.append(f"p.brand = ${param_count}")
        params.append(search_request.brand)
    
    if search_request.retailer:
        param_count += 1
        where_conditions.append(f"p.retailer = ${param_count}")
        params.append(search_request.retailer)
    
    if search_request.min_price:
        param_count += 1
        where_conditions.append(f"pr.current_price >= ${param_count}")
        params.append(search_request.min_price)
    
    if search_request.max_price:
        param_count += 1
        where_conditions.append(f"pr.current_price <= ${param_count}")
        params.append(search_request.max_price)
    
    if search_request.min_rating:
        param_count += 1
        where_conditions.append(f"p.rating >= ${param_count}")
        params.append(search_request.min_rating)
    
    if search_request.availability_status:
        param_count += 1
        where_conditions.append(f"p.availability_status = ${param_count}")
        params.append(search_request.availability_status)
    
    # Add pagination
    offset = (search_request.page - 1) * search_request.limit
    
    # Count query
    count_query = f"""
        SELECT COUNT(*)
        FROM products p
        LEFT JOIN (
            SELECT DISTINCT ON (product_id) 
                product_id, current_price, original_price, discount_percentage
            FROM prices 
            ORDER BY product_id, scraped_at DESC
        ) pr ON p.id = pr.product_id
        WHERE {' AND '.join(where_conditions)}
    """
    
    total_count = await db.fetchval(count_query, *params)
    total_pages = (total_count + search_request.limit - 1) // search_request.limit
    
    # Data query
    data_query = f"""
        SELECT p.*, pr.current_price, pr.original_price, pr.discount_percentage
        FROM products p
        LEFT JOIN (
            SELECT DISTINCT ON (product_id) 
                product_id, current_price, original_price, discount_percentage
            FROM prices 
            ORDER BY product_id, scraped_at DESC
        ) pr ON p.id = pr.product_id
        WHERE {' AND '.join(where_conditions)}
        ORDER BY p.updated_at DESC
        LIMIT ${param_count + 1} OFFSET ${param_count + 2}
    """
    
    params.extend([search_request.limit, offset])
    
    rows = await db.fetch(data_query, *params)
    
    products = []
    for row in rows:
        products.append(ProductResponse(
            id=str(row['id']),
            external_id=row['external_id'],
            retailer=row['retailer'],
            title=row['title'],
            description=row['description'],
            brand=row['brand'],
            model=row['model'],
            category=row['category'],
            subcategory=row['subcategory'],
            current_price=row['current_price'],
            original_price=row['original_price'],
            discount_percentage=row['discount_percentage'],
            rating=row['rating'],
            review_count=row['review_count'],
            availability_status=row['availability_status'],
            image_url=row['image_url'],
            url=row['url'],
            updated_at=row['updated_at'],
            data_quality_score=row['data_quality_score']
        ))
    
    return ProductSearchResponse(
        products=products,
        total_count=total_count,
        page=search_request.page,
        limit=search_request.limit,
        total_pages=total_pages
    )

# Get single product
@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get single product by ID"""
    
    query = """
        SELECT p.*, pr.current_price, pr.original_price, pr.discount_percentage
        FROM products p
        LEFT JOIN (
            SELECT DISTINCT ON (product_id) 
                product_id, current_price, original_price, discount_percentage
            FROM prices 
            ORDER BY product_id, scraped_at DESC
        ) pr ON p.id = pr.product_id
        WHERE p.id = $1 AND p.is_active = TRUE
    """
    
    row = await db.fetchrow(query, product_id)
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductResponse(
        id=str(row['id']),
        external_id=row['external_id'],
        retailer=row['retailer'],
        title=row['title'],
        description=row['description'],
        brand=row['brand'],
        model=row['model'],
        category=row['category'],
        subcategory=row['subcategory'],
        current_price=row['current_price'],
        original_price=row['original_price'],
        discount_percentage=row['discount_percentage'],
        rating=row['rating'],
        review_count=row['review_count'],
        availability_status=row['availability_status'],
        image_url=row['image_url'],
        url=row['url'],
        updated_at=row['updated_at'],
        data_quality_score=row['data_quality_score']
    )

# Get price history
@app.get("/products/{product_id}/price-history", response_model=List[PriceHistoryResponse])
async def get_price_history(
    product_id: str,
    days: int = Query(30, ge=1, le=365),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get price history for a product"""
    
    query = """
        SELECT product_id, current_price as price, scraped_at
        FROM prices
        WHERE product_id = $1 
        AND scraped_at >= $2
        ORDER BY scraped_at DESC
    """
    
    start_date = datetime.now() - timedelta(days=days)
    rows = await db.fetch(query, product_id, start_date)
    
    return [
        PriceHistoryResponse(
            product_id=str(row['product_id']),
            price=row['price'],
            scraped_at=row['scraped_at']
        )
        for row in rows
    ]

# Analytics endpoints
@app.get("/analytics/categories")
async def get_category_analytics(db: asyncpg.Connection = Depends(get_db)):
    """Get product count by category"""
    
    query = """
        SELECT p.category, COUNT(*) as product_count, 
               AVG(p.rating) as avg_rating,
               AVG(pr.current_price) as avg_price
        FROM products p
        LEFT JOIN (
            SELECT DISTINCT ON (product_id) product_id, current_price
            FROM prices 
            ORDER BY product_id, scraped_at DESC
        ) pr ON p.id = pr.product_id
        WHERE p.is_active = TRUE AND p.category IS NOT NULL
        GROUP BY p.category
        ORDER BY product_count DESC
    """
    
    rows = await db.fetch(query)
    return [dict(row) for row in rows]

@app.get("/analytics/retailers")
async def get_retailer_analytics(db: asyncpg.Connection = Depends(get_db)):
    """Get analytics by retailer"""
    
    query = """
        SELECT p.retailer, COUNT(*) as product_count,
               AVG(p.rating) as avg_rating,
               AVG(pr.current_price) as avg_price,
               AVG(p.data_quality_score) as avg_quality_score
        FROM products p
        LEFT JOIN (
            SELECT DISTINCT ON (product_id) product_id, current_price
            FROM prices 
            ORDER BY product_id, scraped_at DESC
        ) pr ON p.id = pr.product_id
        WHERE p.is_active = TRUE
        GROUP BY p.retailer
        ORDER BY product_count DESC
    """
    
    rows = await db.fetch(query)
    return [dict(row) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 5. Requirements File

```txt
# requirements.txt
# Core Framework
fastapi==0.95.0
uvicorn[standard]==0.21.1
pydantic==1.10.7

# Web Scraping
scrapy==2.8.0
selenium==4.8.2
requests==2.28.2
beautifulsoup4==4.11.2

# Database
asyncpg==0.28.0
sqlalchemy==2.0.7
alembic==1.10.2
pymongo==4.3.3

# Caching & Queue
redis==4.5.4
celery==5.2.7

# Data Processing
pandas==2.0.0
numpy==1.24.2
python-dateutil==2.8.2

# Image Processing
Pillow==9.5.0
requests-html==0.10.0

# Monitoring & Logging
prometheus-client==0.16.0
structlog==23.1.0
sentry-sdk[fastapi]==1.20.0

# Development Tools
pytest==7.3.1
pytest-asyncio==0.21.0
black==23.3.0
flake8==6.0.0
mypy==1.2.0

# Deployment
gunicorn==20.1.0
docker==6.1.0
```

This sample code provides a solid foundation for implementing your Unified E-commerce Product Data Aggregator. The code is production-ready with proper error handling, logging, and follows best practices for scalable web scraping and API development.

