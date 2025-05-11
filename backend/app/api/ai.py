from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from ..services.ai_interface import AIInterface
from ..services.openai_service import OpenAIService, OpenAIServiceError
from ..schemas.ai import QuizGenerationRequest, QuizResponse
from ..core.dependencies import get_ai_service
from ..core.cache import get_cache_key, get_cached_content, set_cached_content

router = APIRouter(tags=["AI"])

@router.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(
    request: QuizGenerationRequest,
    ai_service: AIInterface = Depends(get_ai_service)
) -> QuizResponse:
    """
    Generate a quiz from the given content.
    The quiz will be cached for 1 hour to avoid unnecessary API calls.
    """
    # Generate cache key
    cache_key = get_cache_key(
        "quiz",
        content=request.content,
        num_questions=request.num_questions,
        question_type=request.question_type,
        difficulty=request.difficulty
    )
    
    # Try to get from cache
    cached_result = await get_cached_content(cache_key)
    if cached_result:
        return QuizResponse(**cached_result)
    
    try:
        # Generate new quiz
        async with ai_service as service:
            result = await service.generate_quiz(
                content=request.content,
                num_questions=request.num_questions,
                question_type=request.question_type,
                difficulty=request.difficulty
            )
            
            # Cache the result
            await set_cached_content(cache_key, result.dict())
            return result
            
    except OpenAIServiceError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") 