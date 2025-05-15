from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.api import upload, files  # Add files import
import os
from app.core.database import Base, engine
from app.models import UploadedFile, ParsedContent  # Import models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QuizForge API",
    description="API for creating and managing quizzes from documents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
logger.info("Including routers...")
app.include_router(upload.router)
app.include_router(files.router)  # Add files router
logger.info("Routers included successfully")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up QuizForge API")
    
    # Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Initialize OpenAI
    if settings.OPENAI_API_KEY:
        logger.info("OpenAI API key configured successfully")
    else:
        logger.warning("OpenAI API key not configured")
    
    # Initialize cache
    from app.core.cache import cache
    if not os.environ.get("TESTING"):
        # In production, initialize cache if needed
        if hasattr(cache, "init"):
            cache.init()
        elif hasattr(cache, "__call__"):
            cache()
        # Or call async init_cache if needed
        # from app.core.cache import init_cache
        # await init_cache()
        logger.info("Cache initialized successfully")
    else:
        logger.info("Cache initialization skipped in test mode")

@app.get("/")
async def root():
    return {"message": "Welcome to QuizForge API"} 