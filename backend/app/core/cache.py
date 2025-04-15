import os
import logging
from typing import Optional, Any, Dict
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from ..schemas.upload import ParsedContentResponse

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Cache configuration
CACHE_EXPIRE = int(os.getenv("CACHE_EXPIRE", "3600"))  # Default 1 hour
CACHE_PREFIX = os.getenv("CACHE_PREFIX", "quizforge:")
CACHE_EXPIRY = timedelta(hours=1)  # Cache entries expire after 1 hour

# In-memory cache for parsed content
_parsed_content_cache: Dict[str, tuple[ParsedContentResponse, datetime]] = {}

async def init_cache():
    """
    Initialize the cache backend.
    """
    try:
        # Create Redis client
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True
        )
        
        # Test connection
        redis_client.ping()
        logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        
        # Initialize FastAPI cache with Redis backend
        FastAPICache.init(RedisBackend(redis_client), prefix=CACHE_PREFIX)
        logger.info("FastAPI cache initialized with Redis backend")
        
    except Exception as e:
        logger.error(f"Failed to initialize cache: {str(e)}")
        # Fallback to in-memory cache if Redis is not available
        logger.warning("Falling back to in-memory cache")
        from fastapi_cache.backends.inmemory import InMemoryBackend
        FastAPICache.init(InMemoryBackend(), prefix=CACHE_PREFIX)
        logger.info("FastAPI cache initialized with in-memory backend")

def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from the given prefix and arguments.
    
    Args:
        prefix: The prefix for the cache key
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key
        
    Returns:
        A string cache key
    """
    # Convert args to strings
    args_str = ":".join(str(arg) for arg in args)
    
    # Convert kwargs to strings
    kwargs_str = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    
    # Combine all parts
    key_parts = [prefix]
    if args_str:
        key_parts.append(args_str)
    if kwargs_str:
        key_parts.append(kwargs_str)
        
    return ":".join(key_parts)

def cache_with_key(prefix: str, expire: Optional[int] = None):
    """
    Decorator for caching with a custom key prefix.
    
    Args:
        prefix: The prefix for the cache key
        expire: Cache expiration time in seconds (optional)
        
    Returns:
        A decorator function
    """
    def decorator(func):
        @cache(
            expire=expire or CACHE_EXPIRE,
            key_builder=lambda *args, **kwargs: get_cache_key(prefix, *args, **kwargs)
        )
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def invalidate_cache(prefix: str, *args, **kwargs):
    """
    Invalidate cache entries with the given prefix and arguments.
    
    Args:
        prefix: The prefix for the cache key
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key
    """
    try:
        key = get_cache_key(prefix, *args, **kwargs)
        await FastAPICache.clear(key)
        logger.info(f"Cache invalidated for key: {key}")
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {str(e)}")

def get_cached_parsed_content(file_id: str) -> Optional[ParsedContentResponse]:
    """
    Get parsed content from cache if available and not expired.
    """
    if file_id not in _parsed_content_cache:
        return None
        
    cached_content, cache_time = _parsed_content_cache[file_id]
    if datetime.utcnow() - cache_time > CACHE_EXPIRY:
        # Cache entry has expired
        del _parsed_content_cache[file_id]
        return None
        
    return cached_content

def cache_parsed_content(file_id: str, content: ParsedContentResponse) -> None:
    """
    Cache parsed content with current timestamp.
    """
    try:
        _parsed_content_cache[file_id] = (content, datetime.utcnow())
        logging.debug(f"Cached parsed content for file {file_id}")
    except Exception as e:
        logging.error(f"Error caching parsed content: {str(e)}")

def clear_cache() -> None:
    """
    Clear the entire cache.
    """
    _parsed_content_cache.clear()
    logging.info("Parsed content cache cleared") 