import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

class JobScheduler:
    """Handles automated job scheduling and execution"""
    
    def __init__(self):
        self.scheduled_jobs = {}
        self.is_running = False
    
    def schedule_daily_catalog_scrape(self, retailer: str, category_url: str, job_name: str):
        """Schedule daily catalog scraping for a retailer"""
        job_id = f"daily_catalog_{retailer}_{datetime.now().timestamp()}"
        
        job_config = {
            'job_id': job_id,
            'name': job_name,
            'retailer': retailer,
            'job_type': 'catalog',
            'category_url': category_url,
            'schedule': 'daily',
            'next_run': datetime.now() + timedelta(days=1),
            'is_active': True,
            'created_at': datetime.now().isoformat()
        }
        
        self.scheduled_jobs[job_id] = job_config
        
        # Schedule with python-schedule
        schedule.every().day.at("02:00").do(
            self._execute_scheduled_job, 
            job_id=job_id
        ).tag(job_id)
        
        logger.info(f"Scheduled daily catalog scrape for {retailer}: {job_name}")
        return job_id
    
    def schedule_hourly_price_updates(self, retailer: str, product_urls: List[str], job_name: str):
        """Schedule hourly price updates for specific products"""
        job_id = f"hourly_price_{retailer}_{datetime.now().timestamp()}"
        
        job_config = {
            'job_id': job_id,
            'name': job_name,
            'retailer': retailer,
            'job_type': 'price_update',
            'product_urls': product_urls,
            'schedule': 'hourly',
            'next_run': datetime.now() + timedelta(hours=1),
            'is_active': True,
            'created_at': datetime.now().isoformat()
        }
        
        self.scheduled_jobs[job_id] = job_config
        
        # Schedule with python-schedule
        schedule.every().hour.do(
            self._execute_scheduled_job, 
            job_id=job_id
        ).tag(job_id)
        
        logger.info(f"Scheduled hourly price updates for {retailer}: {job_name}")
        return job_id
    
    def schedule_weekly_search_scrape(self, retailer: str, search_queries: List[str], job_name: str):
        """Schedule weekly search-based scraping"""
        job_id = f"weekly_search_{retailer}_{datetime.now().timestamp()}"
        
        job_config = {
            'job_id': job_id,
            'name': job_name,
            'retailer': retailer,
            'job_type': 'search',
            'search_queries': search_queries,
            'schedule': 'weekly',
            'next_run': datetime.now() + timedelta(weeks=1),
            'is_active': True,
            'created_at': datetime.now().isoformat()
        }
        
        self.scheduled_jobs[job_id] = job_config
        
        # Schedule with python-schedule
        schedule.every().monday.at("03:00").do(
            self._execute_scheduled_job, 
            job_id=job_id
        ).tag(job_id)
        
        logger.info(f"Scheduled weekly search scrape for {retailer}: {job_name}")
        return job_id
    
    async def _execute_scheduled_job(self, job_id: str):
        """Execute a scheduled job"""
        try:
            if job_id not in self.scheduled_jobs:
                logger.error(f"Scheduled job {job_id} not found")
                return
            
            job_config = self.scheduled_jobs[job_id]
            if not job_config.get('is_active', False):
                logger.info(f"Scheduled job {job_id} is inactive, skipping")
                return
            
            logger.info(f"Executing scheduled job: {job_id}")
            
            # Create a new scraping job
            job_data = ScrapingJobCreate(
                name=f"Scheduled: {job_config['name']}",
                description=f"Automated {job_config['schedule']} job",
                retailer=job_config['retailer'],
                job_type=job_config['job_type'],
                configuration=job_config
            )
            
            # Execute the job
            await execute_scraping_job(job_id, job_data)
            
            # Update next run time
            if job_config['schedule'] == 'daily':
                job_config['next_run'] = datetime.now() + timedelta(days=1)
            elif job_config['schedule'] == 'hourly':
                job_config['next_run'] = datetime.now() + timedelta(hours=1)
            elif job_config['schedule'] == 'weekly':
                job_config['next_run'] = datetime.now() + timedelta(weeks=1)
            
            logger.info(f"Scheduled job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error executing scheduled job {job_id}: {e}")
    
    def cancel_scheduled_job(self, job_id: str):
        """Cancel a scheduled job"""
        if job_id in self.scheduled_jobs:
            self.scheduled_jobs[job_id]['is_active'] = False
            schedule.clear(job_id)
            logger.info(f"Cancelled scheduled job: {job_id}")
            return True
        return False
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs"""
        return list(self.scheduled_jobs.values())
    
    def get_next_run_times(self) -> Dict[str, str]:
        """Get next run times for all scheduled jobs"""
        next_runs = {}
        for job_id, job_config in self.scheduled_jobs.items():
            if job_config.get('is_active', False):
                next_runs[job_id] = job_config['next_run'].isoformat()
        return next_runs
    
    async def start_scheduler(self):
        """Start the job scheduler"""
        self.is_running = True
        logger.info("Job scheduler started")
        
        while self.is_running:
            try:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in job scheduler: {e}")
                await asyncio.sleep(60)
    
    def stop_scheduler(self):
        """Stop the job scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("Job scheduler stopped")

# Global scheduler instance
job_scheduler = JobScheduler()

# Predefined job templates
JOB_TEMPLATES = {
    'amazon_electronics_daily': {
        'name': 'Amazon Electronics Daily Scrape',
        'retailer': 'amazon',
        'job_type': 'catalog',
        'category_url': 'https://www.amazon.com/s?k=electronics',
        'schedule': 'daily',
        'description': 'Daily scrape of Amazon electronics category'
    },
    'walmart_home_daily': {
        'name': 'Walmart Home & Garden Daily Scrape',
        'retailer': 'walmart',
        'job_type': 'catalog',
        'category_url': 'https://www.walmart.com/browse/home/home-garden',
        'schedule': 'daily',
        'description': 'Daily scrape of Walmart home & garden category'
    },
    'target_fashion_weekly': {
        'name': 'Target Fashion Weekly Scrape',
        'retailer': 'target',
        'job_type': 'search',
        'search_queries': ['clothing', 'shoes', 'accessories'],
        'schedule': 'weekly',
        'description': 'Weekly scrape of Target fashion items'
    },
    'bestbuy_electronics_hourly': {
        'name': 'Best Buy Electronics Price Updates',
        'retailer': 'bestbuy',
        'job_type': 'price_update',
        'product_urls': [],  # Will be populated with specific product URLs
        'schedule': 'hourly',
        'description': 'Hourly price updates for Best Buy electronics'
    }
}

async def setup_default_schedules():
    """Set up default scheduled jobs"""
    try:
        # Schedule daily Amazon electronics scrape
        job_scheduler.schedule_daily_catalog_scrape(
            retailer='amazon',
            category_url='https://www.amazon.com/s?k=electronics',
            job_name='Amazon Electronics Daily'
        )
        
        # Schedule daily Walmart home & garden scrape
        job_scheduler.schedule_daily_catalog_scrape(
            retailer='walmart',
            category_url='https://www.walmart.com/browse/home/home-garden',
            job_name='Walmart Home & Garden Daily'
        )
        
        # Schedule weekly Target fashion search
        job_scheduler.schedule_weekly_search_scrape(
            retailer='target',
            search_queries=['clothing', 'shoes', 'accessories'],
            job_name='Target Fashion Weekly'
        )
        
        logger.info("Default scheduled jobs configured")
        
    except Exception as e:
        logger.error(f"Error setting up default schedules: {e}")

async def run_scheduler():
    """Run the job scheduler in background"""
    await job_scheduler.start_scheduler()
