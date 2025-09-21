"""
Products routes.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from loguru import logger

from ...database.models import Product, User
from ...database.service import db_service
from ..auth import get_current_active_user

router = APIRouter()


class ProductResponse(BaseModel):
    """Product response model."""
    id: str
    job_id: str
    retailer: str
    external_id: str
    url: str
    title: str
    price: Optional[float]
    original_price: Optional[float]
    discount_percentage: Optional[float]
    rating: Optional[float]
    review_count: Optional[int]
    availability: str
    brand: Optional[str]
    category: Optional[str]
    description: Optional[str]
    bullet_points: List[str]
    specifications: dict
    variations: List[dict]
    images: List[str]
    scraped_at: str
    created_at: Optional[str]


class ProductSearchRequest(BaseModel):
    """Product search request model."""
    query: str
    limit: int = 50


@router.get("/job/{job_id}", response_model=List[ProductResponse])
async def get_job_products(
    job_id: str,
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Get products for a specific job."""
    try:
        # Verify job ownership
        job = await db_service.get_scraping_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        if job.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        products = await db_service.get_job_products(job_id, limit)
        
        return [
            ProductResponse(
                id=product.id,
                job_id=product.job_id,
                retailer=product.retailer,
                external_id=product.external_id,
                url=product.url,
                title=product.title,
                price=product.price,
                original_price=product.original_price,
                discount_percentage=product.discount_percentage,
                rating=product.rating,
                review_count=product.review_count,
                availability=product.availability,
                brand=product.brand,
                category=product.category,
                description=product.description,
                bullet_points=product.bullet_points,
                specifications=product.specifications,
                variations=product.variations,
                images=product.images,
                scraped_at=product.scraped_at.isoformat(),
                created_at=product.created_at.isoformat() if product.created_at else None
            )
            for product in products
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting products for job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    query: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Search products by title or description."""
    try:
        products = await db_service.search_products(query, limit)
        
        return [
            ProductResponse(
                id=product.id,
                job_id=product.job_id,
                retailer=product.retailer,
                external_id=product.external_id,
                url=product.url,
                title=product.title,
                price=product.price,
                original_price=product.original_price,
                discount_percentage=product.discount_percentage,
                rating=product.rating,
                review_count=product.review_count,
                availability=product.availability,
                brand=product.brand,
                category=product.category,
                description=product.description,
                bullet_points=product.bullet_points,
                specifications=product.specifications,
                variations=product.variations,
                images=product.images,
                scraped_at=product.scraped_at.isoformat(),
                created_at=product.created_at.isoformat() if product.created_at else None
            )
            for product in products
        ]
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get specific product."""
    try:
        # Get product
        result = db_service.client.table('products').select('*').eq('id', product_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product_data = result.data[0]
        product = Product(**product_data)
        
        # Verify access through job ownership
        job = await db_service.get_scraping_job(product.job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated job not found"
            )
        
        if job.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return ProductResponse(
            id=product.id,
            job_id=product.job_id,
            retailer=product.retailer,
            external_id=product.external_id,
            url=product.url,
            title=product.title,
            price=product.price,
            original_price=product.original_price,
            discount_percentage=product.discount_percentage,
            rating=product.rating,
            review_count=product.review_count,
            availability=product.availability,
            brand=product.brand,
            category=product.category,
            description=product.description,
            bullet_points=product.bullet_points,
            specifications=product.specifications,
            variations=product.variations,
            images=product.images,
            scraped_at=product.scraped_at.isoformat(),
            created_at=product.created_at.isoformat() if product.created_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
