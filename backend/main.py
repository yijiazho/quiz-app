from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload
import logging
import os
from dotenv import load_dotenv
from app.core.cache import init_cache

# Load environment variables
load_dotenv()

# Configure logging
logging_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, logging_level))
logger = logging.getLogger(__name__)

# Import database models to ensure they're registered with SQLAlchemy
from app.core.database import Base, engine
from app.models import UploadedFile

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="QuizForge API", description="API for QuizForge application")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

@app.on_event("startup")
async def startup_event():
    """
    Initialize services on application startup.
    """
    logger.info("Initializing application services...")
    await init_cache()
    logger.info("Application services initialized")

@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to QuizForge API", "status": "ok"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    logger.info("Health check endpoint accessed")
    return {"status": "ok"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all requests.
    """
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Import and include routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
# app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True) 