from supabase import create_client, Client
from config import settings
import redis
import json
from typing import Optional, Any, Dict, List
import asyncio
from functools import wraps

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Initialize Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

class DatabaseManager:
    def __init__(self):
        self.supabase = supabase
        self.redis = redis_client
    
    # User operations
    async def create_user(self, user_data: dict) -> Optional[dict]:
        """Create a new user in Supabase"""
        try:
            result = self.supabase.table("users").insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        try:
            result = self.supabase.table("users").select("*").eq("email", email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    async def update_user(self, user_id: str, update_data: dict) -> Optional[dict]:
        """Update user data"""
        try:
            result = self.supabase.table("users").update(update_data).eq("id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
    
    # Analysis operations
    async def create_analysis(self, analysis_data: dict) -> Optional[dict]:
        """Create a new analysis"""
        try:
            result = self.supabase.table("analyses").insert(analysis_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating analysis: {e}")
            return None
    
    async def get_user_analyses(self, user_id: str) -> List[dict]:
        """Get all analyses for a user"""
        try:
            result = self.supabase.table("analyses").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting user analyses: {e}")
            return []
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[dict]:
        """Get analysis by ID"""
        try:
            result = self.supabase.table("analyses").select("*").eq("id", analysis_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting analysis by ID: {e}")
            return None
    
    async def update_analysis(self, analysis_id: str, update_data: dict) -> Optional[dict]:
        """Update analysis data"""
        try:
            result = self.supabase.table("analyses").update(update_data).eq("id", analysis_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating analysis: {e}")
            return None
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete an analysis"""
        try:
            result = self.supabase.table("analyses").delete().eq("id", analysis_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting analysis: {e}")
            return False
    
    # Portfolio export operations
    async def create_portfolio_export(self, export_data: dict) -> Optional[dict]:
        """Create a portfolio export record"""
        try:
            result = self.supabase.table("portfolio_exports").insert(export_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating portfolio export: {e}")
            return None
    
    async def get_portfolio_exports(self, user_id: str) -> List[dict]:
        """Get portfolio exports for a user"""
        try:
            result = self.supabase.table("portfolio_exports").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting portfolio exports: {e}")
            return []

class CacheManager:
    def __init__(self):
        self.redis = redis_client
    
    def cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        return f"{prefix}:{identifier}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Error getting from cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration"""
        try:
            self.redis.setex(key, expire, json.dumps(value, default=str))
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting from cache: {e}")
            return False
    
    async def get_or_set(self, key: str, func, expire: int = 3600) -> Any:
        """Get from cache or set using function"""
        value = await self.get(key)
        if value is None:
            value = await func()
            if value is not None:
                await self.set(key, value, expire)
        return value

# Global instances
db = DatabaseManager()
cache = CacheManager()
cache_service = CacheManager()

def cache_result(expire: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = await cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                await cache.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator
