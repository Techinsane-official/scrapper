# Technical Architecture & Implementation Guide
## Unified E-commerce Product Data Aggregator

---

## Technology Stack Recommendations

### Backend Development
```python
# Core Framework Stack
Python 3.9+          # Primary language
Scrapy 2.8+          # Web scraping framework
FastAPI 0.95+        # Modern API framework
Celery 5.3+          # Distributed task queue
Redis 6.2+           # Caching and message broker
PostgreSQL 14+       # Primary database
MongoDB 5.0+         # Document storage
```

### Infrastructure & Deployment
```yaml
# Containerization
Docker 20.10+        # Container platform
Kubernetes 1.24+     # Orchestration
Nginx 1.22+          # Reverse proxy

# Cloud Platforms
AWS/Azure/GCP        # Cloud hosting
Elastic Beanstalk    # Application hosting
RDS/Cloud SQL        # Managed databases
S3/Blob Storage      # File storage
```

### Monitoring & Analytics
```python
# Observability Stack
Prometheus           # Metrics collection
Grafana             # Data visualization
ELK Stack           # Log aggregation
Sentry              # Error tracking
New Relic           # APM monitoring
```

---

## System Architecture Design

### Microservices Architecture

#### 1. Scraping Service
```python
# scraper_service/
├── spiders/
│   ├── amazon_spider.py
│   ├── walmart_spider.py
│   └── target_spider.py
├── middlewares/
│   ├── proxy_middleware.py
│   ├── user_agent_middleware.py
│   └── rate_limit_middleware.py
├── pipelines/
│   ├── data_validation.py
│   ├── duplicate_detection.py
│   └── database_storage.py
└── config/
    ├── settings.py
    └── retailers_config.py
```

#### 2. Data Processing Service
```python
# data_processing_service/
├── processors/
│   ├── product_normalizer.py
│   ├── price_validator.py
│   └── image_processor.py
├── models/
│   ├── product_model.py
│   ├── price_model.py
│   └── variation_model.py
├── utils/
│   ├── data_cleaning.py
│   ├── deduplication.py
│   └── quality_scoring.py
└── api/
    ├── endpoints.py
    └── schemas.py
```

#### 3. API Service
```python
# api_service/
├── routes/
│   ├── products.py
│   ├── prices.py
│   └── analytics.py
├── middleware/
│   ├── authentication.py
│   ├── rate_limiting.py
│   └── caching.py
├── models/
│   ├── database_models.py
│   └── response_models.py
└── utils/
    ├── pagination.py
    └── filtering.py
```

---

## Database Schema Design

### PostgreSQL Schema (Core Data)

```sql
-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(255) NOT NULL,
    retailer VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    brand VARCHAR(100),
    model VARCHAR(100),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    sku VARCHAR(100),
    upc VARCHAR(20),
    ean VARCHAR(20),
    asin VARCHAR(20),
    url TEXT NOT NULL,
    image_url TEXT,
    rating DECIMAL(3,2),
    review_count INTEGER DEFAULT 0,
    availability_status VARCHAR(20) DEFAULT 'unknown',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_quality_score DECIMAL(3,2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    
    UNIQUE(external_id, retailer),
    INDEX idx_retailer_external_id (retailer, external_id),
    INDEX idx_category (category),
    INDEX idx_brand (brand),
    INDEX idx_rating (rating),
    INDEX idx_updated_at (updated_at)
);

-- Prices table (Historical pricing)
CREATE TABLE prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    current_price DECIMAL(10,2) NOT NULL,
    original_price DECIMAL(10,2),
    discount_percentage DECIMAL(5,2),
    currency VARCHAR(3) DEFAULT 'USD',
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_product_scraped_at (product_id, scraped_at),
    INDEX idx_scraped_at (scraped_at)
);

-- Product variations
CREATE TABLE product_variations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    variation_type VARCHAR(50) NOT NULL, -- 'size', 'color', 'style'
    variation_value VARCHAR(100) NOT NULL,
    variation_price DECIMAL(10,2),
    availability_status VARCHAR(20),
    external_variation_id VARCHAR(255),
    
    INDEX idx_product_variation (product_id, variation_type),
    UNIQUE(product_id, variation_type, variation_value)
);

-- Product specifications
CREATE TABLE product_specifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    spec_name VARCHAR(100) NOT NULL,
    spec_value TEXT NOT NULL,
    spec_unit VARCHAR(20),
    
    INDEX idx_product_spec (product_id, spec_name),
    UNIQUE(product_id, spec_name, spec_value)
);

-- Scraping logs
CREATE TABLE scraping_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer VARCHAR(50) NOT NULL,
    scraping_type VARCHAR(50) NOT NULL, -- 'full', 'incremental', 'price_check'
    products_scraped INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    products_new INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'failed'
    
    INDEX idx_retailer_started_at (retailer, started_at),
    INDEX idx_status (status)
);
```

