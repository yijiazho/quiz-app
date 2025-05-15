import os
import logging
import openai
from typing import Dict, Any, List
from ..core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        """Initialize the AI service with OpenAI configuration."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment variables")
        else:
            openai.api_key = self.api_key
            logger.info("OpenAI API configured successfully")

    async def generate_quiz(self, content: str, num_questions: int = 5, difficulty: str = "medium") -> Dict[str, Any]:
        """
        Generate a quiz from the given content.
        
        Args:
            content: The content to generate questions from
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            Dict containing the generated quiz
        """
        try:
            logger.info(f"Generating quiz with {num_questions} questions at {difficulty} difficulty")
            
            # Prepare the prompt
            prompt = f"""Generate a {difficulty} difficulty quiz with {num_questions} questions based on the following content:

{content}

Format the response as a JSON object with the following structure:
{{
    "title": "Quiz Title",
    "description": "Brief description of the quiz",
    "questions": [
        {{
            "question": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Correct option",
            "explanation": "Explanation of the correct answer"
        }}
    ]
}}"""

            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a quiz generation assistant. Generate educational quizzes based on the provided content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract and parse the response
            quiz_content = response.choices[0].message.content
            logger.info("Quiz generated successfully")
            
            return {
                "status": "success",
                "quiz": quiz_content
            }
            
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}", exc_info=True)
            raise

    async def analyze_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze content and extract key concepts.
        
        Args:
            content: The content to analyze
            
        Returns:
            Dict containing the analysis results
        """
        try:
            logger.info("Analyzing content")
            
            # Prepare the prompt
            prompt = f"""Analyze the following content and extract key concepts, main ideas, and important details:

{content}

Format the response as a JSON object with the following structure:
{{
    "main_topics": ["Topic 1", "Topic 2", ...],
    "key_concepts": ["Concept 1", "Concept 2", ...],
    "important_details": ["Detail 1", "Detail 2", ...],
    "summary": "Brief summary of the content"
}}"""

            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content analysis assistant. Analyze text and extract key information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            # Extract and parse the response
            analysis = response.choices[0].message.content
            logger.info("Content analyzed successfully")
            
            return {
                "status": "success",
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}", exc_info=True)
            raise 