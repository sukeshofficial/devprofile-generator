import json
import hashlib
from typing import Any, Optional, Callable
from database import cache
import httpx
from config import settings

class CacheService:
    def __init__(self):
        self.cache = cache
        self.default_expire = 3600  # 1 hour
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_github_profile(self, username: str) -> Optional[dict]:
        """Get cached GitHub profile"""
        key = self._generate_key("github_profile", username)
        return await self.cache.get(key)
    
    async def set_github_profile(self, username: str, profile: dict, expire: int = None) -> bool:
        """Cache GitHub profile"""
        key = self._generate_key("github_profile", username)
        return await self.cache.set(key, profile, expire or self.default_expire)
    
    async def get_github_repos(self, username: str) -> Optional[list]:
        """Get cached GitHub repositories"""
        key = self._generate_key("github_repos", username)
        return await self.cache.get(key)
    
    async def set_github_repos(self, username: str, repos: list, expire: int = None) -> bool:
        """Cache GitHub repositories"""
        key = self._generate_key("github_repos", username)
        return await self.cache.set(key, repos, expire or self.default_expire)
    
    async def get_repository_readme(self, username: str, repo_name: str) -> Optional[str]:
        """Get cached repository README"""
        key = self._generate_key("readme", username, repo_name)
        return await self.cache.get(key)
    
    async def set_repository_readme(self, username: str, repo_name: str, content: str, expire: int = None) -> bool:
        """Cache repository README"""
        key = self._generate_key("readme", username, repo_name)
        return await self.cache.set(key, content, expire or self.default_expire)
    
    async def get_ai_skills_analysis(self, content_hash: str) -> Optional[dict]:
        """Get cached AI skills analysis"""
        key = self._generate_key("ai_skills", content_hash)
        return await self.cache.get(key)
    
    async def set_ai_skills_analysis(self, content_hash: str, analysis: dict, expire: int = None) -> bool:
        """Cache AI skills analysis"""
        key = self._generate_key("ai_skills", content_hash)
        return await self.cache.set(key, analysis, expire or self.default_expire)
    
    async def get_ai_job_matches(self, skills_hash: str) -> Optional[list]:
        """Get cached AI job matches"""
        key = self._generate_key("ai_jobs", skills_hash)
        return await self.cache.get(key)
    
    async def set_ai_job_matches(self, skills_hash: str, jobs: list, expire: int = None) -> bool:
        """Cache AI job matches"""
        key = self._generate_key("ai_jobs", skills_hash)
        return await self.cache.set(key, jobs, expire or self.default_expire)
    
    async def get_ai_skill_suggestions(self, skills_hash: str) -> Optional[list]:
        """Get cached AI skill suggestions"""
        key = self._generate_key("ai_suggestions", skills_hash)
        return await self.cache.get(key)
    
    async def set_ai_skill_suggestions(self, skills_hash: str, suggestions: list, expire: int = None) -> bool:
        """Cache AI skill suggestions"""
        key = self._generate_key("ai_suggestions", skills_hash)
        return await self.cache.set(key, suggestions, expire or self.default_expire)
    
    async def get_or_set(self, key: str, func: Callable, expire: int = None) -> Any:
        """Get from cache or execute function and cache result"""
        return await self.cache.get_or_set(key, func, expire or self.default_expire)
    
    async def invalidate_user_cache(self, username: str) -> bool:
        """Invalidate all cache entries for a user"""
        try:
            # Get all keys matching the user pattern
            pattern = f"*{username}*"
            keys = self.cache.redis.keys(pattern)
            
            if keys:
                self.cache.redis.delete(*keys)
            return True
        except Exception as e:
            print(f"Error invalidating user cache: {e}")
            return False
    
    async def clear_all_cache(self) -> bool:
        """Clear all cache entries"""
        try:
            self.cache.redis.flushdb()
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

# Global instance
cache_service = CacheService()

# Decorator for caching function results
def cached(expire: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key = cache_service._generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            result = await cache_service.cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                await cache_service.cache.set(key, result, expire)
            
            return result
        return wrapper
    return decorator
