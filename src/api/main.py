"""
FastAPI main application with Supabase integration.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

from .auth import get_current_user, create_access_token, verify_token
from .routes import auth, jobs, products, dashboard, users
from ..config.supabase import supabase_config
from ..database.service import db_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting Premium Scraper API...")
    
    # Check Supabase connection
    if not supabase_config.is_configured():
        logger.warning("Supabase not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY")
    else:
        logger.info("Supabase connection configured")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Premium Scraper API...")


# Create FastAPI app
app = FastAPI(
    title="Premium E-commerce Scraper API",
    description="Professional e-commerce product scraping service with Supabase integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Scraping Jobs"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Premium E-commerce Scraper API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test Supabase connection
        if supabase_config.is_configured():
            supabase_config.client.table('users').select('id').limit(1).execute()
            db_status = "connected"
        else:
            db_status = "not_configured"
        
        return {
            "status": "healthy",
            "database": db_status,
            "timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
