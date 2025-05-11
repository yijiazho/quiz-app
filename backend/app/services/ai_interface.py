from abc import ABC, abstractmethod
from typing import Dict, Any
from ..schemas.ai import QuizResponse

class AIInterface(ABC):
    """Abstract base class for AI service implementations."""
    
    @abstractmethod
    async def generate_quiz(
        self,
        content: str,
        num_questions: int = 5,
        question_type: str = "multiple_choice",
        difficulty: str = "medium"
    ) -> QuizResponse:
        """
        Generate a quiz from the given content.
        
        Args:
            content: The content to generate questions from
            num_questions: Number of questions to generate
            question_type: Type of questions to generate
            difficulty: Difficulty level of the questions
            
        Returns:
            A QuizResponse object containing the generated quiz
        """
        pass 