### MongoDB Collections (Complex Data)

```javascript
// Raw scraped data
{
  "_id": ObjectId,
  "retailer": "amazon",
  "product_url": "https://amazon.com/product/...",
  "scraped_at": ISODate,
  "raw_data": {
    "title": "Product Title",
    "price": "$99.99",
    "images": ["url1", "url2"],
    "specifications": {...},
    "reviews": [...],
    "variations": [...]
  },
  "processing_status": "pending|processed|failed",
  "error_details": {...}
}

// Product analytics
{
  "_id": ObjectId,
  "product_id": "uuid",
  "date": ISODate,
  "metrics": {
    "price_trend": "up|down|stable",
    "availability_changes": 3,
    "rating_changes": 0.1,
    "review_count_change": 15
  },
  "market_position": {
    "price_rank": 5,
    "rating_rank": 2,
    "availability_rank": 1
  }
}
```

---

## Sample Implementation Code

### 1. Scrapy Spider Example

```python
# spiders/amazon_spider.py
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import json
import re
from datetime import datetime

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['amazon.com']
    
    def __init__(self, category=None, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.category = category or 'electronics'
        
    def start_requests(self):
        """Generate initial requests for product categories"""
        base_url = f"https://www.amazon.com/s?k={self.category}&page=1"
        yield Request(
            url=base_url,
            callback=self.parse_search_results,
            meta={'page': 1}
        )
    
    def parse_search_results(self, response):
        """Parse search results page"""
        # Extract product URLs
        product_links = response.css('h2 a::attr(href)').getall()
        
        for link in product_links:
            product_url = urljoin(response.url, link)
            yield Request(
                url=product_url,
                callback=self.parse_product,
                meta={'dont_cache': True}
            )
        
        # Follow pagination
        next_page = response.css('a[aria-label="Next Page"]::attr(href)').get()
        if next_page:
            yield Request(
                url=urljoin(response.url, next_page),
                callback=self.parse_search_results
            )
    
    def parse_product(self, response):
        """Parse individual product page"""
        # Extract product data
        product_data = {
            'retailer': 'amazon',
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
            'bullet_points': self.extract_bullet_points(response)
        }
        
        yield product_data
    
    def extract_title(self, response):
        """Extract product title"""
        title = response.css('#productTitle::text').get()
        return title.strip() if title else None
    
    def extract_price(self, response):
        """Extract current price"""
        price_selectors = [
            '.a-price-whole::text',
            '.a-offscreen::text',
            '#priceblock_dealprice::text',
            '#priceblock_ourprice::text'
        ]
        
        for selector in price_selectors:
            price_text = response.css(selector).get()
            if price_text:
                # Clean price text
                price = re.sub(r'[^\d.]', '', price_text)
                return float(price) if price else None
        
        return None
    
    def extract_rating(self, response):
        """Extract customer rating"""
        rating_text = response.css('.a-icon-alt::text').get()
        if rating_text:
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            return float(rating_match.group(1)) if rating_match else None
        return None
    
    def extract_images(self, response):
        """Extract product images"""
        images = response.css('#altImages img::attr(src)').getall()
        # Convert to high-resolution URLs
        high_res_images = []
        for img in images:
            if img:
                high_res_img = img.replace('._AC_SX38_', '._AC_SX1000_')
                high_res_images.append(high_res_img)
        return high_res_images
    
    def extract_specifications(self, response):
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
    
    def extract_variations(self, response):
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
```

