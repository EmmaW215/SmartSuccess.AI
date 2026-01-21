"""
SmartSuccess.AI GPU Backend - Main Application
FastAPI entry point with hybrid architecture support

This server provides GPU-accelerated services for:
- Voice interviews (Whisper ASR + XTTS TTS)
- Pre-trained RAG question bank (Tech/AI focused)
- Personalized RAG from MatchWise.ai integration
- Advanced embedding generation

When GPU is unavailable, gracefully degrades to CPU mode or
signals frontend to use Render backend fallback.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings, is_gpu_available
from routes import health_router, interview_router, rag_router, voice_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("gpu_backend.log", mode='a')
    ]
)
logger = logging.getLogger(__name__)


# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("=" * 60)
    logger.info("SmartSuccess.AI GPU Backend Starting...")
    logger.info("=" * 60)
    
    settings = get_settings()
    
    # Check GPU availability
    gpu_available = is_gpu_available()
    logger.info(f"GPU Available: {gpu_available}")
    
    if gpu_available:
        import torch
        logger.info(f"CUDA Version: {torch.version.cuda}")
        logger.info(f"GPU Device: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU Memory: {torch.cuda.mem_get_info()[1] / (1024**3):.2f} GB")
    else:
        logger.warning("No GPU detected - running in CPU mode")
        logger.warning("Voice services will be limited")
    
    # Initialize services
    try:
        logger.info("Initializing Pre-RAG service...")
        from services import get_prerag_service
        prerag_service = get_prerag_service()
        stats = prerag_service.get_stats()
        logger.info(f"Pre-RAG initialized: {stats.total_questions} questions")
    except Exception as e:
        logger.error(f"Failed to initialize Pre-RAG: {e}")
    
    try:
        logger.info("Initializing Embedding service...")
        from services import get_embedding_service
        embedding_service = get_embedding_service()
        embedding_service.load_model()
        logger.info(f"Embedding model loaded: {embedding_service.get_model_info()}")
    except Exception as e:
        logger.error(f"Failed to initialize Embedding service: {e}")
    
    logger.info("=" * 60)
    logger.info(f"Server ready at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"GPU Mode: {gpu_available}")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Shutting down GPU Backend...")
    
    # Cleanup resources
    try:
        from services import get_voice_service
        voice_service = get_voice_service()
        voice_service.unload_models()
    except:
        pass
    
    try:
        from services import get_embedding_service
        embedding_service = get_embedding_service()
        embedding_service.unload_model()
    except:
        pass
    
    if gpu_available:
        import torch
        torch.cuda.empty_cache()
    
    logger.info("GPU Backend shutdown complete")


# Create FastAPI application
settings = get_settings()

app = FastAPI(
    title="SmartSuccess.AI GPU Backend",
    description="""
    GPU-accelerated backend for SmartSuccess.AI mock interview platform.
    
    ## Features
    
    - **Voice Processing**: Whisper large-v3 for ASR, XTTS-v2 for TTS
    - **Pre-RAG**: 5000+ interview questions for Tech/AI domain
    - **Personalized RAG**: MatchWise.ai integration for targeted questions
    - **Embeddings**: GPU-accelerated sentence embeddings
    
    ## Architecture
    
    This server works alongside the main Render backend:
    - Render: User management, payments, basic AI services
    - GPU Server: Voice processing, RAG, embeddings
    
    When GPU is unavailable, frontend falls back to Render.
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests
    """
    start_time = datetime.utcnow()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.2f}ms"
    )
    
    return response


# Include routers
app.include_router(health_router)
app.include_router(interview_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(voice_router, prefix="/api")


# Root endpoint (redirect to docs)
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


# Favicon handler
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return empty response for favicon requests"""
    return JSONResponse(content={})


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
