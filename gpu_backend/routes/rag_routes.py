"""
SmartSuccess.AI GPU Backend - RAG Routes
Pre-RAG and Personalized RAG endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from models.schemas import (
    InterviewCategory,
    InterviewDifficulty,
    InterviewQuestion,
    RAGQueryRequest,
    RAGQueryResponse,
    PersonalizedRAGRequest,
    PersonalizedRAGResponse,
    PersonalizedQuestionRequest,
    QuestionBankStats,
    EmbeddingRequest,
    EmbeddingResponse
)
from services import (
    get_prerag_service, 
    get_matchwise_service,
    get_embedding_service,
    PreRAGService,
    MatchWiseIntegrationService,
    EmbeddingService
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG"])


# ============================================================================
# Pre-RAG (General Question Bank)
# ============================================================================

@router.post("/general/query", response_model=RAGQueryResponse)
async def query_general_rag(
    request: RAGQueryRequest,
    service: PreRAGService = Depends(get_prerag_service)
):
    """
    Query the pre-trained general question bank
    
    Search for interview questions semantically based on query text.
    Optionally filter by category and difficulty.
    
    Args:
        request: Query parameters including search text, category, and difficulty
        
    Returns:
        RAGQueryResponse with matching questions
    """
    try:
        response = service.query(request)
        return response
        
    except Exception as e:
        logger.error(f"Pre-RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/general/random", response_model=InterviewQuestion)
async def get_random_question(
    category: InterviewCategory,
    difficulty: Optional[InterviewDifficulty] = None,
    exclude: Optional[List[str]] = Query(default=[]),
    service: PreRAGService = Depends(get_prerag_service)
):
    """
    Get a random question from the general question bank
    
    Args:
        category: Interview category
        difficulty: Optional difficulty filter
        exclude: List of question IDs to exclude
        
    Returns:
        A random InterviewQuestion
    """
    question = service.get_random_question(
        category=category,
        difficulty=difficulty,
        exclude_ids=exclude
    )
    
    if not question:
        raise HTTPException(
            status_code=404, 
            detail=f"No questions available for category: {category.value}"
        )
    
    return question


@router.get("/general/stats", response_model=QuestionBankStats)
async def get_question_bank_stats(
    service: PreRAGService = Depends(get_prerag_service)
):
    """
    Get statistics about the general question bank
    
    Returns:
        QuestionBankStats with counts by category and difficulty
    """
    return service.get_stats()


@router.post("/general/rebuild")
async def rebuild_question_bank(
    service: PreRAGService = Depends(get_prerag_service)
):
    """
    Rebuild the general question bank
    
    Admin endpoint to rebuild all vector collections from scratch.
    This may take a few minutes.
    
    Returns:
        Confirmation of rebuild
    """
    try:
        service.rebuild_all()
        return {"status": "success", "message": "Question bank rebuilt successfully"}
        
    except Exception as e:
        logger.error(f"Failed to rebuild question bank: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Personalized RAG (MatchWise Integration)
# ============================================================================

@router.post("/personalized/build", response_model=PersonalizedRAGResponse)
async def build_personalized_rag(
    request: PersonalizedRAGRequest,
    service: MatchWiseIntegrationService = Depends(get_matchwise_service)
):
    """
    Build personalized RAG from MatchWise analysis data
    
    This endpoint receives analysis data from MatchWise.ai and builds
    a personalized question bank targeting the user's strengths and gaps.
    
    Args:
        request: User ID, MatchWise analysis data, and preferences
        
    Returns:
        PersonalizedRAGResponse with rag_id and stats
    """
    try:
        response = await service.build_personalized_rag(request)
        logger.info(f"Built personalized RAG: {response.rag_id} for user: {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to build personalized RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/personalized/question", response_model=InterviewQuestion)
async def get_personalized_question(
    request: PersonalizedQuestionRequest,
    service: MatchWiseIntegrationService = Depends(get_matchwise_service)
):
    """
    Get a personalized question from user's RAG
    
    Args:
        request: RAG ID, optional category/difficulty, and exclude list
        
    Returns:
        A personalized InterviewQuestion
    """
    question = service.get_personalized_question(request)
    
    if not question:
        raise HTTPException(
            status_code=404,
            detail=f"No questions available in RAG: {request.rag_id}"
        )
    
    return question


@router.get("/personalized/{rag_id}/query")
async def query_personalized_rag(
    rag_id: str,
    query: str,
    n_results: int = Query(default=5, ge=1, le=20),
    service: MatchWiseIntegrationService = Depends(get_matchwise_service)
):
    """
    Query a personalized RAG
    
    Semantic search within a user's personalized question bank.
    
    Args:
        rag_id: The personalized RAG ID
        query: Search query
        n_results: Number of results to return
        
    Returns:
        List of matching questions
    """
    questions = service.query_personalized_rag(rag_id, query, n_results)
    return {"questions": [q.dict() for q in questions]}


@router.get("/personalized/{rag_id}/info")
async def get_personalized_rag_info(
    rag_id: str,
    service: MatchWiseIntegrationService = Depends(get_matchwise_service)
):
    """
    Get information about a personalized RAG
    
    Args:
        rag_id: The personalized RAG ID
        
    Returns:
        RAG metadata including question count
    """
    info = service.get_rag_info(rag_id)
    
    if not info:
        raise HTTPException(status_code=404, detail=f"RAG not found: {rag_id}")
    
    return info


@router.delete("/personalized/{rag_id}")
async def delete_personalized_rag(
    rag_id: str,
    service: MatchWiseIntegrationService = Depends(get_matchwise_service)
):
    """
    Delete a personalized RAG
    
    Args:
        rag_id: The personalized RAG ID to delete
        
    Returns:
        Confirmation of deletion
    """
    success = service.delete_user_rag(rag_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"RAG not found: {rag_id}")
    
    return {"status": "success", "message": f"Deleted RAG: {rag_id}"}


# ============================================================================
# Embedding Service
# ============================================================================

@router.post("/embedding", response_model=EmbeddingResponse)
async def generate_embeddings(
    request: EmbeddingRequest,
    service: EmbeddingService = Depends(get_embedding_service)
):
    """
    Generate embeddings for texts
    
    GPU-accelerated embedding generation for custom use cases.
    
    Args:
        request: List of texts to embed
        
    Returns:
        EmbeddingResponse with embeddings
    """
    import time
    start = time.time()
    
    try:
        embeddings = service.encode(
            request.texts,
            normalize=request.normalize
        )
        
        processing_time = (time.time() - start) * 1000
        
        return EmbeddingResponse(
            embeddings=embeddings.tolist(),
            dimension=service.get_dimension(),
            model=service.model_config.EMBEDDING_MODEL_NAME,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/embedding/info")
async def get_embedding_info(
    service: EmbeddingService = Depends(get_embedding_service)
):
    """
    Get embedding model information
    
    Returns:
        Model name, dimension, and device information
    """
    return service.get_model_info()
