import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from dotenv import load_dotenv
from app.core.logging_config import configure_logging
from app.api import upload, ai, quiz, auth
from app.core.database_config import engine, Base
from app.core.cache import init_cache, cache

# Load environment variables
load_dotenv()

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)

# Create database tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="QuizForge API",
    description="API for the QuizForge application",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request started: {request.method} {request.url}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    # Log request body for non-GET requests, but skip multipart/form-data
    if request.method != "GET" and "multipart/form-data" not in request.headers.get("content-type", ""):
        try:
            body = await request.body()
            if body:
                logger.info(f"Request body: {body.decode()}")
        except Exception as e:
            logger.warning(f"Could not log request body: {str(e)}")
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(f"Request completed: {request.method} {request.url} - Status: {response.status_code} - Duration: {process_time:.2f}s")
    return response

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up QuizForge API")
    try:
        # Verify OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not found in environment variables")
        else:
            logger.info("OpenAI API key configured successfully")
        
        await init_cache()
        logger.info("Cache initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down QuizForge API")

# Include routers
logger.info("Including routers...")
app.include_router(upload.router, tags=["upload"])  # Removed prefix since it's already in the frontend URL
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
logger.info("Routers included successfully")

@app.get("/")
async def root():
    """Root endpoint"""
    logger.debug("Root endpoint accessed")
    return {"status": "ok", "message": "QuizForge API is running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    logger.info("Health check endpoint accessed")
    return {"status": "ok"}

if __name__ == "__main__":
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True) 