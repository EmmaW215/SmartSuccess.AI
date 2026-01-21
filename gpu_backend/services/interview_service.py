"""
SmartSuccess.AI GPU Backend - Interview Service
GPU-accelerated interview service with advanced features
"""

import asyncio
import logging
import time
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from config import get_settings, get_model_config, is_gpu_available
from models.schemas import (
    InterviewQuestion,
    InterviewCategory,
    InterviewDifficulty,
    InterviewConfig,
    StartInterviewRequest,
    InterviewSessionResponse,
    InterviewMessageRequest,
    InterviewMessageResponse,
    InterviewFeedback,
    SessionFeedback,
    MatchWiseAnalysisData,
    PersonalizedRAGRequest,
    TranscriptionRequest,
    TTSRequest,
    VoicePreset,
    EmotionStyle
)
from services.prerag_service import get_prerag_service
from services.matchwise_service import get_matchwise_service
from services.voice_service import get_voice_service, get_voice_service_with_fallback
from services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


# Interview prompts for LLM
INTERVIEW_PROMPTS = {
    "system": """You are an experienced AI/ML technical interviewer conducting a mock interview.
Your role is to:
1. Ask relevant interview questions based on the candidate's background
2. Provide constructive feedback using the STAR method
3. Be professional, encouraging, and helpful
4. Adapt difficulty based on the candidate's responses

Current interview context:
- Category: {category}
- Difficulty: {difficulty}
- User has resume: {has_resume}
""",
    
    "feedback": """Analyze the candidate's response and provide feedback.

Question: {question}
Candidate's Response: {response}

Provide feedback in JSON format:
{{
    "overall_score": <0-100>,
    "strengths": ["strength1", "strength2"],
    "growth_areas": ["area1", "area2"],
    "star_analysis": {{
        "situation": <score 0-100>,
        "task": <score 0-100>,
        "action": <score 0-100>,
        "result": <score 0-100>
    }},
    "suggestions": ["suggestion1", "suggestion2"],
    "keywords_used": ["keyword1"],
    "keywords_missing": ["keyword1"]
}}
""",
    
    "follow_up": """Based on the candidate's response, generate an appropriate follow-up question.
Consider:
- The depth of their answer
- Areas that need clarification
- Opportunities to explore their experience further

Previous question: {question}
Candidate's response: {response}

Generate a follow-up question that digs deeper into their experience.
"""
}


class InterviewSession:
    """Represents an active interview session"""
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        config: InterviewConfig,
        rag_id: Optional[str] = None
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.config = config
        self.rag_id = rag_id
        
        self.started_at = datetime.utcnow()
        self.questions_asked: List[InterviewQuestion] = []
        self.responses: List[Dict[str, Any]] = []
        self.feedback_history: List[InterviewFeedback] = []
        
        self.current_question_index = 0
        self.current_category_index = 0
        self.current_question: Optional[InterviewQuestion] = None
        
        self.state = "started"  # started, in_progress, feedback, completed
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "config": self.config.dict(),
            "rag_id": self.rag_id,
            "started_at": self.started_at.isoformat(),
            "current_question_index": self.current_question_index,
            "total_questions": len(self.questions_asked),
            "state": self.state
        }


