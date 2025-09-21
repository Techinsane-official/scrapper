"""
Supabase configuration and connection management.
"""

import os
from typing import Optional
from supabase import create_client, Client
from loguru import logger


class SupabaseConfig:
    """Supabase configuration and client management."""
    
    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL", "")
        self.key: str = os.getenv("SUPABASE_ANON_KEY", "")
        self.service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
        self._client: Optional[Client] = None
        self._admin_client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get Supabase client for regular operations."""
        if not self._client:
            if not self.url or not self.key:
                raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
            self._client = create_client(self.url, self.key)
            logger.info("Supabase client initialized")
        return self._client
    
    @property
    def admin_client(self) -> Client:
        """Get Supabase admin client for elevated operations."""
        if not self._admin_client:
            if not self.url or not self.service_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
            self._admin_client = create_client(self.url, self.service_key)
            logger.info("Supabase admin client initialized")
        return self._admin_client
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return bool(self.url and self.key)
    
    def get_auth(self):
        """Get authentication client."""
        return self.client.auth
    
    def get_storage(self):
        """Get storage client."""
        return self.client.storage
    
    def get_realtime(self):
        """Get realtime client."""
        return self.client.realtime


# Global Supabase instance
supabase_config = SupabaseConfig()


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return supabase_config.client


def get_supabase_admin() -> Client:
    """Get Supabase admin client instance."""
    return supabase_config.admin_client


def get_auth_client():
    """Get Supabase auth client."""
    return supabase_config.get_auth()


def get_storage_client():
    """Get Supabase storage client."""
    return supabase_config.get_storage()


def get_realtime_client():
    """Get Supabase realtime client."""
    return supabase_config.get_realtime()