### 2. Data Processing Pipeline

```python
# processors/product_normalizer.py
from typing import Dict, List, Optional
import re
from datetime import datetime
import logging

class ProductNormalizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def normalize_product(self, raw_data: Dict) -> Dict:
        """Normalize scraped product data"""
        try:
            normalized = {
                'external_id': self.extract_external_id(raw_data),
                'retailer': raw_data.get('retailer'),
                'title': self.clean_title(raw_data.get('title')),
                'description': self.clean_description(raw_data.get('description')),
                'brand': self.extract_brand(raw_data),
                'model': self.extract_model(raw_data),
                'category': self.categorize_product(raw_data),
                'price': self.normalize_price(raw_data.get('price')),
                'original_price': self.normalize_price(raw_data.get('original_price')),
                'rating': self.normalize_rating(raw_data.get('rating')),
                'review_count': self.normalize_review_count(raw_data.get('review_count')),
                'availability': self.normalize_availability(raw_data.get('availability')),
                'images': self.process_images(raw_data.get('images', [])),
                'specifications': self.normalize_specifications(raw_data.get('specifications', {})),
                'variations': self.normalize_variations(raw_data.get('variations', [])),
                'url': raw_data.get('url'),
                'scraped_at': raw_data.get('scraped_at'),
                'data_quality_score': self.calculate_quality_score(raw_data)
            }
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizing product data: {e}")
            return None
    
    def extract_external_id(self, data: Dict) -> str:
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
    
    def normalize_price(self, price) -> Optional[float]:
        """Normalize price to float"""
        if not price:
            return None
        
        if isinstance(price, (int, float)):
            return float(price)
        
        if isinstance(price, str):
            # Extract numeric value
            price_match = re.search(r'[\d,]+\.?\d*', price.replace(',', ''))
            if price_match:
                return float(price_match.group(0))
        
        return None
    
    def calculate_quality_score(self, data: Dict) -> float:
        """Calculate data quality score (0-1)"""
        required_fields = ['title', 'price', 'url']
        optional_fields = ['description', 'rating', 'images', 'specifications']
        
        score = 0.0
        total_weight = 0.0
        
        # Required fields (70% weight)
        for field in required_fields:
            total_weight += 0.7 / len(required_fields)
            if data.get(field):
                score += 0.7 / len(required_fields)
        
        # Optional fields (30% weight)
        for field in optional_fields:
            total_weight += 0.3 / len(optional_fields)
            if data.get(field):
                score += 0.3 / len(optional_fields)
        
        return score / total_weight if total_weight > 0 else 0.0
```

### 3. FastAPI Application

