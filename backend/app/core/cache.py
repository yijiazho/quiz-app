import os
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from ..schemas.upload import ParsedContentResponse

# Configure logging
logger = logging.getLogger(__name__)

# Cache configuration
CACHE_EXPIRY = timedelta(hours=1)  # Cache entries expire after 1 hour

# In-memory cache
_cache: Dict[str, tuple[Any, datetime]] = {}

async def init_cache():
    """Initialize the cache."""
    logger.info("Initialized in-memory cache")

def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key."""
    args_str = ":".join(str(arg) for arg in args)
    kwargs_str = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_parts = [prefix]
    if args_str:
        key_parts.append(args_str)
    if kwargs_str:
        key_parts.append(kwargs_str)
    return ":".join(key_parts)

async def get_cached_content(key: str) -> Optional[Dict[str, Any]]:
    """Get content from cache."""
    try:
        if key not in _cache:
            return None
        content, cache_time = _cache[key]
        if datetime.utcnow() - cache_time > CACHE_EXPIRY:
            del _cache[key]
            return None
        return content
    except Exception as e:
        logger.error(f"Error getting cached content: {str(e)}")
        return None

async def set_cached_content(key: str, value: Dict[str, Any]) -> None:
    """Set content in cache."""
    try:
        _cache[key] = (value, datetime.utcnow())
    except Exception as e:
        logger.error(f"Error setting cached content: {str(e)}")

def clear_cache() -> None:
    """Clear the entire cache."""
    _cache.clear()
    logger.info("Cache cleared") 