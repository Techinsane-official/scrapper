from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AvailabilityStatus(str, Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    PRE_ORDER = "pre_order"
    LIMITED_STOCK = "limited_stock"
    UNKNOWN = "unknown"

class ScrapingStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProductVariation(BaseModel):
    """Product variation (size, color, style, etc.)"""
    variation_type: str  # "size", "color", "style", etc.
    variation_value: str  # "Large", "Red", "Classic", etc.
    price: Optional[float] = None
    availability: Optional[AvailabilityStatus] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None

class ProductDimensions(BaseModel):
    """Product dimensions"""
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    unit: str = "inches"  # "inches", "cm", "lbs", "kg"

class ReviewDistribution(BaseModel):
    """Review rating distribution"""
    five_star: int = 0
    four_star: int = 0
    three_star: int = 0
    two_star: int = 0
    one_star: int = 0

class ProductData(BaseModel):
    """Comprehensive product data model"""
    
    # Core Information
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    bullet_points: Optional[List[str]] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    
    # Pricing & Availability
    current_price: Optional[float] = Field(None, ge=0)
    original_price: Optional[float] = Field(None, ge=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    availability: AvailabilityStatus = AvailabilityStatus.UNKNOWN
    stock_quantity: Optional[int] = Field(None, ge=0)
    shipping_info: Optional[str] = None
    
    # Media & Visuals
    primary_image_url: Optional[str] = None
    additional_images: List[str] = Field(default_factory=list)
    video_urls: List[str] = Field(default_factory=list)
    
    # Specifications & Features
    specifications: Dict[str, str] = Field(default_factory=dict)
    dimensions: Optional[ProductDimensions] = None
    materials: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    compatibility: List[str] = Field(default_factory=list)
    
    # Variations & Options
    variations: List[ProductVariation] = Field(default_factory=list)
    
    # Social Proof & Reviews
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    review_distribution: Optional[ReviewDistribution] = None
    best_seller_rank: Optional[int] = Field(None, ge=1)
    
    # Metadata
    source_url: str = Field(..., min_length=1)
    retailer: str = Field(..., min_length=1)
    last_updated: datetime = Field(default_factory=datetime.now)
    data_quality_score: float = Field(default=0.0, ge=0, le=1)
    scraping_status: ScrapingStatus = ScrapingStatus.PENDING
    
    # Curation & Business Logic
    is_curated: bool = False
    curation_score: Optional[float] = Field(None, ge=0, le=1)
    curation_reason: Optional[str] = None
    
    # Additional metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScrapingJobCreate(BaseModel):
    """Enhanced job creation model"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    retailer: str = Field(..., min_length=1)
    job_type: str = Field(..., min_length=1)  # "catalog", "price_update", "search", "product"
    
    # Job-specific configuration
    configuration: Dict[str, Any] = Field(default_factory=dict)
    
    # For catalog scraping
    category_url: Optional[str] = None
    max_pages: int = Field(default=1, ge=1, le=100)
    
    # For search-based scraping
    search_query: Optional[str] = None
    search_filters: Optional[Dict[str, Any]] = None
    
    # For individual product scraping
    product_urls: Optional[List[str]] = None
    
    # Scheduling
    schedule_type: str = Field(default="manual")  # "manual", "hourly", "daily", "weekly"
    priority: int = Field(default=1, ge=1, le=10)

class ScrapingJob(BaseModel):
    """Enhanced job model"""
    id: str
    name: str
    description: Optional[str] = None
    retailer: str
    job_type: str
    status: ScrapingStatus
    configuration: Dict[str, Any] = Field(default_factory=dict)
    
    # Results
    products_found: int = 0
    products_processed: int = 0
    products_successful: int = 0
    products_failed: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PriceUpdate(BaseModel):
    """Price update model for real-time sync"""
    product_id: str
    old_price: Optional[float] = None
    new_price: float
    old_availability: Optional[AvailabilityStatus] = None
    new_availability: AvailabilityStatus
    change_percentage: Optional[float] = None
    detected_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CurationRule(BaseModel):
    """Product curation rule"""
    name: str
    description: str
    conditions: Dict[str, Any]  # Conditions to check
    action: str  # "include", "exclude", "flag"
    priority: int = Field(default=1, ge=1, le=10)
    is_active: bool = True
    
    # Examples:
    # conditions: {"min_rating": 4.0, "min_reviews": 10, "availability": "in_stock"}
    # action: "include"

class MarketplaceStats(BaseModel):
    """Marketplace statistics"""
    total_products: int = 0
    curated_products: int = 0
    active_retailers: int = 0
    total_jobs: int = 0
    running_jobs: int = 0
    completed_jobs_today: int = 0
    failed_jobs_today: int = 0
    products_updated_today: int = 0
    average_data_quality: float = 0.0
    price_changes_today: int = 0
    
    # Performance metrics
    avg_scraping_speed: float = 0.0  # products per minute
    success_rate: float = 0.0  # percentage
    uptime_percentage: float = 0.0
    
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
