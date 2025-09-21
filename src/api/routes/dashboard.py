"""
Dashboard routes.
"""

from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from loguru import logger

from ...database.models import DashboardStats, SystemLog, Notification, User
from ...database.service import db_service
from ..auth import get_current_active_user

router = APIRouter()


class DashboardResponse(BaseModel):
    """Dashboard response model."""
    stats: DashboardStats
    recent_logs: List[dict]
    notifications: List[dict]


@router.get("/", response_model=DashboardResponse)
async def get_dashboard_data(current_user: User = Depends(get_current_active_user)):
    """Get dashboard data."""
    try:
        # Get dashboard statistics
        stats = await db_service.get_dashboard_stats()
        
        # Get recent system logs
        recent_logs = await db_service.get_recent_logs(limit=20)
        logs_data = [
            {
                "id": log.id,
                "level": log.level,
                "message": log.message,
                "component": log.component,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in recent_logs
        ]
        
        # Get user notifications
        notifications = await db_service.get_user_notifications(current_user.id, unread_only=True)
        notifications_data = [
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "created_at": notification.created_at.isoformat() if notification.created_at else None
            }
            for notification in notifications
        ]
        
        return DashboardResponse(
            stats=stats,
            recent_logs=logs_data,
            notifications=notifications_data
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user)):
    """Get dashboard statistics."""
    try:
        stats = await db_service.get_dashboard_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
