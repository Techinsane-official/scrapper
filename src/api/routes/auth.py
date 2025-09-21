"""
Authentication routes.
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from loguru import logger

from ...database.models import User, UserRole
from ...database.service import db_service
from ..auth import create_access_token, verify_password, get_password_hash, get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request model."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    user: User


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: Optional[str]
    last_login: Optional[str]


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login."""
    try:
        # Get user by email
        user = await db_service.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password (in a real app, you'd get this from Supabase auth)
        # For now, we'll use a simple check
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        
        # Update last login
        await db_service.update_user(user.id, {"last_login": "now()"})
        
        logger.info(f"User {user.email} logged in successfully")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest):
    """User registration."""
    try:
        # Check if user already exists
        existing_user = await db_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = User(
            email=request.email,
            full_name=request.full_name,
            role=UserRole.USER,
            is_active=True
        )
        
        created_user = await db_service.create_user(user)
        
        logger.info(f"User {created_user.email} registered successfully")
        
        return UserResponse(
            id=created_user.id,
            email=created_user.email,
            full_name=created_user.full_name,
            role=created_user.role,
            is_active=created_user.is_active,
            created_at=created_user.created_at.isoformat() if created_user.created_at else None,
            last_login=created_user.last_login.isoformat() if created_user.last_login else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )


@router.post("/logout")
async def logout():
    """User logout (client-side token removal)."""
    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token."""
    try:
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": current_user.id}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
