from typing import AsyncGenerator
from ..services.ai_interface import AIInterface
from ..services.openai_service import OpenAIService

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