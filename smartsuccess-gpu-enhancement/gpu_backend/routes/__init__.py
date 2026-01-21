"""Routes module for SmartSuccess.AI GPU Backend"""

from .health_routes import router as health_router
from .interview_routes import router as interview_router
from .rag_routes import router as rag_router
from .voice_routes import router as voice_router

__all__ = [
    "health_router",
    "interview_router", 
    "rag_router",
    "voice_router"
]