```python
# api_service/main.py
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import asyncpg
import redis
from datetime import datetime, timedelta

app = FastAPI(title="E-commerce Data Aggregator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
class Product(BaseModel):
    id: str
    external_id: str
    retailer: str
    title: str
    description: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    category: Optional[str]
    current_price: Optional[float]
    original_price: Optional[float]
    discount_percentage: Optional[float]
    rating: Optional[float]
    review_count: Optional[int]
    availability_status: str
    image_url: Optional[str]
    url: str
    updated_at: datetime

class PriceHistory(BaseModel):
    product_id: str
    price: float
    scraped_at: datetime

class ProductSearch(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    retailer: Optional[str] = None
    page: int = 1
    limit: int = 20

# API Endpoints
@app.get("/products", response_model=List[Product])
async def search_products(
    search: ProductSearch = Depends(),
    db: asyncpg.Connection = Depends(get_db)
):
    """Search products with filters"""
    
    # Build SQL query
    where_conditions = ["is_active = TRUE"]
    params = []
    
    if search.query:
        where_conditions.append("title ILIKE $%d" % (len(params) + 1))
        params.append(f"%{search.query}%")
    
    if search.category:
        where_conditions.append("category = $%d" % (len(params) + 1))
        params.append(search.category)
    
    if search.brand:
        where_conditions.append("brand = $%d" % (len(params) + 1))
        params.append(search.brand)
    
    if search.min_price:
        where_conditions.append("current_price >= $%d" % (len(params) + 1))
        params.append(search.min_price)
    
    if search.max_price:
        where_conditions.append("current_price <= $%d" % (len(params) + 1))
        params.append(search.max_price)
    
    if search.min_rating:
        where_conditions.append("rating >= $%d" % (len(params) + 1))
        params.append(search.min_rating)
    
    if search.retailer:
        where_conditions.append("retailer = $%d" % (len(params) + 1))
        params.append(search.retailer)
    
    # Add pagination
    offset = (search.page - 1) * search.limit
    
    query = f"""
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
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    
    params.extend([search.limit, offset])
    
    rows = await db.fetch(query, *params)
    
    products = []
    for row in rows:
        products.append(Product(
            id=str(row['id']),
            external_id=row['external_id'],
            retailer=row['retailer'],
            title=row['title'],
            description=row['description'],
            brand=row['brand'],
            model=row['model'],
            category=row['category'],
            current_price=row['current_price'],
            original_price=row['original_price'],
            discount_percentage=row['discount_percentage'],
            rating=row['rating'],
            review_count=row['review_count'],
            availability_status=row['availability_status'],
            image_url=row['image_url'],
            url=row['url'],
            updated_at=row['updated_at']
        ))
    
    return products

@app.get("/products/{product_id}", response_model=Product)
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
    
    return Product(
        id=str(row['id']),
        external_id=row['external_id'],
        retailer=row['retailer'],
        title=row['title'],
        description=row['description'],
        brand=row['brand'],
        model=row['model'],
        category=row['category'],
        current_price=row['current_price'],
        original_price=row['original_price'],
        discount_percentage=row['discount_percentage'],
        rating=row['rating'],
        review_count=row['review_count'],
        availability_status=row['availability_status'],
        image_url=row['image_url'],
        url=row['url'],
        updated_at=row['updated_at']
    )

@app.get("/products/{product_id}/price-history", response_model=List[PriceHistory])
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
        PriceHistory(
            product_id=str(row['product_id']),
            price=row['price'],
            scraped_at=row['scraped_at']
        )
        for row in rows
    ]

@app.get("/analytics/categories")
async def get_category_analytics(db: asyncpg.Connection = Depends(get_db)):
    """Get product count by category"""
    
    query = """
        SELECT category, COUNT(*) as product_count, 
               AVG(rating) as avg_rating,
               AVG(current_price) as avg_price
        FROM products p
        LEFT JOIN (
            SELECT DISTINCT ON (product_id) product_id, current_price
            FROM prices 
            ORDER BY product_id, scraped_at DESC
        ) pr ON p.id = pr.product_id
        WHERE p.is_active = TRUE AND p.category IS NOT NULL
        GROUP BY category
        ORDER BY product_count DESC
    """
    
    rows = await db.fetch(query)
    return [dict(row) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Deployment Configuration

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: ecommerce_aggregator
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6.2-alpine
    ports:
      - "6379:6379"

  mongodb:
    image: mongo:5.0
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/ecommerce_aggregator
      REDIS_URL: redis://redis:6379
      MONGODB_URL: mongodb://admin:password@mongodb:27017
    depends_on:
      - postgres
      - redis
      - mongodb

  scraper:
    build: .
    command: scrapy crawl amazon
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/ecommerce_aggregator
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  mongodb_data:
```

### Kubernetes Configuration

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-aggregator-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ecommerce-aggregator-api
  template:
    metadata:
      labels:
        app: ecommerce-aggregator-api
    spec:
      containers:
      - name: api
        image: ecommerce-aggregator:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: ecommerce-aggregator-service
spec:
  selector:
    app: ecommerce-aggregator-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

This technical architecture provides a solid foundation for building your Unified E-commerce Product Data Aggregator. The system is designed to be scalable, maintainable, and production-ready with proper monitoring and deployment configurations.

