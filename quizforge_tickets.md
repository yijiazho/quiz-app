# Implementation Tickets – QuizForge

## Epic: Textbook Upload & Processing

### `UPLOAD-001` – File Upload UI (Frontend)
- Drag-and-drop file input
- Accept only PDF, DOCX, TXT
- Show upload progress

### `UPLOAD-002` – File Upload API (Backend)
- POST `/upload` endpoint
- Virus scan, size validation

### `UPLOAD-003` – Data Storage (Backend)
- Choose proper database to store the uploaded files
- Update the backend endpoint to store the file in the database
- Support extracting the file from the database

### `UPLOAD-004` – File Parser Service (Backend)
- Extract structured text from files
- Remove formatting noise
- Segment by chapters/sections

### `UPLOAD-005` – Parser Caching Service (Backend)
- Implement caching for parsed file content
- Use FastAPI cache with Redis or in-memory storage
- Cache invalidation on file updates/deletions
- Configure cache expiration policies
- Add cache status monitoring

---

## Epic: AI/NLP Quiz Generation

### `AI-001` – Concept & Topic Extraction
- Keyphrase extraction using NLP tools
- Handle long content

### `AI-002` – Question Generator (MCQ + T/F)
- Use transformer models
- Generate distractors
- Filter poor questions

### `AI-003` – Answer & Explanation Generator
- Generate correct answers and short explanations

---

## Epic: Quiz Interaction & Review

### `QUIZ-001` – Quiz Generation UI (Frontend)
- Select chapters/sections
- Choose number and type of questions

### `QUIZ-002` – Take Quiz UI (Frontend)
- Navigate through questions
- Submit answers

### `QUIZ-003` – Quiz Submit & Score (Backend)
- Compare answers
- Return score and correct answers

### `QUIZ-004` – Review Mode UI (Frontend)
- Highlight correct/incorrect
- Show explanations

---

## Epic: User Accounts & Auth

### `AUTH-001` – Signup/Login UI (Frontend)
- Email/password and OAuth

### `AUTH-002` – Auth API & JWT (Backend)
- JWT-based session handling

---

## Epic: Infrastructure & DevOps

### `INFRA-001` – Docker Setup
- Dockerfile for frontend, backend, NLP services

### `INFRA-002` – Deploy to Cloud
- Deploy backend + frontend
- HTTPS and domain config

## Current Sprint: Database Integration and Caching

### CACHE-001: Implement Database Query Caching with Redis
**Status**: Open
**Priority**: High
**Description**: Implement Redis-based caching for database queries to improve performance and reduce database load.

**Technical Details**:
- Use Redis as the caching layer
- Cache frequently accessed database queries
- Implement cache invalidation strategies
- Add cache configuration options
- Monitor cache hit/miss rates

**Implementation Plan**:
1. Add Redis dependencies:
   ```python
   # requirements.txt
   redis==5.0.1
   ```

2. Create Redis configuration:
   ```python
   # app/core/config.py
   REDIS_HOST = "localhost"
   REDIS_PORT = 6379
   REDIS_DB = 0
   REDIS_TTL = 3600  # 1 hour default TTL
   ```

3. Implement Redis cache service:
   ```python
   # app/services/cache_service.py
   from redis import Redis
   from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_TTL
   
   class RedisCache:
       def __init__(self):
           self.redis = Redis(
               host=REDIS_HOST,
               port=REDIS_PORT,
               db=REDIS_DB,
               decode_responses=True
           )
           
       async def get(self, key: str) -> Optional[Any]:
           return self.redis.get(key)
           
       async def set(self, key: str, value: Any, ttl: int = REDIS_TTL):
           self.redis.set(key, value, ex=ttl)
           
       async def delete(self, key: str):
           self.redis.delete(key)
           
       async def clear(self):
           self.redis.flushdb()
   ```

4. Add cache decorators for database queries:
   ```python
   # app/core/decorators.py
   from functools import wraps
   from app.services.cache_service import RedisCache
   
   def cache_query(ttl: int = None):
       def decorator(func):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               cache = RedisCache()
               cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
               
               # Try to get from cache
               cached_result = await cache.get(cache_key)
               if cached_result:
                   return cached_result
                   
               # If not in cache, execute query
               result = await func(*args, **kwargs)
               
               # Store in cache
               await cache.set(cache_key, result, ttl)
               return result
           return wrapper
       return decorator
   ```

5. Apply caching to database queries:
   ```python
   # app/services/file_service.py
   from app.core.decorators import cache_query
   
   class FileService:
       @cache_query(ttl=3600)  # Cache for 1 hour
       async def get_file_by_id(self, file_id: str):
           # Existing implementation
           pass
   ```

**Testing Requirements**:
1. Unit tests for Redis cache service
2. Integration tests for cached queries
3. Performance benchmarks
4. Cache invalidation tests
5. Load testing with concurrent requests

**Acceptance Criteria**:
- [ ] Redis cache is properly configured
- [ ] Cache decorators are implemented
- [ ] Cache invalidation works correctly
- [ ] Performance improvement is measurable
- [ ] Cache hit/miss rates are monitored
- [ ] Tests are written and passing
- [ ] Documentation is updated

**Dependencies**:
- Redis server
- Python Redis client
- Monitoring tools for cache metrics

**Notes**:
- Consider using Redis Cluster for production
- Implement circuit breakers for cache failures
- Add cache warming for frequently accessed data
- Monitor memory usage
- Set up alerts for cache performance
