import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "QuizForge API"
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./quizforge.db")
    
    # Cache settings
    CACHE_EXPIRY: int = 3600  # 1 hour in seconds
    
    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings() 