class GPUInterviewService:
    """
    GPU-accelerated interview service
    
    Features:
    - Voice-based interviews with Whisper + TTS
    - Personalized questions from MatchWise integration
    - Pre-trained RAG for users without resumes
    - Real-time feedback generation
    - Session management
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.prerag_service = get_prerag_service()
        self.matchwise_service = get_matchwise_service()
        self.voice_service = get_voice_service_with_fallback()
        
        self.active_sessions: Dict[str, InterviewSession] = {}
        self.gpu_mode = is_gpu_available()
        
        logger.info(f"GPUInterviewService initialized (GPU mode: {self.gpu_mode})")
    
    async def start_interview(
        self,
        request: StartInterviewRequest
    ) -> InterviewSessionResponse:
        """Start a new interview session"""
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Build personalized RAG if MatchWise data provided
        rag_id = None
        if request.matchwise_data and request.config.use_personalized_rag:
            try:
                rag_request = PersonalizedRAGRequest(
                    user_id=request.user_id,
                    matchwise_data=request.matchwise_data,
                    focus_categories=request.config.categories,
                    difficulty_preference=request.config.difficulty,
                    num_questions=request.config.max_questions
                )
                rag_response = await self.matchwise_service.build_personalized_rag(rag_request)
                rag_id = rag_response.rag_id
                logger.info(f"Built personalized RAG: {rag_id}")
            except Exception as e:
                logger.error(f"Failed to build personalized RAG: {e}")
        
        # Create session
        session = InterviewSession(
            session_id=session_id,
            user_id=request.user_id,
            config=request.config,
            rag_id=rag_id or request.config.rag_id
        )
        
        self.active_sessions[session_id] = session
        
        return InterviewSessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            status="started",
            config=request.config,
            current_question_index=0,
            total_questions=request.config.max_questions,
            started_at=session.started_at,
            gpu_mode=self.gpu_mode
        )
    
    async def process_message(
        self,
        request: InterviewMessageRequest
    ) -> InterviewMessageResponse:
        """Process an interview message/response"""
        
        session = self.active_sessions.get(request.session_id)
        if not session:
            raise ValueError(f"Session not found: {request.session_id}")
        
        message = request.message.strip()
        audio_response = None
        
        # Handle voice input if provided
        if request.audio_base64:
            try:
                import base64
                audio_data = base64.b64decode(request.audio_base64)
                transcription = await self.voice_service.transcribe(
                    audio_data,
                    TranscriptionRequest(language="en")
                )
                message = transcription.text
            except Exception as e:
                logger.error(f"Voice transcription failed: {e}")
        
        # Process based on session state
        if session.state == "started":
            # Get first question
            question = await self._get_next_question(session)
            session.current_question = question
            session.state = "in_progress"
            
            response_text = f"Let's begin the interview. {question.question}"
            
            # Generate voice response if enabled
            if session.config.use_voice:
                audio_response = await self._generate_voice_response(
                    response_text,
                    session.config.voice_preset
                )
            
            return InterviewMessageResponse(
                session_id=session.session_id,
                response=response_text,
                audio_base64=audio_response,
                question=question,
                feedback=None,
                session_complete=False,
                next_action="continue"
            )
        
        elif session.state == "in_progress":
            # Record response
            session.responses.append({
                "question": session.current_question.dict() if session.current_question else None,
                "response": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Generate feedback for current answer
            feedback = await self._generate_feedback(
                session.current_question,
                message
            )
            session.feedback_history.append(feedback)
            
            # Check if we should continue or end
            if session.current_question_index >= session.config.max_questions - 1:
                # End of interview
                session.state = "completed"
                session_feedback = self._calculate_session_feedback(session)
                
                response_text = "Thank you for completing the interview! Here's your overall feedback."
                
                if session.config.use_voice:
                    audio_response = await self._generate_voice_response(
                        response_text,
                        session.config.voice_preset
                    )
                
                return InterviewMessageResponse(
                    session_id=session.session_id,
                    response=response_text,
                    audio_base64=audio_response,
                    question=None,
                    feedback={"question_feedback": feedback.dict(), "session_feedback": session_feedback.dict()},
                    session_complete=True,
                    next_action="complete"
                )
            
            # Get next question
            session.current_question_index += 1
            next_question = await self._get_next_question(session)
            session.current_question = next_question
            
            response_text = f"Good answer. Here's the next question: {next_question.question}"
            
            if session.config.use_voice:
                audio_response = await self._generate_voice_response(
                    response_text,
                    session.config.voice_preset
                )
            
            return InterviewMessageResponse(
                session_id=session.session_id,
                response=response_text,
                audio_base64=audio_response,
                question=next_question,
                feedback={"question_feedback": feedback.dict()},
                session_complete=False,
                next_action="continue"
            )
        
        else:
            return InterviewMessageResponse(
                session_id=session.session_id,
                response="Interview session has ended.",
                audio_base64=None,
                question=None,
                feedback=None,
                session_complete=True,
                next_action="complete"
            )
    
    async def _get_next_question(
        self,
        session: InterviewSession
    ) -> InterviewQuestion:
        """Get the next question for the session"""
        
        # Determine current category
        categories = session.config.categories
        category = categories[session.current_category_index % len(categories)]
        
        # Get list of already asked question IDs
        asked_ids = [q.id for q in session.questions_asked]
        
        # Try personalized RAG first
        if session.rag_id:
            from models.schemas import PersonalizedQuestionRequest
            question = self.matchwise_service.get_personalized_question(
                PersonalizedQuestionRequest(
                    rag_id=session.rag_id,
                    category=category,
                    difficulty=session.config.difficulty,
                    exclude_ids=asked_ids
                )
            )
            if question:
                session.questions_asked.append(question)
                return question
        
        # Fall back to pre-RAG
        question = self.prerag_service.get_random_question(
            category=category,
            difficulty=session.config.difficulty,
            exclude_ids=asked_ids
        )
        
        if question:
            session.questions_asked.append(question)
            # Rotate category for next question
            session.current_category_index += 1
            return question
        
        # Ultimate fallback - generic question
        return InterviewQuestion(
            id=f"fallback_{session.current_question_index}",
            question="Tell me about a challenging project you've worked on and how you handled it.",
            category=category,
            difficulty=session.config.difficulty,
            tags=["general", "behavioral"]
        )
    
    async def _generate_feedback(
        self,
        question: InterviewQuestion,
        response: str
    ) -> InterviewFeedback:
        """Generate feedback for a response"""
        
        # In production, this would call an LLM
        # For now, provide structured feedback based on response length and keywords
        
        response_words = len(response.split())
        
        # Basic scoring based on response length
        if response_words < 20:
            score = 50
            length_feedback = "Consider providing more detail in your response."
        elif response_words < 50:
            score = 70
            length_feedback = "Good level of detail."
        elif response_words < 150:
            score = 85
            length_feedback = "Great comprehensive response."
        else:
            score = 90
            length_feedback = "Excellent thorough response."
        
        # Check for STAR method components
        star_analysis = {
            "situation": 0,
            "task": 0,
            "action": 0,
            "result": 0
        }
        
        response_lower = response.lower()
        
        if any(word in response_lower for word in ["when", "while", "during", "at"]):
            star_analysis["situation"] = 80
        if any(word in response_lower for word in ["needed", "required", "had to", "goal"]):
            star_analysis["task"] = 80
        if any(word in response_lower for word in ["i did", "i made", "i created", "i developed"]):
            star_analysis["action"] = 80
        if any(word in response_lower for word in ["result", "outcome", "achieved", "improved"]):
            star_analysis["result"] = 80
        
        # Calculate average STAR score
        star_avg = sum(star_analysis.values()) / 4
        final_score = (score + star_avg) / 2
        
        return InterviewFeedback(
            question_id=question.id,
            overall_score=final_score,
            strengths=[
                length_feedback,
                "Shows understanding of the question"
            ],
            growth_areas=[
                "Consider using the STAR method more explicitly" if star_avg < 60 else "Good use of STAR method",
                "Include specific metrics or outcomes" if "%" not in response else "Good use of metrics"
            ],
            star_analysis=star_analysis,
            suggestions=[
                "Try to quantify your achievements",
                "Include the impact of your actions"
            ],
            keywords_used=question.tags[:3] if question.tags else [],
            keywords_missing=[]
        )
    
    def _calculate_session_feedback(
        self,
        session: InterviewSession
    ) -> SessionFeedback:
        """Calculate overall session feedback"""
        
        if not session.feedback_history:
            return SessionFeedback(
                session_id=session.session_id,
                overall_score=0,
                total_questions=0,
                questions_answered=0,
                category_scores={},
                strengths=[],
                growth_areas=[],
                recommendations=[]
            )
        
        # Calculate averages
        total_score = sum(f.overall_score for f in session.feedback_history)
        avg_score = total_score / len(session.feedback_history)
        
        # Calculate category scores
        category_scores = {}
        for q, f in zip(session.questions_asked, session.feedback_history):
            cat = q.category.value
            if cat not in category_scores:
                category_scores[cat] = []
            category_scores[cat].append(f.overall_score)
        
        category_averages = {
            cat: sum(scores) / len(scores)
            for cat, scores in category_scores.items()
        }
        
        # Aggregate strengths and growth areas
        all_strengths = []
        all_growth = []
        for f in session.feedback_history:
            all_strengths.extend(f.strengths)
            all_growth.extend(f.growth_areas)
        
        # Deduplicate and prioritize
        unique_strengths = list(set(all_strengths))[:5]
        unique_growth = list(set(all_growth))[:5]
        
        # Generate recommendations
        recommendations = []
        if avg_score < 60:
            recommendations.append("Consider practicing with the STAR method more frequently")
        if avg_score >= 60 and avg_score < 80:
            recommendations.append("Good foundation - focus on adding more specific examples")
        if avg_score >= 80:
            recommendations.append("Excellent performance - ready for real interviews!")
        
        # Determine trend
        if len(session.feedback_history) >= 3:
            first_half = session.feedback_history[:len(session.feedback_history)//2]
            second_half = session.feedback_history[len(session.feedback_history)//2:]
            
            first_avg = sum(f.overall_score for f in first_half) / len(first_half)
            second_avg = sum(f.overall_score for f in second_half) / len(second_half)
            
            if second_avg > first_avg + 5:
                trend = "improving"
            elif second_avg < first_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = None
        
        return SessionFeedback(
            session_id=session.session_id,
            overall_score=avg_score,
            total_questions=len(session.questions_asked),
            questions_answered=len(session.responses),
            category_scores=category_averages,
            strengths=unique_strengths,
            growth_areas=unique_growth,
            recommendations=recommendations,
            performance_trend=trend,
            comparison_to_average=avg_score - 70  # Assuming 70 is average
        )
    
    async def _generate_voice_response(
        self,
        text: str,
        voice_preset: VoicePreset
    ) -> Optional[str]:
        """Generate voice response using TTS"""
        
        if not self.gpu_mode:
            return None
        
        try:
            tts_response = await self.voice_service.synthesize(
                TTSRequest(
                    text=text,
                    voice_preset=voice_preset,
                    emotion=EmotionStyle.NEUTRAL,
                    speed=1.0
                )
            )
            return tts_response.audio_base64
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get an active session"""
        return self.active_sessions.get(session_id)
    
    def end_session(self, session_id: str) -> Optional[SessionFeedback]:
        """End a session and get final feedback"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        session.state = "completed"
        feedback = self._calculate_session_feedback(session)
        
        # Clean up
        del self.active_sessions[session_id]
        
        return feedback
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.active_sessions)


# Singleton accessor
_interview_service: Optional[GPUInterviewService] = None

def get_gpu_interview_service() -> GPUInterviewService:
    """Get the GPU interview service singleton"""
    global _interview_service
    if _interview_service is None:
        _interview_service = GPUInterviewService()
    return _interview_service
