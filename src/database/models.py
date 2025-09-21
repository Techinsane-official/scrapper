"""
Database models for the scraper application.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ScrapingStatus(str, Enum):
    """Scraping job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    """User roles."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class User(BaseModel):
    """User model."""
    id: Optional[str] = None
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")
    role: UserRole = Field(UserRole.USER, description="User role")
    is_active: bool = Field(True, description="Whether user is active")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class ScrapingJob(BaseModel):
    """Scraping job model."""
    id: Optional[str] = None
    user_id: str = Field(..., description="User who created the job")
    name: str = Field(..., description="Job name")
    description: Optional[str] = Field(None, description="Job description")
    retailer: str = Field(..., description="Target retailer (amazon, walmart, etc.)")
    category: Optional[str] = Field(None, description="Product category")
    search_query: Optional[str] = Field(None, description="Search query")
    max_pages: int = Field(5, description="Maximum pages to scrape")
    status: ScrapingStatus = Field(ScrapingStatus.PENDING, description="Job status")
    progress: int = Field(0, description="Progress percentage (0-100)")
    products_scraped: int = Field(0, description="Number of products scraped")
    products_found: int = Field(0, description="Number of products found")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Product(BaseModel):
    """Product model."""
    id: Optional[str] = None
    job_id: str = Field(..., description="Associated scraping job ID")
    retailer: str = Field(..., description="Retailer name")
    external_id: str = Field(..., description="External product ID (ASIN, SKU, etc.)")
    url: str = Field(..., description="Product URL")
    title: str = Field(..., description="Product title")
    price: Optional[float] = Field(None, description="Current price")
    original_price: Optional[float] = Field(None, description="Original/MSRP price")
    discount_percentage: Optional[float] = Field(None, description="Discount percentage")
    rating: Optional[float] = Field(None, description="Customer rating")
    review_count: Optional[int] = Field(None, description="Number of reviews")
    availability: str = Field("unknown", description="Availability status")
    brand: Optional[str] = Field(None, description="Product brand")
    category: Optional[str] = Field(None, description="Product category")
    description: Optional[str] = Field(None, description="Product description")
    bullet_points: List[str] = Field(default_factory=list, description="Product bullet points")
    specifications: Dict[str, str] = Field(default_factory=dict, description="Product specifications")
    variations: List[Dict[str, Any]] = Field(default_factory=list, description="Product variations")
    images: List[str] = Field(default_factory=list, description="Product image URLs")
    scraped_at: datetime = Field(default_factory=datetime.now, description="When product was scraped")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ScrapingStats(BaseModel):
    """Scraping statistics model."""
    id: Optional[str] = None
    job_id: str = Field(..., description="Associated scraping job ID")
    total_requests: int = Field(0, description="Total HTTP requests made")
    successful_requests: int = Field(0, description="Successful HTTP requests")
    failed_requests: int = Field(0, description="Failed HTTP requests")
    products_scraped: int = Field(0, description="Products successfully scraped")
    products_failed: int = Field(0, description="Products that failed to scrape")
    average_response_time: float = Field(0.0, description="Average response time in seconds")
    total_duration: float = Field(0.0, description="Total scraping duration in seconds")
    memory_usage: float = Field(0.0, description="Peak memory usage in MB")
    cpu_usage: float = Field(0.0, description="Peak CPU usage percentage")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SystemLog(BaseModel):
    """System log model."""
    id: Optional[str] = None
    level: str = Field(..., description="Log level (INFO, WARNING, ERROR, DEBUG)")
    message: str = Field(..., description="Log message")
    component: str = Field(..., description="Component that generated the log")
    job_id: Optional[str] = Field(None, description="Associated job ID if applicable")
    user_id: Optional[str] = Field(None, description="Associated user ID if applicable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: Optional[datetime] = None


class Notification(BaseModel):
    """Notification model."""
    id: Optional[str] = None
    user_id: str = Field(..., description="Target user ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    type: str = Field("info", description="Notification type (info, success, warning, error)")
    is_read: bool = Field(False, description="Whether notification has been read")
    job_id: Optional[str] = Field(None, description="Associated job ID if applicable")
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None


class DashboardStats(BaseModel):
    """Dashboard statistics model."""
    total_jobs: int = Field(0, description="Total number of scraping jobs")
    active_jobs: int = Field(0, description="Number of active jobs")
    completed_jobs: int = Field(0, description="Number of completed jobs")
    failed_jobs: int = Field(0, description="Number of failed jobs")
    total_products: int = Field(0, description="Total products scraped")
    total_users: int = Field(0, description="Total number of users")
    average_job_duration: float = Field(0.0, description="Average job duration in minutes")
    success_rate: float = Field(0.0, description="Success rate percentage")
    last_updated: Optional[datetime] = None
