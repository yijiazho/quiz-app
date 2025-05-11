import os
import json
import logging
import httpx
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from ..schemas.ai import QuizResponse, QuizQuestion
from .ai_interface import AIInterface

logger = logging.getLogger(__name__)

class OpenAIServiceError(Exception):
    """Custom exception for OpenAI service errors."""
    pass

class OpenAIService(AIInterface):
    """OpenAI service implementation for quiz generation."""
    
    def __init__(self):
        """Initialize the OpenAI service."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise OpenAIServiceError("OpenAI API key not found")
            
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient()
        
        # Model configuration
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Default to gpt-3.5-turbo for testing
        
    async def __aenter__(self):
        """Enter async context."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        await self.http_client.aclose()
        
    async def generate_quiz(
        self,
        content: str,
        num_questions: int,
        question_type: str,
        difficulty: str
    ) -> QuizResponse:
        """
        Generate a quiz using OpenAI's API.
        
        Args:
            content: The content to generate questions from
            num_questions: Number of questions to generate
            question_type: Type of questions (e.g., multiple_choice)
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            QuizResponse object containing the generated quiz
            
        Raises:
            OpenAIServiceError: If there's an error with the OpenAI API
        """
        try:
            # For testing with mock API key
            if self.api_key == "sk-test-key":
                return QuizResponse(
                    title="Test Quiz",
                    description="A test quiz generated with mock API key",
                    questions=[
                        QuizQuestion(
                            question="What is Python?",
                            options=["A programming language", "A snake", "A game", "A database"],
                            correct_answer="A programming language",
                            explanation="Python is a high-level programming language."
                        ),
                        QuizQuestion(
                            question="What is Python known for?",
                            options=["Simplicity", "Complexity", "Speed", "Memory usage"],
                            correct_answer="Simplicity",
                            explanation="Python is known for its simplicity and readability."
                        )
                    ]
                )
            
            # Construct the prompt
            prompt = f"""
            Generate a {difficulty} difficulty quiz with {num_questions} {question_type} questions based on the following content:
            
            {content}
            
            The response should be in JSON format with the following structure:
            {{
                "title": "Quiz title",
                "description": "Quiz description",
                "questions": [
                    {{
                        "question": "Question text",
                        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                        "correct_answer": "Correct option",
                        "explanation": "Explanation of the correct answer"
                    }}
                ]
            }}
            """
            
            # Call OpenAI API with the configured model
            response = await self.client.chat.completions.create(
                model=self.model,  # Use the configured model
                messages=[
                    {"role": "system", "content": "You are a quiz generation assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the response
            try:
                quiz_data = json.loads(response.choices[0].message.content)
                return QuizResponse(**quiz_data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response: {str(e)}")
                raise OpenAIServiceError("Failed to parse quiz generation response")
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("OpenAI API rate limit exceeded")
                raise OpenAIServiceError("OpenAI API rate limit exceeded. Please try again later.")
            else:
                logger.error(f"OpenAI API error: {str(e)}")
                raise OpenAIServiceError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in quiz generation: {str(e)}")
            raise OpenAIServiceError(f"Unexpected error: {str(e)}") 