"""
SmartSuccess.AI GPU Backend - Interview Routes
Interview session management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging

from models.schemas import (
    StartInterviewRequest,
    InterviewSessionResponse,
    InterviewMessageRequest,
    InterviewMessageResponse,
    SessionFeedback,
    ErrorResponse
)
from services import get_gpu_interview_service, GPUInterviewService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interview", tags=["Interview"])


def get_service() -> GPUInterviewService:
    """Dependency to get interview service"""
    return get_gpu_interview_service()


@router.post("/start", response_model=InterviewSessionResponse)
async def start_interview(
    request: StartInterviewRequest,
    service: GPUInterviewService = Depends(get_service)
):
    """
    Start a new interview session
    
    This endpoint creates a new interview session with the specified configuration.
    If MatchWise analysis data is provided, it will build a personalized RAG
    for targeted interview questions.
    
    Args:
        request: Interview configuration including user_id, categories, and optional MatchWise data
        
    Returns:
        InterviewSessionResponse with session_id and initial state
    """
    try:
        response = await service.start_interview(request)
        logger.info(f"Started interview session: {response.session_id} for user: {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to start interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=InterviewMessageResponse)
async def process_message(
    request: InterviewMessageRequest,
    service: GPUInterviewService = Depends(get_service)
):
    """
    Process an interview message
    
    Send a message (text or voice) to the interview session and receive
    the next question and/or feedback.
    
    Args:
        request: Message content including session_id and text/audio
        
    Returns:
        InterviewMessageResponse with response, question, and feedback
    """
    try:
        response = await service.process_message(request)
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    service: GPUInterviewService = Depends(get_service)
):
    """
    Get interview session status
    
    Args:
        session_id: The session ID to query
        
    Returns:
        Session information including progress and state
    """
    session = service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_dict()


@router.post("/session/{session_id}/end", response_model=SessionFeedback)
async def end_session(
    session_id: str,
    service: GPUInterviewService = Depends(get_service)
):
    """
    End an interview session
    
    Ends the session and returns final feedback.
    
    Args:
        session_id: The session ID to end
        
    Returns:
        SessionFeedback with overall performance summary
    """
    feedback = service.end_session(session_id)
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Session not found")
    
    logger.info(f"Ended interview session: {session_id}")
    return feedback


@router.get("/stats")
async def get_interview_stats(
    service: GPUInterviewService = Depends(get_service)
):
    """
    Get interview service statistics
    
    Returns:
        Statistics about active sessions and service health
    """
    return {
        "active_sessions": service.get_active_sessions_count(),
        "gpu_mode": service.gpu_mode
    }
