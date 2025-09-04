"""
In-memory TTL cache for expensive operations

Provides caching functionality for GitHub API calls and AI responses
to reduce latency and API usage.
"""

import time
from typing import Any, Optional, Dict
import threading

class TTLCache:
    """Thread-safe in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                return None
            
            return entry["value"]
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL in seconds"""
        with self._lock:
            self._cache[key] = {
                "value": value,
                "expires_at": time.time() + ttl
            }
    
    def delete(self, key: str):
        """Delete key from cache"""
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self):
        """Remove expired entries from cache"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if current_time > entry["expires_at"]
            ]
            for key in expired_keys:
                del self._cache[key]

# Global cache instance
_cache = TTLCache()

def cache_get(key: str) -> Optional[Any]:
    """Get value from global cache"""
    return _cache.get(key)

def cache_set(key: str, value: Any, ttl: int = 3600):
    """Set value in global cache"""
    _cache.set(key, value, ttl)

def cache_delete(key: str):
    """Delete key from global cache"""
    _cache.delete(key)

def cache_clear():
    """Clear global cache"""
    _cache.clear()

def cache_cleanup():
    """Clean up expired entries"""
    _cache.cleanup_expired()

# Background cleanup (in production, use a proper scheduler)
import threading
import time

def _background_cleanup():
    """Background thread to clean up expired cache entries"""
    while True:
        time.sleep(300)  # Clean up every 5 minutes
        cache_cleanup()

# Start background cleanup thread
cleanup_thread = threading.Thread(target=_background_cleanup, daemon=True)
cleanup_thread.start()