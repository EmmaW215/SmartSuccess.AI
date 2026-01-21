"""
SmartSuccess.AI GPU Backend - Pydantic Schemas
Data models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class InterviewCategory(str, Enum):
    SELF_INTRODUCTION = "self_introduction"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SOFT_SKILLS = "soft_skills"
    SCENARIO = "scenario"


class InterviewDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class VoicePreset(str, Enum):
    PROFESSIONAL_MALE = "professional_male"
    PROFESSIONAL_FEMALE = "professional_female"
    FRIENDLY_MALE = "friendly_male"
    FRIENDLY_FEMALE = "friendly_female"
    NEUTRAL = "neutral"


class EmotionStyle(str, Enum):
    NEUTRAL = "neutral"
    ENCOURAGING = "encouraging"
    SERIOUS = "serious"
    WARM = "warm"


# ============================================================================
# Health & Status
# ============================================================================

class HealthStatus(BaseModel):
    status: str = "healthy"
    gpu_available: bool = False
    gpu_memory_free: Optional[float] = None
    gpu_memory_total: Optional[float] = None
    gpu_utilization: Optional[float] = None
    active_requests: int = 0
    models_loaded: Dict[str, bool] = {}
    uptime_seconds: float = 0
    version: str = "1.0.0"


class GPUStatus(BaseModel):
    available: bool = False
    device_name: Optional[str] = None
    memory_total_gb: Optional[float] = None
    memory_used_gb: Optional[float] = None
    memory_free_gb: Optional[float] = None
    utilization_percent: Optional[float] = None
    temperature_celsius: Optional[float] = None
    cuda_version: Optional[str] = None


# ============================================================================
# Voice / Audio
# ============================================================================

class TranscriptionRequest(BaseModel):
    """Request for audio transcription"""
    language: str = "en"
    task: str = "transcribe"  # transcribe or translate
    word_timestamps: bool = True
    initial_prompt: Optional[str] = None


class TranscriptionResponse(BaseModel):
    """Response from audio transcription"""
    text: str
    language: str
    duration_seconds: float
    segments: Optional[List[Dict[str, Any]]] = None
    word_timestamps: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    processing_time_ms: float


class TTSRequest(BaseModel):
    """Request for text-to-speech synthesis"""
    text: str
    voice_preset: VoicePreset = VoicePreset.PROFESSIONAL_MALE
    emotion: EmotionStyle = EmotionStyle.NEUTRAL
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    language: str = "en"


class TTSResponse(BaseModel):
    """Response from TTS synthesis"""
    audio_base64: str
    duration_seconds: float
    sample_rate: int
    format: str = "wav"
    processing_time_ms: float


# ============================================================================
# RAG / Question Bank
# ============================================================================

class QuestionMetadata(BaseModel):
    """Metadata for interview questions"""
    category: InterviewCategory
    subcategory: Optional[str] = None
    difficulty: InterviewDifficulty = InterviewDifficulty.MEDIUM
    tags: List[str] = []
    source: Optional[str] = None
    evaluation_criteria: Optional[List[str]] = None


class InterviewQuestion(BaseModel):
    """Interview question with metadata"""
    id: str
    question: str
    category: InterviewCategory
    subcategory: Optional[str] = None
    difficulty: InterviewDifficulty = InterviewDifficulty.MEDIUM
    sample_answer: Optional[str] = None
    evaluation_criteria: Optional[List[str]] = None
    tags: List[str] = []
    follow_up_questions: Optional[List[str]] = None
    relevance_score: Optional[float] = None


class RAGQueryRequest(BaseModel):
    """Request for RAG query"""
    query: str
    category: Optional[InterviewCategory] = None
    n_results: int = Field(default=5, ge=1, le=20)
    difficulty: Optional[InterviewDifficulty] = None
    include_sample_answers: bool = False


class RAGQueryResponse(BaseModel):
    """Response from RAG query"""
    questions: List[InterviewQuestion]
    query_time_ms: float
    total_results: int


# ============================================================================
# Personalized RAG (MatchWise Integration)
# ============================================================================

class MatchWiseAnalysisData(BaseModel):
    """Data from MatchWise.ai analysis"""
    resume_text: str
    job_description: str
    match_score: float = Field(ge=0, le=100)
    strengths: List[str] = []
    gaps: List[str] = []
    recommendations: List[str] = []
    skills_match: Dict[str, float] = {}  # skill -> match percentage
    experience_match: Optional[float] = None
    keywords_matched: List[str] = []
    keywords_missing: List[str] = []


class PersonalizedRAGRequest(BaseModel):
    """Request to build personalized RAG"""
    user_id: str
    matchwise_data: MatchWiseAnalysisData
    focus_categories: Optional[List[InterviewCategory]] = None
    difficulty_preference: InterviewDifficulty = InterviewDifficulty.MEDIUM
    num_questions: int = Field(default=20, ge=5, le=50)


class PersonalizedRAGResponse(BaseModel):
    """Response from personalized RAG building"""
    rag_id: str
    user_id: str
    status: str
    question_bank_size: int
    categories_covered: List[InterviewCategory]
    focus_areas: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None


class PersonalizedQuestionRequest(BaseModel):
    """Request for personalized question"""
    rag_id: str
    category: Optional[InterviewCategory] = None
    difficulty: Optional[InterviewDifficulty] = None
    exclude_ids: List[str] = []


# ============================================================================
# Interview Session
# ============================================================================

class InterviewConfig(BaseModel):
    """Configuration for interview session"""
    categories: List[InterviewCategory] = [InterviewCategory.SELF_INTRODUCTION]
    use_voice: bool = True
    use_personalized_rag: bool = False
    rag_id: Optional[str] = None
    voice_preset: VoicePreset = VoicePreset.PROFESSIONAL_MALE
    difficulty: InterviewDifficulty = InterviewDifficulty.MEDIUM
    max_questions: int = 10
    time_limit_minutes: Optional[int] = None


class StartInterviewRequest(BaseModel):
    """Request to start interview"""
    user_id: str
    config: InterviewConfig
    matchwise_data: Optional[MatchWiseAnalysisData] = None


class InterviewSessionResponse(BaseModel):
    """Response with interview session info"""
    session_id: str
    user_id: str
    status: str
    config: InterviewConfig
    current_question_index: int = 0
    total_questions: int
    started_at: datetime
    gpu_mode: bool = True


class InterviewMessageRequest(BaseModel):
    """Request for interview message"""
    session_id: str
    message: str
    audio_base64: Optional[str] = None  # If voice input


class InterviewMessageResponse(BaseModel):
    """Response to interview message"""
    session_id: str
    response: str
    audio_base64: Optional[str] = None  # If voice output
    question: Optional[InterviewQuestion] = None
    feedback: Optional[Dict[str, Any]] = None
    session_complete: bool = False
    next_action: str = "continue"  # continue, feedback, complete


class InterviewFeedback(BaseModel):
    """Feedback for interview answer"""
    question_id: str
    overall_score: float = Field(ge=0, le=100)
    strengths: List[str] = []
    growth_areas: List[str] = []
    star_analysis: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []
    keywords_used: List[str] = []
    keywords_missing: List[str] = []


class SessionFeedback(BaseModel):
    """Overall session feedback"""
    session_id: str
    overall_score: float = Field(ge=0, le=100)
    total_questions: int
    questions_answered: int
    category_scores: Dict[str, float] = {}
    strengths: List[str] = []
    growth_areas: List[str] = []
    recommendations: List[str] = []
    performance_trend: Optional[str] = None
    comparison_to_average: Optional[float] = None


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    code: str = "UNKNOWN_ERROR"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "Validation Error"
    detail: List[Dict[str, Any]]
    code: str = "VALIDATION_ERROR"


# ============================================================================
# Embedding
# ============================================================================

class EmbeddingRequest(BaseModel):
    """Request for text embedding"""
    texts: List[str]
    normalize: bool = True


class EmbeddingResponse(BaseModel):
    """Response with embeddings"""
    embeddings: List[List[float]]
    dimension: int
    model: str
    processing_time_ms: float


# ============================================================================
# Pre-RAG Question Bank
# ============================================================================

class QuestionBankStats(BaseModel):
    """Statistics for question bank"""
    total_questions: int
    by_category: Dict[str, int]
    by_difficulty: Dict[str, int]
    by_subcategory: Dict[str, int]
    last_updated: datetime


class QuestionBankUpdateRequest(BaseModel):
    """Request to update question bank"""
    questions: List[InterviewQuestion]
    mode: str = "append"  # append or replace


# ============================================================================
# Export
# ============================================================================

__all__ = [
    # Enums
    "InterviewCategory",
    "InterviewDifficulty", 
    "VoicePreset",
    "EmotionStyle",
    # Health
    "HealthStatus",
    "GPUStatus",
    # Voice
    "TranscriptionRequest",
    "TranscriptionResponse",
    "TTSRequest",
    "TTSResponse",
    # RAG
    "QuestionMetadata",
    "InterviewQuestion",
    "RAGQueryRequest",
    "RAGQueryResponse",
    # Personalized RAG
    "MatchWiseAnalysisData",
    "PersonalizedRAGRequest",
    "PersonalizedRAGResponse",
    "PersonalizedQuestionRequest",
    # Interview
    "InterviewConfig",
    "StartInterviewRequest",
    "InterviewSessionResponse",
    "InterviewMessageRequest",
    "InterviewMessageResponse",
    "InterviewFeedback",
    "SessionFeedback",
    # Errors
    "ErrorResponse",
    "ValidationErrorResponse",
    # Embedding
    "EmbeddingRequest",
    "EmbeddingResponse",
    # Question Bank
    "QuestionBankStats",
    "QuestionBankUpdateRequest",
]
