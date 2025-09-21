"""
Database service layer for Supabase operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from .models import (
    User, ScrapingJob, Product, ScrapingStats, SystemLog, 
    Notification, DashboardStats, ScrapingStatus, UserRole
)
from ..config.supabase import get_supabase_client, get_supabase_admin


class DatabaseService:
    """Database service for Supabase operations."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.admin_client = get_supabase_admin()
    
    # User operations
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        try:
            user_data = user.dict(exclude={'id', 'created_at', 'updated_at'})
            result = self.admin_client.table('users').insert(user_data).execute()
            if result.data:
                return User(**result.data[0])
            raise Exception("Failed to create user")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            result = self.client.table('users').select('*').eq('id', user_id).execute()
            if result.data:
                return User(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            result = self.client.table('users').select('*').eq('email', email).execute()
            if result.data:
                return User(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update user."""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            result = self.client.table('users').update(updates).eq('id', user_id).execute()
            if result.data:
                return User(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    # Scraping job operations
    async def create_scraping_job(self, job: ScrapingJob) -> ScrapingJob:
        """Create a new scraping job."""
        try:
            job_data = job.dict(exclude={'id', 'created_at', 'updated_at'})
            result = self.client.table('scraping_jobs').insert(job_data).execute()
            if result.data:
                return ScrapingJob(**result.data[0])
            raise Exception("Failed to create scraping job")
        except Exception as e:
            logger.error(f"Error creating scraping job: {e}")
            raise
    
    async def get_scraping_job(self, job_id: str) -> Optional[ScrapingJob]:
        """Get scraping job by ID."""
        try:
            result = self.client.table('scraping_jobs').select('*').eq('id', job_id).execute()
            if result.data:
                return ScrapingJob(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting scraping job {job_id}: {e}")
            return None
    
    async def get_user_jobs(self, user_id: str, limit: int = 50) -> List[ScrapingJob]:
        """Get user's scraping jobs."""
        try:
            result = self.client.table('scraping_jobs').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            return [ScrapingJob(**job) for job in result.data]
        except Exception as e:
            logger.error(f"Error getting user jobs for {user_id}: {e}")
            return []
    
    async def update_scraping_job(self, job_id: str, updates: Dict[str, Any]) -> Optional[ScrapingJob]:
        """Update scraping job."""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            result = self.client.table('scraping_jobs').update(updates).eq('id', job_id).execute()
            if result.data:
                return ScrapingJob(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating scraping job {job_id}: {e}")
            return None
    
    async def delete_scraping_job(self, job_id: str) -> bool:
        """Delete scraping job."""
        try:
            result = self.client.table('scraping_jobs').delete().eq('id', job_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting scraping job {job_id}: {e}")
            return False
    
    # Product operations
    async def create_product(self, product: Product) -> Product:
        """Create a new product."""
        try:
            product_data = product.dict(exclude={'id', 'created_at', 'updated_at'})
            result = self.client.table('products').insert(product_data).execute()
            if result.data:
                return Product(**result.data[0])
            raise Exception("Failed to create product")
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise
    
    async def create_products_batch(self, products: List[Product]) -> List[Product]:
        """Create multiple products in batch."""
        try:
            products_data = [product.dict(exclude={'id', 'created_at', 'updated_at'}) for product in products]
            result = self.client.table('products').insert(products_data).execute()
            return [Product(**product) for product in result.data]
        except Exception as e:
            logger.error(f"Error creating products batch: {e}")
            raise
    
    async def get_job_products(self, job_id: str, limit: int = 100) -> List[Product]:
        """Get products for a specific job."""
        try:
            result = self.client.table('products').select('*').eq('job_id', job_id).order('scraped_at', desc=True).limit(limit).execute()
            return [Product(**product) for product in result.data]
        except Exception as e:
            logger.error(f"Error getting products for job {job_id}: {e}")
            return []
    
    async def search_products(self, query: str, limit: int = 50) -> List[Product]:
        """Search products by title or description."""
        try:
            result = self.client.table('products').select('*').or_(f'title.ilike.%{query}%,description.ilike.%{query}%').limit(limit).execute()
            return [Product(**product) for product in result.data]
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    # Statistics operations
    async def create_scraping_stats(self, stats: ScrapingStats) -> ScrapingStats:
        """Create scraping statistics."""
        try:
            stats_data = stats.dict(exclude={'id', 'created_at', 'updated_at'})
            result = self.client.table('scraping_stats').insert(stats_data).execute()
            if result.data:
                return ScrapingStats(**result.data[0])
            raise Exception("Failed to create scraping stats")
        except Exception as e:
            logger.error(f"Error creating scraping stats: {e}")
            raise
    
    async def get_job_stats(self, job_id: str) -> Optional[ScrapingStats]:
        """Get statistics for a specific job."""
        try:
            result = self.client.table('scraping_stats').select('*').eq('job_id', job_id).execute()
            if result.data:
                return ScrapingStats(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting stats for job {job_id}: {e}")
            return None
    
    # Logging operations
    async def create_log(self, log: SystemLog) -> SystemLog:
        """Create a system log entry."""
        try:
            log_data = log.dict(exclude={'id', 'created_at'})
            result = self.client.table('system_logs').insert(log_data).execute()
            if result.data:
                return SystemLog(**result.data[0])
            raise Exception("Failed to create log")
        except Exception as e:
            logger.error(f"Error creating log: {e}")
            raise
    
    async def get_recent_logs(self, limit: int = 100) -> List[SystemLog]:
        """Get recent system logs."""
        try:
            result = self.client.table('system_logs').select('*').order('created_at', desc=True).limit(limit).execute()
            return [SystemLog(**log) for log in result.data]
        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
            return []
    
    # Notification operations
    async def create_notification(self, notification: Notification) -> Notification:
        """Create a notification."""
        try:
            notification_data = notification.dict(exclude={'id', 'created_at', 'read_at'})
            result = self.client.table('notifications').insert(notification_data).execute()
            if result.data:
                return Notification(**result.data[0])
            raise Exception("Failed to create notification")
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise
    
    async def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        """Get user notifications."""
        try:
            query = self.client.table('notifications').select('*').eq('user_id', user_id)
            if unread_only:
                query = query.eq('is_read', False)
            result = query.order('created_at', desc=True).execute()
            return [Notification(**notification) for notification in result.data]
        except Exception as e:
            logger.error(f"Error getting notifications for user {user_id}: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str) -> bool:
        """Mark notification as read."""
        try:
            result = self.client.table('notifications').update({'is_read': True, 'read_at': datetime.now().isoformat()}).eq('id', notification_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {e}")
            return False
    
    # Dashboard operations
    async def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics."""
        try:
            # Get job counts
            jobs_result = self.client.table('scraping_jobs').select('status').execute()
            job_counts = {'total': 0, 'active': 0, 'completed': 0, 'failed': 0}
            for job in jobs_result.data:
                job_counts['total'] += 1
                status = job['status']
                if status in ['pending', 'running']:
                    job_counts['active'] += 1
                elif status == 'completed':
                    job_counts['completed'] += 1
                elif status == 'failed':
                    job_counts['failed'] += 1
            
            # Get product count
            products_result = self.client.table('products').select('id', count='exact').execute()
            total_products = products_result.count or 0
            
            # Get user count
            users_result = self.client.table('users').select('id', count='exact').execute()
            total_users = users_result.count or 0
            
            # Calculate success rate
            success_rate = 0.0
            if job_counts['total'] > 0:
                success_rate = (job_counts['completed'] / job_counts['total']) * 100
            
            return DashboardStats(
                total_jobs=job_counts['total'],
                active_jobs=job_counts['active'],
                completed_jobs=job_counts['completed'],
                failed_jobs=job_counts['failed'],
                total_products=total_products,
                total_users=total_users,
                success_rate=round(success_rate, 2),
                last_updated=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return DashboardStats()


# Global database service instance
db_service = DatabaseService()
