from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import openai
from ..core.database import get_db
from ..core.cache import cache
from ..services.ai_service import AIService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])
ai_service = AIService()

@router.post("/generate")
async def generate_quiz(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate a quiz based on the provided content.
    """
    try:
        # Get parameters from request
        content = request.get("content")
        num_questions = request.get("num_questions", 5)
        difficulty = request.get("difficulty", "medium")
        
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Generate cache key
        cache_key = cache.get_cache_key("quiz", content, num_questions, difficulty)
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached quiz")
            return cached_result
        
        # Generate new quiz
        logger.info(f"Generating new quiz with {num_questions} questions at {difficulty} difficulty")
        quiz = await ai_service.generate_quiz(content, num_questions, difficulty)
        
        # Cache the result
        cache.set(cache_key, quiz)
        logger.info("Quiz cached successfully")
        
        return quiz
        
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_content(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze content and extract key concepts.
    """
    try:
        content = request.get("content")
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Generate cache key
        cache_key = cache.get_cache_key("analysis", content)
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached analysis")
            return cached_result
        
        # Perform analysis
        logger.info("Performing content analysis")
        analysis = await ai_service.analyze_content(content)
        
        # Cache the result
        cache.set(cache_key, analysis)
        logger.info("Analysis cached successfully")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing content: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 