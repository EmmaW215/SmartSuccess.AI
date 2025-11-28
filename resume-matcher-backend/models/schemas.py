# models/schemas.py
"""Pydantic schemas for API request/response validation"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class BuildContextRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    job_text: str = Field(..., description="Job posting text")


class BuildContextResponse(BaseModel):
    status: str
    message: str
    details: Dict


class InterviewStartResponse(BaseModel):
    session_id: str
    message: str
    section: str


class InterviewMessageRequest(BaseModel):
    session_id: str
    message: str


class STARScoreSchema(BaseModel):
    situation: int = Field(ge=1, le=5)
    task: int = Field(ge=1, le=5)
    action: int = Field(ge=1, le=5)
    result: int = Field(ge=1, le=5)
    average: float


class DeliveryMetricsSchema(BaseModel):
    fillerWords: int
    wordCount: int
    speakingTime: float
    pacing: str


class QuestionFeedbackSchema(BaseModel):
    question: str
    response: str
    timestamp: str
    activeListening: Dict
    starScore: STARScoreSchema
    strengths: List[str]
    growthAreas: List[str]
    delivery: DeliveryMetricsSchema


class InterviewMessageResponse(BaseModel):
    response: str
    section: str
    question_index: Optional[int] = None
    is_complete: bool = False
    feedback: Optional[QuestionFeedbackSchema] = None


class FeedbackResponse(BaseModel):
    sessionId: str
    userId: str
    overallScore: float
    questionsFeedback: List[QuestionFeedbackSchema]
    aggregatedStrengths: List[str]
    aggregatedGrowthAreas: List[str]

