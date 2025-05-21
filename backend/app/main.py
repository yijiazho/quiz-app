from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.api import upload, files, auth
import os
from app.core.database import Base, engine
from app.models import UploadedFile, ParsedContent
from app.core.database_config import db_config, DatabaseError
from app.core.migrations import migration_manager

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
app.include_router(files.router)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
logger.info("Routers included successfully")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up QuizForge API")
    
    # Test database connection
    if not db_config.test_connection():
        logger.error("Failed to connect to database")
        raise RuntimeError("Database connection failed")
    logger.info("Database connection test successful")
    
    # Apply database migrations
    try:
        logger.info("Applying database migrations...")
        migration_manager.apply_migrations()
        logger.info("Database migrations applied successfully")
    except DatabaseError as e:
        logger.error(f"Failed to apply database migrations: {str(e)}")
        raise RuntimeError(f"Database migration failed: {str(e)}")
    
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
        logger.info("Cache initialized successfully")
    else:
        logger.info("Cache initialization skipped in test mode")

@app.get("/")
async def root():
    return {"message": "Welcome to QuizForge API"}

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies database connection and initialization."""
    try:
        # Test database connection
        if not db_config.test_connection():
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        # Get database info
        db_info = db_config.get_db_info()
        
        # Get migration status
        applied_migrations = migration_manager.get_applied_migrations()
        
        return {
            "status": "healthy",
            "database": db_info,
            "migrations": {
                "applied": applied_migrations,
                "total": len(migration_manager._migrations)
            }
        }
    except DatabaseError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/migrations/apply")
async def apply_migrations():
    """Apply all pending database migrations."""
    try:
        migration_manager.apply_migrations()
        return {
            "status": "success",
            "message": "Migrations applied successfully",
            "applied_migrations": migration_manager.get_applied_migrations()
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/migrations/rollback/{version}")
async def rollback_migration(version: int):
    """Rollback a specific migration."""
    try:
        migration_manager.rollback_migration(version)
        return {
            "status": "success",
            "message": f"Migration {version} rolled back successfully"
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e)) 