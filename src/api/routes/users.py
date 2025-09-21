"""
Users management routes.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from loguru import logger

from ...database.models import User, UserRole
from ...database.service import db_service
from ..auth import get_current_admin_user

router = APIRouter()


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: str
    updated_at: str
    last_login: str


class UserUpdateRequest(BaseModel):
    """User update request model."""
    full_name: str = None
    role: UserRole = None
    is_active: bool = None


@router.get("/", response_model=List[UserResponse])
async def get_all_users(current_user: User = Depends(get_current_admin_user)):
    """Get all users (admin only)."""
    try:
        result = db_service.client.table('users').select('*').execute()
        users = [User(**user_data) for user_data in result.data]
        
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name or "",
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else "",
                updated_at=user.updated_at.isoformat() if user.updated_at else "",
                last_login=user.last_login.isoformat() if user.last_login else ""
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_admin_user)
):
    """Update user (admin only)."""
    try:
        # Prepare updates
        updates = {}
        if request.full_name is not None:
            updates["full_name"] = request.full_name
        if request.role is not None:
            updates["role"] = request.role
        if request.is_active is not None:
            updates["is_active"] = request.is_active
        
        updated_user = await db_service.update_user(user_id, updates)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            full_name=updated_user.full_name or "",
            role=updated_user.role,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at.isoformat() if updated_user.created_at else "",
            updated_at=updated_user.updated_at.isoformat() if updated_user.updated_at else "",
            last_login=updated_user.last_login.isoformat() if updated_user.last_login else ""
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Delete user (admin only)."""
    try:
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        result = db_service.client.table('users').delete().eq('id', user_id).execute()
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
