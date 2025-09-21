"""
Scraping jobs routes.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel
from loguru import logger

from ...database.models import ScrapingJob, ScrapingStatus, User
from ...database.service import db_service
from ..auth import get_current_active_user
from ...scraper.amazon import PremiumAmazonScraper

router = APIRouter()


class CreateJobRequest(BaseModel):
    """Create job request model."""
    name: str
    description: Optional[str] = None
    retailer: str
    category: Optional[str] = None
    search_query: Optional[str] = None
    max_pages: int = 5


class JobResponse(BaseModel):
    """Job response model."""
    id: str
    name: str
    description: Optional[str]
    retailer: str
    category: Optional[str]
    search_query: Optional[str]
    max_pages: int
    status: ScrapingStatus
    progress: int
    products_scraped: int
    products_found: int
    error_message: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: Optional[str]


class JobUpdateRequest(BaseModel):
    """Job update request model."""
    name: Optional[str] = None
    description: Optional[str] = None
    max_pages: Optional[int] = None


async def run_scraping_job(job_id: str):
    """Background task to run scraping job."""
    try:
        logger.info(f"Starting scraping job {job_id}")
        
        # Update job status to running
        await db_service.update_scraping_job(job_id, {
            "status": ScrapingStatus.RUNNING,
            "started_at": "now()"
        })
        
        # Get job details
        job = await db_service.get_scraping_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        # Initialize scraper based on retailer
        scraper = None
        if job.retailer.lower() == "amazon":
            scraper = PremiumAmazonScraper()
        else:
            raise ValueError(f"Unsupported retailer: {job.retailer}")
        
        # Run scraping based on job type
        if job.category:
            results = await scraper.scrape_category(job.category, job.max_pages)
        elif job.search_query:
            results = await scraper.scrape_search_results(
                f"{scraper.base_url}/s?k={job.search_query}", 
                job.max_pages
            )
        else:
            raise ValueError("Either category or search_query must be provided")
        
        # Process results
        products_scraped = 0
        products_found = len(results)
        
        for result in results:
            if result.success and result.data:
                try:
                    from ...database.models import Product
                    product = Product(
                        job_id=job_id,
                        retailer=job.retailer,
                        **result.data
                    )
                    await db_service.create_product(product)
                    products_scraped += 1
                except Exception as e:
                    logger.error(f"Error saving product: {e}")
        
        # Update job completion
        await db_service.update_scraping_job(job_id, {
            "status": ScrapingStatus.COMPLETED,
            "progress": 100,
            "products_scraped": products_scraped,
            "products_found": products_found,
            "completed_at": "now()"
        })
        
        logger.info(f"Completed scraping job {job_id}: {products_scraped}/{products_found} products")
        
    except Exception as e:
        logger.error(f"Scraping job {job_id} failed: {e}")
        await db_service.update_scraping_job(job_id, {
            "status": ScrapingStatus.FAILED,
            "error_message": str(e),
            "completed_at": "now()"
        })


@router.post("/", response_model=JobResponse)
async def create_job(
    request: CreateJobRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new scraping job."""
    try:
        # Validate retailer
        if request.retailer.lower() not in ["amazon"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported retailer"
            )
        
        # Create job
        job = ScrapingJob(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            retailer=request.retailer.lower(),
            category=request.category,
            search_query=request.search_query,
            max_pages=request.max_pages,
            status=ScrapingStatus.PENDING
        )
        
        created_job = await db_service.create_scraping_job(job)
        
        # Start background scraping task
        background_tasks.add_task(run_scraping_job, created_job.id)
        
        logger.info(f"Created scraping job {created_job.id} for user {current_user.email}")
        
        return JobResponse(
            id=created_job.id,
            name=created_job.name,
            description=created_job.description,
            retailer=created_job.retailer,
            category=created_job.category,
            search_query=created_job.search_query,
            max_pages=created_job.max_pages,
            status=created_job.status,
            progress=created_job.progress,
            products_scraped=created_job.products_scraped,
            products_found=created_job.products_found,
            error_message=created_job.error_message,
            started_at=created_job.started_at.isoformat() if created_job.started_at else None,
            completed_at=created_job.completed_at.isoformat() if created_job.completed_at else None,
            created_at=created_job.created_at.isoformat() if created_job.created_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=List[JobResponse])
async def get_user_jobs(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
):
    """Get user's scraping jobs."""
    try:
        jobs = await db_service.get_user_jobs(current_user.id, limit)
        
        return [
            JobResponse(
                id=job.id,
                name=job.name,
                description=job.description,
                retailer=job.retailer,
                category=job.category,
                search_query=job.search_query,
                max_pages=job.max_pages,
                status=job.status,
                progress=job.progress,
                products_scraped=job.products_scraped,
                products_found=job.products_found,
                error_message=job.error_message,
                started_at=job.started_at.isoformat() if job.started_at else None,
                completed_at=job.completed_at.isoformat() if job.completed_at else None,
                created_at=job.created_at.isoformat() if job.created_at else None
            )
            for job in jobs
        ]
        
    except Exception as e:
        logger.error(f"Error getting user jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get specific scraping job."""
    try:
        job = await db_service.get_scraping_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check if user owns the job
        if job.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return JobResponse(
            id=job.id,
            name=job.name,
            description=job.description,
            retailer=job.retailer,
            category=job.category,
            search_query=job.search_query,
            max_pages=job.max_pages,
            status=job.status,
            progress=job.progress,
            products_scraped=job.products_scraped,
            products_found=job.products_found,
            error_message=job.error_message,
            started_at=job.started_at.isoformat() if job.started_at else None,
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            created_at=job.created_at.isoformat() if job.created_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    request: JobUpdateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Update scraping job."""
    try:
        job = await db_service.get_scraping_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check if user owns the job
        if job.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if job can be updated
        if job.status in [ScrapingStatus.RUNNING, ScrapingStatus.COMPLETED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update running or completed job"
            )
        
        # Prepare updates
        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description
        if request.max_pages is not None:
            updates["max_pages"] = request.max_pages
        
        updated_job = await db_service.update_scraping_job(job_id, updates)
        
        return JobResponse(
            id=updated_job.id,
            name=updated_job.name,
            description=updated_job.description,
            retailer=updated_job.retailer,
            category=updated_job.category,
            search_query=updated_job.search_query,
            max_pages=updated_job.max_pages,
            status=updated_job.status,
            progress=updated_job.progress,
            products_scraped=updated_job.products_scraped,
            products_found=updated_job.products_found,
            error_message=updated_job.error_message,
            started_at=updated_job.started_at.isoformat() if updated_job.started_at else None,
            completed_at=updated_job.completed_at.isoformat() if updated_job.completed_at else None,
            created_at=updated_job.created_at.isoformat() if updated_job.created_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete scraping job."""
    try:
        job = await db_service.get_scraping_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check if user owns the job
        if job.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if job can be deleted
        if job.status == ScrapingStatus.RUNNING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete running job"
            )
        
        success = await db_service.delete_scraping_job(job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete job"
            )
        
        return {"message": "Job deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
