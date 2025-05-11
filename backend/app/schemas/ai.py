from pydantic import BaseModel, Field
from typing import List, Optional

class QuizGenerationRequest(BaseModel):
    content: str = Field(..., description="The content to generate quiz questions from")
    num_questions: int = Field(default=5, ge=1, le=20, description="Number of questions to generate")
    question_type: str = Field(default="multiple_choice", description="Type of questions to generate")
    difficulty: str = Field(default="medium", description="Difficulty level of the questions")

class QuizQuestion(BaseModel):
    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., min_items=2, description="List of possible answers")
    correct_answer: str = Field(..., description="The correct answer")
    explanation: str = Field(..., description="Explanation of why this is the correct answer")

class QuizResponse(BaseModel):
    title: str = Field(..., description="Title of the quiz")
    description: str = Field(..., description="Description of the quiz")
    questions: List[QuizQuestion] = Field(..., description="List of quiz questions") 