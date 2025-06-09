from typing import AsyncGenerator, Generator
from sqlalchemy.orm import Session
from ..services.ai_interface import AIInterface
from ..services.openai_service import OpenAIService
from .database_config import get_db

def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Uses context manager to ensure proper session cleanup.
    """
    db = get_db()
    try:
        yield db
    finally:
        db.close()

async def get_ai_service() -> AsyncGenerator[AIInterface, None]:
    """
    Dependency that provides an AI service instance.
    Uses async context manager to ensure proper resource cleanup.
    """
    service = OpenAIService()
    try:
        yield service
    finally:
        # The context manager in the route handler will handle cleanup
        pass 