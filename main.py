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

# In-memory storage (replace with database in production)
jobs_db = {}
products_db = {}
users_db = {}

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

# Scraping functions
async def scrape_amazon_product(url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Scrape Amazon product data"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract product data
            product_data = {
                'title': '',
                'price': '',
                'rating': '',
                'reviews_count': '',
                'image_url': '',
                'url': url
            }
            
            # Title
            title_selectors = [
                '#productTitle',
                'h1.a-size-large',
                '.a-size-large.product-title-word-break'
            ]
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    product_data['title'] = title_elem.get_text().strip()
                    break
            
            # Price
            price_selectors = [
                '.a-price-whole',
                '.a-price .a-offscreen',
                '#priceblock_dealprice',
                '#priceblock_ourprice'
            ]
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    product_data['price'] = price_elem.get_text().strip()
                    break
            
            # Rating
            rating_elem = soup.select_one('.a-icon-alt')
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    product_data['rating'] = rating_match.group(1)
            
            # Reviews count
            reviews_elem = soup.select_one('#acrCustomerReviewText')
            if reviews_elem:
                reviews_text = reviews_elem.get_text()
                reviews_match = re.search(r'(\d+)', reviews_text.replace(',', ''))
                if reviews_match:
                    product_data['reviews_count'] = reviews_match.group(1)
            
            # Image
            img_elem = soup.select_one('#landingImage')
            if img_elem:
                product_data['image_url'] = img_elem.get('src')
            
            return product_data
            
    except Exception as e:
        logger.error(f"Error scraping Amazon product: {e}")
        raise e

async def execute_scraping_job(job_id: str, job_data: ScrapingJobCreate):
    """Execute a scraping job in the background"""
    try:
        jobs_db[job_id]['status'] = 'running'
        logger.info(f"Starting job {job_id}")
        
        products = []
        async with aiohttp.ClientSession() as session:
            if job_data.job_type == "amazon_product":
                product_data = await scrape_amazon_product(job_data.url, session)
                product_data['id'] = str(uuid.uuid4())
                product_data['job_id'] = job_id
                product_data['scraped_at'] = datetime.now()
                
                products.append(product_data)
                products_db[product_data['id']] = product_data
        
        jobs_db[job_id]['status'] = 'completed'
        jobs_db[job_id]['completed_at'] = datetime.now()
        jobs_db[job_id]['products_count'] = len(products)
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['error'] = str(e)
        logger.error(f"Job {job_id} failed: {e}")

# API Routes
@app.get("/")
async def root():
    return {"message": "Premium Scraper API is running!", "status": "success", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is working", "timestamp": datetime.now()}

@app.post("/api/auth/register")
async def register(user: UserCreate):
    """Register a new user"""
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_id = str(uuid.uuid4())
    users_db[user.email] = {
        "id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": datetime.now()
    }
    
    return {"message": "User created successfully", "user_id": user_id}

@app.post("/api/auth/login")
async def login(user: UserLogin):
    """Login user"""
    if user.email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Simple authentication (replace with proper password hashing)
    return {
        "access_token": "demo_token",
        "token_type": "bearer",
        "user": {
            "id": users_db[user.email]["id"],
            "email": user.email,
            "full_name": users_db[user.email]["full_name"]
        }
    }

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
    jobs = list(jobs_db.values())
    return {"jobs": jobs, "total": len(jobs)}

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
    """Get dashboard statistics"""
    total_jobs = len(jobs_db)
    completed_jobs = len([j for j in jobs_db.values() if j['status'] == 'completed'])
    running_jobs = len([j for j in jobs_db.values() if j['status'] == 'running'])
    total_products = len(products_db)
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "running_jobs": running_jobs,
        "total_products": total_products,
        "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))