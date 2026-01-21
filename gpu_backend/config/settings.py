"""
SmartSuccess.AI GPU Backend - Settings Configuration
Centralized configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Main application settings"""
    
    # Application
    APP_NAME: str = "SmartSuccess.AI GPU Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(default=[
        "https://smart-success-ai.vercel.app",
        "https://smartsuccess-ai.vercel.app",
        "https://matchwise-ai.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000"
    ])
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    XAI_API_KEY: Optional[str] = None
    
    # Render Backend (for fallback)
    RENDER_BACKEND_URL: str = "https://smartsuccess-ai.onrender.com"
    
    # Redis (for caching)
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour
    
    # Cloud Storage
    S3_BUCKET: Optional[str] = None
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Data Paths
    DATA_DIR: str = "./data"
    PRERAG_DIR: str = "./data/pre_rag"
    USER_RAG_DIR: str = "./data/user_rag"
    VOICE_PRESETS_DIR: str = "./data/voice_presets"
    MODEL_CACHE_DIR: str = "./models"
    
    # Model Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    WHISPER_MODEL: str = "large-v3"
    TTS_MODEL: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    LLM_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"
    
    # GPU Settings
    GPU_DEVICE: str = "cuda"
    GPU_MEMORY_FRACTION: float = 0.9
    MIXED_PRECISION: bool = True
    
    # Performance
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 60
    BATCH_SIZE: int = 8
    
    # Interview Settings
    MAX_QUESTIONS_PER_SESSION: int = 20
    QUESTION_TIMEOUT: int = 300  # 5 minutes per question
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


class GPUConfig(BaseSettings):
    """GPU-specific configuration"""
    
    # Device settings
    CUDA_VISIBLE_DEVICES: str = "0"
    TORCH_CUDA_ARCH_LIST: str = "7.0;7.5;8.0;8.6;8.9;9.0"
    
    # Memory management
    MAX_GPU_MEMORY: str = "45GB"  # Leave some headroom
    ENABLE_MEMORY_EFFICIENT_ATTENTION: bool = True
    GRADIENT_CHECKPOINTING: bool = False
    
    # Optimization
    USE_FLASH_ATTENTION: bool = True
    USE_SDPA: bool = True
    COMPILE_MODEL: bool = False  # torch.compile can be unstable
    
    # Batch processing
    EMBEDDING_BATCH_SIZE: int = 32
    INFERENCE_BATCH_SIZE: int = 4
    TTS_BATCH_SIZE: int = 1  # TTS is memory intensive
    
    # Timeouts
    MODEL_LOAD_TIMEOUT: int = 300  # 5 minutes
    INFERENCE_TIMEOUT: int = 60
    
    class Config:
        env_file = ".env"
        env_prefix = "GPU_"
        extra = "ignore"  # Ignore extra fields from .env


class ModelConfig(BaseSettings):
    """Model-specific configuration"""
    
    # Whisper ASR
    WHISPER_MODEL_SIZE: str = "large-v3"
    WHISPER_COMPUTE_TYPE: str = "float16"
    WHISPER_LANGUAGE: str = "en"
    WHISPER_TASK: str = "transcribe"
    WHISPER_VAD_FILTER: bool = True
    WHISPER_BEAM_SIZE: int = 5
    
    # TTS
    TTS_MODEL_NAME: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    TTS_SPEAKER_WAV: str = "./data/voice_presets/professional_male.wav"
    TTS_LANGUAGE: str = "en"
    TTS_SPEED: float = 1.0
    
    # Embedding
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-mpnet-base-v2"
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_MAX_LENGTH: int = 512
    
    # LLM (Optional local model)
    LLM_MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.2"
    LLM_MAX_NEW_TOKENS: int = 1024
    LLM_TEMPERATURE: float = 0.7
    LLM_TOP_P: float = 0.9
    LLM_DO_SAMPLE: bool = True
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/pre_rag/chroma"
    CHROMA_COLLECTION_PREFIX: str = "smartsuccess"
    CHROMA_DISTANCE_FN: str = "cosine"
    
    class Config:
        env_file = ".env"
        env_prefix = "MODEL_"
        extra = "ignore"  # Ignore extra fields from .env


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


@lru_cache()
def get_gpu_config() -> GPUConfig:
    """Get cached GPU config instance"""
    return GPUConfig()


@lru_cache()
def get_model_config() -> ModelConfig:
    """Get cached model config instance"""
    return ModelConfig()


# Convenience functions
def is_gpu_available() -> bool:
    """Check if GPU is available"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def get_device() -> str:
    """Get the appropriate device"""
    settings = get_settings()
    if is_gpu_available():
        return settings.GPU_DEVICE
    return "cpu"


def get_data_path(subdir: str = "") -> str:
    """Get data directory path"""
    settings = get_settings()
    base = settings.DATA_DIR
    if subdir:
        return os.path.join(base, subdir)
    return base
