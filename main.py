from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import aiohttp
import json
import os
from datetime import datetime
import uuid
from bs4 import BeautifulSoup
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://ndyhnflavubulhjickkj.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5keWhuZmxhdnVidWxoamlja2tqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODQ0NjI1OCwiZXhwIjoyMDc0MDIyMjU4fQ.SEcFx7Posp3e3TJPKxuzUsKWEB0jprgd2F61rKIz7PE")

app = FastAPI(title="Premium Scraper API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# In-memory storage for jobs and products (will be replaced with database)
jobs_db = {}
products_db = {}

# Supabase helper functions
async def supabase_request(method: str, table: str, data: dict = None, params: dict = None):
    """Make a request to Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, headers=headers, json=data, params=params) as response:
            if response.status >= 400:
                error_text = await response.text()
                logger.error(f"Supabase error: {response.status} - {error_text}")
                raise HTTPException(status_code=response.status, detail=f"Database error: {error_text}")
            
            if response.status == 204:  # No content
                return None
            
            return await response.json()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class ScrapingJobCreate(BaseModel):
    url: str
    job_type: str = "amazon_product"
    max_pages: int = 1
    keywords: Optional[str] = None

class ScrapingJob(BaseModel):
    id: str
    url: str
    job_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    products_count: int = 0
    max_pages: int = 1
    keywords: Optional[str] = None

class Product(BaseModel):
    id: str
    job_id: str
    title: str
    price: Optional[str] = None
    rating: Optional[str] = None
    reviews_count: Optional[str] = None
    image_url: Optional[str] = None
    url: str
    scraped_at: datetime

# Authentication functions
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Simple token verification (replace with JWT in production)
    token = credentials.credentials
    if token == "demo_token":  # Demo token for testing
        return {"user_id": "demo_user", "email": "demo@example.com"}
    raise HTTPException(status_code=401, detail="Invalid token")

# Enhanced scraping functions
async def scrape_amazon_product(url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Enhanced Amazon product scraper with comprehensive data extraction"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Initialize comprehensive product data
            product_data = {
                'title': '',
                'description': '',
                'bullet_points': [],
                'brand': '',
                'model': '',
                'sku': '',
                'category': '',
                'subcategory': '',
                'current_price': None,
                'original_price': None,
                'discount_percentage': None,
                'availability': 'unknown',
                'stock_quantity': None,
                'shipping_info': '',
                'primary_image_url': '',
                'additional_images': [],
                'video_urls': [],
                'specifications': {},
                'dimensions': {},
                'materials': [],
                'features': [],
                'compatibility': [],
                'variations': [],
                'rating': None,
                'review_count': None,
                'review_distribution': {},
                'best_seller_rank': None,
                'source_url': url,
                'retailer': 'amazon',
                'last_updated': datetime.now().isoformat(),
                'data_quality_score': 0.0,
                'scraping_status': 'completed'
            }
            
            # Title extraction
            title_selectors = [
                '#productTitle',
                'h1.a-size-large',
                '.a-size-large.product-title-word-break',
                'h1[data-automation-id="product-title"]'
            ]
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    product_data['title'] = title_elem.get_text().strip()
                    break
            
            # Description extraction
            desc_selectors = [
                '#feature-bullets ul',
                '.a-unordered-list.a-vertical.a-spacing-mini',
                '#productDescription p'
            ]
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    if selector == '#productDescription p':
                        product_data['description'] = desc_elem.get_text().strip()
                    else:
                        # Extract bullet points
                        bullets = desc_elem.find_all('li')
                        product_data['bullet_points'] = [li.get_text().strip() for li in bullets if li.get_text().strip()]
                    break
            
            # Brand extraction
            brand_selectors = [
                '#bylineInfo',
                '.a-link-normal[href*="/brand/"]',
                'a[href*="/brand/"]'
            ]
            for selector in brand_selectors:
                brand_elem = soup.select_one(selector)
                if brand_elem:
                    product_data['brand'] = brand_elem.get_text().strip()
                    break
            
            # Price extraction (enhanced)
            price_selectors = [
                '.a-price-whole',
                '.a-price .a-offscreen',
                '#priceblock_dealprice',
                '#priceblock_ourprice',
                '.a-price-range .a-offscreen',
                '.a-price .a-price-whole'
            ]
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text().strip()
                    # Extract numeric price
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace('$', '').replace(',', ''))
                    if price_match:
                        try:
                            product_data['current_price'] = float(price_match.group())
                        except ValueError:
                            pass
                    break
            
            # Original price (for discounts)
            original_price_elem = soup.select_one('.a-text-price .a-offscreen')
            if original_price_elem:
                original_price_text = original_price_elem.get_text().strip()
                original_price_match = re.search(r'[\d,]+\.?\d*', original_price_text.replace('$', '').replace(',', ''))
                if original_price_match:
                    try:
                        product_data['original_price'] = float(original_price_match.group())
                        if product_data['current_price'] and product_data['original_price']:
                            discount = ((product_data['original_price'] - product_data['current_price']) / product_data['original_price']) * 100
                            product_data['discount_percentage'] = round(discount, 2)
                    except ValueError:
                        pass
            
            # Availability extraction
            availability_selectors = [
                '#availability span',
                '.a-size-medium.a-color-success',
                '.a-size-medium.a-color-price',
                '#outOfStock'
            ]
            for selector in availability_selectors:
                avail_elem = soup.select_one(selector)
                if avail_elem:
                    avail_text = avail_elem.get_text().strip().lower()
                    if 'in stock' in avail_text:
                        product_data['availability'] = 'in_stock'
                    elif 'out of stock' in avail_text or 'unavailable' in avail_text:
                        product_data['availability'] = 'out_of_stock'
                    elif 'pre-order' in avail_text:
                        product_data['availability'] = 'pre_order'
                    elif 'limited' in avail_text:
                        product_data['availability'] = 'limited_stock'
                    break
            
            # Rating extraction
            rating_elem = soup.select_one('.a-icon-alt')
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    try:
                        product_data['rating'] = float(rating_match.group(1))
                    except ValueError:
                        pass
            
            # Reviews count extraction
            reviews_elem = soup.select_one('#acrCustomerReviewText')
            if reviews_elem:
                reviews_text = reviews_elem.get_text()
                reviews_match = re.search(r'(\d+)', reviews_text.replace(',', ''))
                if reviews_match:
                    try:
                        product_data['review_count'] = int(reviews_match.group(1))
                    except ValueError:
                        pass
            
            # Primary image extraction
            img_selectors = [
                '#landingImage',
                '#imgBlkFront',
                '.a-dynamic-image'
            ]
            for selector in img_selectors:
                img_elem = soup.select_one(selector)
                if img_elem:
                    product_data['primary_image_url'] = img_elem.get('src') or img_elem.get('data-src')
                    break
            
            # Additional images
            additional_imgs = soup.select('#altImages img')
            for img in additional_imgs:
                img_url = img.get('src') or img.get('data-src')
                if img_url and img_url not in product_data['additional_images']:
                    product_data['additional_images'].append(img_url)
            
            # Specifications extraction
            spec_table = soup.select_one('#productDetails_techSpec_section_1 table')
            if spec_table:
                rows = spec_table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) == 2:
                        key = cells[0].get_text().strip()
                        value = cells[1].get_text().strip()
                        if key and value:
                            product_data['specifications'][key] = value
            
            # Features extraction
            features_section = soup.select_one('#feature-bullets')
            if features_section:
                feature_items = features_section.find_all('li')
                for item in feature_items:
                    feature_text = item.get_text().strip()
                    if feature_text and len(feature_text) > 10:  # Filter out short items
                        product_data['features'].append(feature_text)
            
            # Best seller rank
            bsr_elem = soup.select_one('#SalesRank')
            if bsr_elem:
                bsr_text = bsr_elem.get_text()
                bsr_match = re.search(r'#(\d+)', bsr_text.replace(',', ''))
                if bsr_match:
                    try:
                        product_data['best_seller_rank'] = int(bsr_match.group(1))
                    except ValueError:
                        pass
            
            # Calculate data quality score
            quality_score = 0.0
            if product_data['title']: quality_score += 0.2
            if product_data['current_price']: quality_score += 0.15
            if product_data['rating']: quality_score += 0.1
            if product_data['primary_image_url']: quality_score += 0.1
            if product_data['brand']: quality_score += 0.1
            if product_data['availability'] != 'unknown': quality_score += 0.1
            if product_data['specifications']: quality_score += 0.1
            if product_data['features']: quality_score += 0.1
            if product_data['bullet_points']: quality_score += 0.05
            
            product_data['data_quality_score'] = min(quality_score, 1.0)
            
            return product_data
            
    except Exception as e:
        logger.error(f"Error scraping Amazon product: {e}")
        raise e

async def scrape_walmart_product(url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Enhanced Walmart product scraper"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch Walmart page: {response.status}")
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            product_data = {
                'title': '',
                'description': '',
                'bullet_points': [],
                'brand': '',
                'model': '',
                'sku': '',
                'category': '',
                'subcategory': '',
                'current_price': None,
                'original_price': None,
                'discount_percentage': None,
                'availability': 'unknown',
                'stock_quantity': None,
                'shipping_info': '',
                'primary_image_url': '',
                'additional_images': [],
                'video_urls': [],
                'specifications': {},
                'dimensions': {},
                'materials': [],
                'features': [],
                'compatibility': [],
                'variations': [],
                'rating': None,
                'review_count': None,
                'review_distribution': {},
                'best_seller_rank': None,
                'source_url': url,
                'retailer': 'walmart',
                'last_updated': datetime.now().isoformat(),
                'data_quality_score': 0.0,
                'scraping_status': 'completed'
            }
            
            # Title extraction
            title_elem = soup.select_one('h1[data-automation-id="product-title"]')
            if title_elem:
                product_data['title'] = title_elem.get_text().strip()
            
            # Price extraction
            price_elem = soup.select_one('[data-automation-id="product-price"]')
            if price_elem:
                price_text = price_elem.get_text().strip()
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace('$', '').replace(',', ''))
                if price_match:
                    try:
                        product_data['current_price'] = float(price_match.group())
                    except ValueError:
                        pass
            
            # Rating extraction
            rating_elem = soup.select_one('[data-automation-id="product-rating"]')
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    try:
                        product_data['rating'] = float(rating_match.group(1))
                    except ValueError:
                        pass
            
            # Reviews count
            reviews_elem = soup.select_one('[data-automation-id="product-review-count"]')
            if reviews_elem:
                reviews_text = reviews_elem.get_text()
                reviews_match = re.search(r'(\d+)', reviews_text.replace(',', ''))
                if reviews_match:
                    try:
                        product_data['review_count'] = int(reviews_match.group(1))
                    except ValueError:
                        pass
            
            # Primary image
            img_elem = soup.select_one('[data-automation-id="product-image"] img')
            if img_elem:
                product_data['primary_image_url'] = img_elem.get('src') or img_elem.get('data-src')
            
            # Availability
            availability_elem = soup.select_one('[data-automation-id="product-availability"]')
            if availability_elem:
                avail_text = availability_elem.get_text().strip().lower()
                if 'in stock' in avail_text:
                    product_data['availability'] = 'in_stock'
                elif 'out of stock' in avail_text:
                    product_data['availability'] = 'out_of_stock'
            
            # Calculate quality score
            quality_score = 0.0
            if product_data['title']: quality_score += 0.2
            if product_data['current_price']: quality_score += 0.15
            if product_data['rating']: quality_score += 0.1
            if product_data['primary_image_url']: quality_score += 0.1
            if product_data['availability'] != 'unknown': quality_score += 0.1
            
            product_data['data_quality_score'] = min(quality_score, 1.0)
            
            return product_data
            
    except Exception as e:
        logger.error(f"Error scraping Walmart product: {e}")
        raise e

async def scrape_target_product(url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Enhanced Target product scraper"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch Target page: {response.status}")
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            product_data = {
                'title': '',
                'description': '',
                'bullet_points': [],
                'brand': '',
                'model': '',
                'sku': '',
                'category': '',
                'subcategory': '',
                'current_price': None,
                'original_price': None,
                'discount_percentage': None,
                'availability': 'unknown',
                'stock_quantity': None,
                'shipping_info': '',
                'primary_image_url': '',
                'additional_images': [],
                'video_urls': [],
                'specifications': {},
                'dimensions': {},
                'materials': [],
                'features': [],
                'compatibility': [],
                'variations': [],
                'rating': None,
                'review_count': None,
                'review_distribution': {},
                'best_seller_rank': None,
                'source_url': url,
                'retailer': 'target',
                'last_updated': datetime.now().isoformat(),
                'data_quality_score': 0.0,
                'scraping_status': 'completed'
            }
            
            # Title extraction
            title_elem = soup.select_one('h1[data-test="product-title"]')
            if title_elem:
                product_data['title'] = title_elem.get_text().strip()
            
            # Price extraction
            price_elem = soup.select_one('[data-test="product-price"]')
            if price_elem:
                price_text = price_elem.get_text().strip()
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace('$', '').replace(',', ''))
                if price_match:
                    try:
                        product_data['current_price'] = float(price_match.group())
                    except ValueError:
                        pass
            
            # Rating extraction
            rating_elem = soup.select_one('[data-test="product-rating"]')
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    try:
                        product_data['rating'] = float(rating_match.group(1))
                    except ValueError:
                        pass
            
            # Reviews count
            reviews_elem = soup.select_one('[data-test="product-review-count"]')
            if reviews_elem:
                reviews_text = reviews_elem.get_text()
                reviews_match = re.search(r'(\d+)', reviews_text.replace(',', ''))
                if reviews_match:
                    try:
                        product_data['review_count'] = int(reviews_match.group(1))
                    except ValueError:
                        pass
            
            # Primary image
            img_elem = soup.select_one('[data-test="product-image"] img')
            if img_elem:
                product_data['primary_image_url'] = img_elem.get('src') or img_elem.get('data-src')
            
            # Availability
            availability_elem = soup.select_one('[data-test="product-availability"]')
            if availability_elem:
                avail_text = availability_elem.get_text().strip().lower()
                if 'in stock' in avail_text:
                    product_data['availability'] = 'in_stock'
                elif 'out of stock' in avail_text:
                    product_data['availability'] = 'out_of_stock'
            
            # Calculate quality score
            quality_score = 0.0
            if product_data['title']: quality_score += 0.2
            if product_data['current_price']: quality_score += 0.15
            if product_data['rating']: quality_score += 0.1
            if product_data['primary_image_url']: quality_score += 0.1
            if product_data['availability'] != 'unknown': quality_score += 0.1
            
            product_data['data_quality_score'] = min(quality_score, 1.0)
            
            return product_data
            
    except Exception as e:
        logger.error(f"Error scraping Target product: {e}")
        raise e

async def scrape_bestbuy_product(url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Enhanced Best Buy product scraper"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch Best Buy page: {response.status}")
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            product_data = {
                'title': '',
                'description': '',
                'bullet_points': [],
                'brand': '',
                'model': '',
                'sku': '',
                'category': '',
                'subcategory': '',
                'current_price': None,
                'original_price': None,
                'discount_percentage': None,
                'availability': 'unknown',
                'stock_quantity': None,
                'shipping_info': '',
                'primary_image_url': '',
                'additional_images': [],
                'video_urls': [],
                'specifications': {},
                'dimensions': {},
                'materials': [],
                'features': [],
                'compatibility': [],
                'variations': [],
                'rating': None,
                'review_count': None,
                'review_distribution': {},
                'best_seller_rank': None,
                'source_url': url,
                'retailer': 'bestbuy',
                'last_updated': datetime.now().isoformat(),
                'data_quality_score': 0.0,
                'scraping_status': 'completed'
            }
            
            # Title extraction
            title_elem = soup.select_one('h1[data-test="product-title"]')
            if title_elem:
                product_data['title'] = title_elem.get_text().strip()
            
            # Price extraction
            price_elem = soup.select_one('[data-test="product-price"]')
            if price_elem:
                price_text = price_elem.get_text().strip()
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace('$', '').replace(',', ''))
                if price_match:
                    try:
                        product_data['current_price'] = float(price_match.group())
                    except ValueError:
                        pass
            
            # Rating extraction
            rating_elem = soup.select_one('[data-test="product-rating"]')
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    try:
                        product_data['rating'] = float(rating_match.group(1))
                    except ValueError:
                        pass
            
            # Reviews count
            reviews_elem = soup.select_one('[data-test="product-review-count"]')
            if reviews_elem:
                reviews_text = reviews_elem.get_text()
                reviews_match = re.search(r'(\d+)', reviews_text.replace(',', ''))
                if reviews_match:
                    try:
                        product_data['review_count'] = int(reviews_match.group(1))
                    except ValueError:
                        pass
            
            # Primary image
            img_elem = soup.select_one('[data-test="product-image"] img')
            if img_elem:
                product_data['primary_image_url'] = img_elem.get('src') or img_elem.get('data-src')
            
            # Availability
            availability_elem = soup.select_one('[data-test="product-availability"]')
            if availability_elem:
                avail_text = availability_elem.get_text().strip().lower()
                if 'in stock' in avail_text:
                    product_data['availability'] = 'in_stock'
                elif 'out of stock' in avail_text:
                    product_data['availability'] = 'out_of_stock'
            
            # Calculate quality score
            quality_score = 0.0
            if product_data['title']: quality_score += 0.2
            if product_data['current_price']: quality_score += 0.15
            if product_data['rating']: quality_score += 0.1
            if product_data['primary_image_url']: quality_score += 0.1
            if product_data['availability'] != 'unknown': quality_score += 0.1
            
            product_data['data_quality_score'] = min(quality_score, 1.0)
            
            return product_data
            
    except Exception as e:
        logger.error(f"Error scraping Best Buy product: {e}")
        raise e

async def execute_scraping_job(job_id: str, job_data: ScrapingJobCreate):
    """Execute a scraping job in the background with multi-retailer support"""
    try:
        jobs_db[job_id]['status'] = 'running'
        logger.info(f"Starting job {job_id} for retailer: {job_data.retailer}")
        
        products = []
        async with aiohttp.ClientSession() as session:
            # Determine which scraper to use based on retailer
            scraper_map = {
                'amazon': scrape_amazon_product,
                'walmart': scrape_walmart_product,
                'target': scrape_target_product,
                'bestbuy': scrape_bestbuy_product
            }
            
            scraper_func = scraper_map.get(job_data.retailer.lower())
            if not scraper_func:
                raise Exception(f"Unsupported retailer: {job_data.retailer}")
            
            # Handle different job types
            if job_data.job_type == "product":
                # Single product scraping
                product_data = await scraper_func(job_data.url, session)
                product_data['id'] = str(uuid.uuid4())
                product_data['job_id'] = job_id
                product_data['scraped_at'] = datetime.now()
                
                products.append(product_data)
                products_db[product_data['id']] = product_data
                
            elif job_data.job_type == "search":
                # Search-based scraping (placeholder for now)
                logger.info(f"Search scraping not yet implemented for {job_data.retailer}")
                
            elif job_data.job_type == "catalog":
                # Catalog scraping (placeholder for now)
                logger.info(f"Catalog scraping not yet implemented for {job_data.retailer}")
        
        jobs_db[job_id]['status'] = 'completed'
        jobs_db[job_id]['completed_at'] = datetime.now()
        jobs_db[job_id]['products_count'] = len(products)
        
        logger.info(f"Job {job_id} completed successfully with {len(products)} products")
        
    except Exception as e:
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['error'] = str(e)
        logger.error(f"Job {job_id} failed: {e}")

# Real-time price monitoring and sync
async def monitor_price_changes():
    """Monitor price changes for existing products"""
    try:
        logger.info("Starting price monitoring cycle")
        
        # Get products that need price updates (last updated > 1 hour ago)
        products_to_update = []
        current_time = datetime.now()
        
        for product_id, product in products_db.items():
            last_updated = product.get('last_updated')
            if isinstance(last_updated, str):
                last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            
            # Check if product needs update (older than 1 hour)
            if (current_time - last_updated).total_seconds() > 3600:  # 1 hour
                products_to_update.append(product)
        
        logger.info(f"Found {len(products_to_update)} products needing price updates")
        
        # Update prices in batches
        async with aiohttp.ClientSession() as session:
            for product in products_to_update[:10]:  # Limit to 10 products per cycle
                try:
                    retailer = product.get('retailer', 'amazon')
                    url = product.get('source_url')
                    
                    if not url:
                        continue
                    
                    # Determine scraper function
                    scraper_map = {
                        'amazon': scrape_amazon_product,
                        'walmart': scrape_walmart_product,
                        'target': scrape_target_product,
                        'bestbuy': scrape_bestbuy_product
                    }
                    
                    scraper_func = scraper_map.get(retailer.lower())
                    if not scraper_func:
                        continue
                    
                    # Scrape updated product data
                    updated_data = await scraper_func(url, session)
                    
                    # Check for price changes
                    old_price = product.get('current_price')
                    new_price = updated_data.get('current_price')
                    
                    if old_price and new_price and old_price != new_price:
                        price_change = {
                            'product_id': product['id'],
                            'old_price': old_price,
                            'new_price': new_price,
                            'change_percentage': ((new_price - old_price) / old_price) * 100,
                            'detected_at': datetime.now().isoformat()
                        }
                        
                        logger.info(f"Price change detected for {product['title']}: ${old_price} -> ${new_price}")
                        
                        # Store price change in database
                        if 'price_changes' not in globals():
                            globals()['price_changes'] = {}
                        price_changes[f"{product['id']}_{datetime.now().timestamp()}"] = price_change
                    
                    # Update product data
                    product.update(updated_data)
                    product['last_updated'] = datetime.now().isoformat()
                    
                    # Add small delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error updating price for product {product.get('id')}: {e}")
                    continue
        
        logger.info("Price monitoring cycle completed")
        
    except Exception as e:
        logger.error(f"Error in price monitoring: {e}")

async def schedule_price_monitoring():
    """Schedule price monitoring to run every hour"""
    while True:
        try:
            await monitor_price_changes()
            # Wait for 1 hour before next cycle
            await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"Error in scheduled price monitoring: {e}")
            # Wait 5 minutes before retrying
            await asyncio.sleep(300)

# API Routes
@app.get("/")
async def root():
    return {"message": "Premium Scraper API is running!", "status": "success", "version": "1.0.0"}

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {"message": "API is working", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is working", "timestamp": datetime.now()}

@app.post("/api/auth/register")
async def register(user: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_users = await supabase_request("GET", "users", params={"email": f"eq.{user.email}"})
        if existing_users:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        user_data = {
            "id": str(uuid.uuid4()),
            "email": user.email,
            "full_name": user.full_name,
            "password": user.password,  # In production, hash this password
            "role": "user",
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        
        result = await supabase_request("POST", "users", data=user_data)
        logger.info(f"User registered: {user.email}")
        
        return {"message": "User created successfully", "user_id": user_data["id"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login")
async def login(user: UserLogin):
    """Login user"""
    try:
        # Find user in database
        users = await supabase_request("GET", "users", params={"email": f"eq.{user.email}"})
        if not users:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_data = users[0]
        
        # Simple password check (in production, use proper password hashing)
        if user_data.get("password") != user.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"User logged in: {user.email}")
        
        return {
            "access_token": "demo_token",
            "token_type": "bearer",
            "user": {
                "id": user_data["id"],
                "email": user_data["email"],
                "full_name": user_data["full_name"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/user/me")
async def get_current_user(current_user: dict = Depends(verify_token)):
    """Get current user info"""
    return current_user

@app.get("/api/auth/me")
async def get_auth_user(current_user: dict = Depends(verify_token)):
    """Get current authenticated user info"""
    return current_user

@app.post("/api/jobs")
async def create_job(job: ScrapingJobCreate, background_tasks: BackgroundTasks, current_user: dict = Depends(verify_token)):
    """Create a new scraping job"""
    job_id = str(uuid.uuid4())
    
    job_data = ScrapingJob(
        id=job_id,
        url=job.url,
        job_type=job.job_type,
        status="pending",
        created_at=datetime.now(),
        max_pages=job.max_pages,
        keywords=job.keywords
    )
    
    jobs_db[job_id] = job_data.dict()
    
    # Start job in background
    background_tasks.add_task(execute_scraping_job, job_id, job)
    
    return {"message": "Job created successfully", "job_id": job_id, "job": job_data}

@app.get("/api/jobs")
async def get_jobs(current_user: dict = Depends(verify_token)):
    """Get all jobs for current user"""
    try:
        # If no jobs exist, return empty array
        if not jobs_db:
            return {"jobs": [], "total": 0}
        
        jobs = list(jobs_db.values())
        return {"jobs": jobs, "total": len(jobs)}
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        return {"jobs": [], "total": 0}

@app.get("/api/jobs-public")
async def get_jobs_public():
    """Public jobs endpoint for testing"""
    try:
        # If no jobs exist, return empty array
        if not jobs_db:
            return {"jobs": [], "total": 0}
        
        jobs = list(jobs_db.values())
        return {"jobs": jobs, "total": len(jobs)}
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        return {"jobs": [], "total": 0}

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str, current_user: dict = Depends(verify_token)):
    """Get specific job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job": jobs_db[job_id]}

@app.get("/api/products")
async def get_products(job_id: Optional[str] = None, current_user: dict = Depends(verify_token)):
    """Get scraped products"""
    products = list(products_db.values())
    
    if job_id:
        products = [p for p in products if p['job_id'] == job_id]
    
    return {"products": products, "total": len(products)}

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(verify_token)):
    """Get enhanced dashboard statistics"""
    try:
        total_jobs = len(jobs_db)
        completed_jobs = len([j for j in jobs_db.values() if j['status'] == 'completed'])
        running_jobs = len([j for j in jobs_db.values() if j['status'] == 'running'])
        total_products = len(products_db)
        
        # Calculate retailer distribution
        retailer_counts = {}
        for product in products_db.values():
            retailer = product.get('retailer', 'unknown')
            retailer_counts[retailer] = retailer_counts.get(retailer, 0) + 1
        
        # Calculate data quality metrics
        quality_scores = [p.get('data_quality_score', 0) for p in products_db.values()]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Count curated products
        curated_products = len([p for p in products_db.values() if p.get('is_curated', False)])
        
        # Price changes today
        today_changes = 0
        if 'price_changes' in globals():
            today = datetime.now().date()
            for change in price_changes.values():
                change_date = datetime.fromisoformat(change['detected_at']).date()
                if change_date == today:
                    today_changes += 1
        
        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "running_jobs": running_jobs,
            "total_products": total_products,
            "curated_products": curated_products,
            "retailer_distribution": retailer_counts,
            "average_data_quality": round(avg_quality, 2),
            "price_changes_today": today_changes,
            "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/price-changes")
