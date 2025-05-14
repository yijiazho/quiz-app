import os
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from ..schemas.upload import ParsedContentResponse

# Configure logging
logger = logging.getLogger(__name__)

class Cache:
    def __init__(self):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self.CACHE_EXPIRY = timedelta(hours=1)  # Cache entries expire after 1 hour
        logger.info("Cache instance initialized")

    def get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key."""
        args_str = ":".join(str(arg) for arg in args)
        kwargs_str = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_parts = [prefix]
        if args_str:
            key_parts.append(args_str)
        if kwargs_str:
            key_parts.append(kwargs_str)
        return ":".join(key_parts)

    def get(self, key: str) -> Optional[Any]:
        """Get content from cache."""
        try:
            if key not in self._cache:
                return None
            content, cache_time = self._cache[key]
            if datetime.utcnow() - cache_time > self.CACHE_EXPIRY:
                del self._cache[key]
                return None
            return content
        except Exception as e:
            logger.error(f"Error getting cached content: {str(e)}")
            return None

    def set(self, key: str, value: Any) -> None:
        """Set content in cache."""
        try:
            self._cache[key] = (value, datetime.utcnow())
            logger.debug(f"Content cached for key: {key}")
        except Exception as e:
            logger.error(f"Error setting cached content: {str(e)}")

    def clear(self) -> None:
        """Clear the entire cache."""
        self._cache.clear()
        logger.info("Cache cleared")

# Create a singleton instance
cache = Cache()

async def init_cache():
    """Initialize the cache."""
    logger.info("Initialized in-memory cache")
    return cache 