async def get_price_changes(current_user: dict = Depends(verify_token)):
    """Get recent price changes"""
    try:
        if 'price_changes' not in globals():
            return {"price_changes": []}
        
        # Sort by detection time (most recent first)
        changes = sorted(price_changes.values(), 
                        key=lambda x: x['detected_at'], 
                        reverse=True)
        
        return {"price_changes": changes[:50]}  # Return last 50 changes
    except Exception as e:
        logger.error(f"Error getting price changes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/start-price-monitoring")
async def start_price_monitoring(current_user: dict = Depends(verify_token)):
    """Start price monitoring service"""
    try:
        # Start price monitoring in background
        import asyncio
        asyncio.create_task(schedule_price_monitoring())
        
        return {"message": "Price monitoring started", "status": "success"}
    except Exception as e:
        logger.error(f"Error starting price monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scheduled-jobs")
async def get_scheduled_jobs(current_user: dict = Depends(verify_token)):
    """Get all scheduled jobs"""
    try:
        # Import scheduler if not already imported
        try:
            from src.scheduling.scheduler import job_scheduler
            scheduled_jobs = job_scheduler.get_scheduled_jobs()
            next_runs = job_scheduler.get_next_run_times()
            
            return {
                "scheduled_jobs": scheduled_jobs,
                "next_runs": next_runs,
                "total_jobs": len(scheduled_jobs)
            }
        except ImportError:
            return {
                "scheduled_jobs": [],
                "next_runs": {},
                "total_jobs": 0,
                "message": "Scheduler not available"
            }
    except Exception as e:
        logger.error(f"Error getting scheduled jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule-job")
async def schedule_job(
    job_config: dict,
    current_user: dict = Depends(verify_token)
):
    """Schedule a new automated job"""
    try:
        from src.scheduling.scheduler import job_scheduler
        
        retailer = job_config.get('retailer')
        job_type = job_config.get('job_type')
        schedule_type = job_config.get('schedule', 'daily')
        job_name = job_config.get('name', f'Scheduled {job_type} job')
        
        job_id = None
        
        if job_type == 'catalog':
            category_url = job_config.get('category_url')
            if schedule_type == 'daily':
                job_id = job_scheduler.schedule_daily_catalog_scrape(
                    retailer=retailer,
                    category_url=category_url,
                    job_name=job_name
                )
        elif job_type == 'price_update':
            product_urls = job_config.get('product_urls', [])
            if schedule_type == 'hourly':
                job_id = job_scheduler.schedule_hourly_price_updates(
                    retailer=retailer,
                    product_urls=product_urls,
                    job_name=job_name
                )
        elif job_type == 'search':
            search_queries = job_config.get('search_queries', [])
            if schedule_type == 'weekly':
                job_id = job_scheduler.schedule_weekly_search_scrape(
                    retailer=retailer,
                    search_queries=search_queries,
                    job_name=job_name
                )
        
        if job_id:
            return {
                "message": "Job scheduled successfully",
                "job_id": job_id,
                "status": "success"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid job configuration")
            
    except Exception as e:
        logger.error(f"Error scheduling job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/scheduled-jobs/{job_id}")
async def cancel_scheduled_job(
    job_id: str,
    current_user: dict = Depends(verify_token)
):
    """Cancel a scheduled job"""
    try:
        from src.scheduling.scheduler import job_scheduler
        
        success = job_scheduler.cancel_scheduled_job(job_id)
        
        if success:
            return {"message": "Job cancelled successfully", "status": "success"}
        else:
            raise HTTPException(status_code=404, detail="Job not found")
            
    except Exception as e:
        logger.error(f"Error cancelling scheduled job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Product curation endpoints
@app.post("/api/curate-products")
async def curate_products(
    curation_rules: dict,
    current_user: dict = Depends(verify_token)
):
    """Apply curation rules to products"""
    try:
        from src.processing.normalizer import CurationEngine
        
        curation_engine = CurationEngine()
        
        # Get all products
        all_products = list(products_db.values())
        
        # Apply curation rules
        curated_products = curation_engine.apply_curation_rules(
            all_products, 
            curation_rules.get('rules', [])
        )
        
        # Update products in database
        curated_count = 0
        for product in curated_products:
            if product.get('is_curated', False):
                products_db[product['id']] = product
                curated_count += 1
        
        return {
            "message": f"Curation completed",
            "total_products": len(all_products),
            "curated_products": curated_count,
            "curation_rate": (curated_count / len(all_products) * 100) if all_products else 0,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error curating products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/curated-products")
async def get_curated_products(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(verify_token)
):
    """Get curated products"""
    try:
        curated_products = [
            p for p in products_db.values() 
            if p.get('is_curated', False)
        ]
        
        # Sort by curation score
        curated_products.sort(
            key=lambda x: x.get('curation_score', 0), 
            reverse=True
        )
        
        # Apply pagination
        paginated_products = curated_products[offset:offset + limit]
        
        return {
            "products": paginated_products,
            "total": len(curated_products),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting curated products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/deduplicate-products")
async def deduplicate_products(current_user: dict = Depends(verify_token)):
    """Find and merge duplicate products"""
    try:
        from src.processing.normalizer import ProductDeduplicator
        
        deduplicator = ProductDeduplicator()
        
        # Get all products
        all_products = list(products_db.values())
        
        # Find duplicates
        duplicate_groups = deduplicator.find_duplicates(all_products)
        
        # Merge duplicates
        merged_count = 0
        for duplicate_group in duplicate_groups:
            merged_product = deduplicator.merge_duplicates(duplicate_group)
            
            # Keep the merged product and remove duplicates
            merged_product['id'] = duplicate_group[0]['id']  # Keep first product's ID
            products_db[merged_product['id']] = merged_product
            
            # Remove duplicate products
            for duplicate in duplicate_group[1:]:
                if duplicate['id'] in products_db:
                    del products_db[duplicate['id']]
            
            merged_count += len(duplicate_group) - 1
        
        return {
            "message": "Deduplication completed",
            "duplicate_groups_found": len(duplicate_groups),
            "products_merged": merged_count,
            "total_products_after": len(products_db),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error deduplicating products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/marketplace-analytics")
async def get_marketplace_analytics(current_user: dict = Depends(verify_token)):
    """Get comprehensive marketplace analytics"""
    try:
        all_products = list(products_db.values())
        
        # Retailer distribution
        retailer_counts = {}
        retailer_avg_prices = {}
        retailer_avg_ratings = {}
        
        for product in all_products:
            retailer = product.get('retailer', 'unknown')
            retailer_counts[retailer] = retailer_counts.get(retailer, 0) + 1
            
            # Calculate average prices
            if product.get('current_price'):
                if retailer not in retailer_avg_prices:
                    retailer_avg_prices[retailer] = []
                retailer_avg_prices[retailer].append(product['current_price'])
            
            # Calculate average ratings
            if product.get('rating'):
                if retailer not in retailer_avg_ratings:
                    retailer_avg_ratings[retailer] = []
                retailer_avg_ratings[retailer].append(product['rating'])
        
        # Calculate averages
        for retailer in retailer_avg_prices:
            retailer_avg_prices[retailer] = sum(retailer_avg_prices[retailer]) / len(retailer_avg_prices[retailer])
        
        for retailer in retailer_avg_ratings:
            retailer_avg_ratings[retailer] = sum(retailer_avg_ratings[retailer]) / len(retailer_avg_ratings[retailer])
        
        # Price distribution
        prices = [p.get('current_price') for p in all_products if p.get('current_price')]
        price_ranges = {
            'under_25': len([p for p in prices if p < 25]),
            '25_50': len([p for p in prices if 25 <= p < 50]),
            '50_100': len([p for p in prices if 50 <= p < 100]),
            '100_500': len([p for p in prices if 100 <= p < 500]),
            'over_500': len([p for p in prices if p >= 500])
        }
        
        # Quality distribution
        quality_scores = [p.get('data_quality_score', 0) for p in all_products]
        quality_distribution = {
            'excellent': len([s for s in quality_scores if s >= 0.9]),
            'good': len([s for s in quality_scores if 0.7 <= s < 0.9]),
            'fair': len([s for s in quality_scores if 0.5 <= s < 0.7]),
            'poor': len([s for s in quality_scores if s < 0.5])
        }
        
        # Availability distribution
        availability_counts = {}
        for product in all_products:
            availability = product.get('availability', 'unknown')
            availability_counts[availability] = availability_counts.get(availability, 0) + 1
        
        return {
            "total_products": len(all_products),
            "retailer_distribution": retailer_counts,
            "retailer_avg_prices": retailer_avg_prices,
            "retailer_avg_ratings": retailer_avg_ratings,
            "price_distribution": price_ranges,
            "quality_distribution": quality_distribution,
            "availability_distribution": availability_counts,
            "avg_data_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "curated_products": len([p for p in all_products if p.get('is_curated', False)])
        }
        
    except Exception as e:
        logger.error(f"Error getting marketplace analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Users endpoint (for admin functionality)
@app.get("/api/users")
async def get_users(current_user: dict = Depends(verify_token)):
    """Get all users (admin only)"""
    try:
        # For now, return a simple list of users
        # In production, this would query the database
        users = [
            {
                "id": "demo_user",
                "email": "demo@example.com",
                "role": "admin",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        return {"users": users, "total": len(users)}
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))