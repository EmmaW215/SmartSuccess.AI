"""
SmartSuccess.AI GPU Backend - Embedding Service
GPU-accelerated text embedding generation
"""

import torch
import numpy as np
from typing import List, Optional, Union
from sentence_transformers import SentenceTransformer
import logging
import time
from functools import lru_cache

from config import get_settings, get_model_config, get_device, is_gpu_available

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    GPU-accelerated embedding service using SentenceTransformers
    
    Features:
    - Batch processing for efficiency
    - GPU acceleration when available
    - Caching for repeated queries
    - Fallback to CPU if GPU fails
    """
    
    _instance: Optional["EmbeddingService"] = None
    
    def __new__(cls):
        """Singleton pattern for model efficiency"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.settings = get_settings()
        self.model_config = get_model_config()
        self.device = get_device()
        self.model: Optional[SentenceTransformer] = None
        self._initialized = True
        
        logger.info(f"EmbeddingService initialized on device: {self.device}")
    
    def load_model(self) -> bool:
        """Load the embedding model"""
        if self.model is not None:
            return True
            
        try:
            logger.info(f"Loading embedding model: {self.model_config.EMBEDDING_MODEL_NAME}")
            start_time = time.time()
            
            self.model = SentenceTransformer(
                self.model_config.EMBEDDING_MODEL_NAME,
                device=self.device
            )
            
            # Optimize for inference
            if self.device == "cuda":
                self.model.half()  # FP16 for faster inference
            
            load_time = time.time() - start_time
            logger.info(f"Embedding model loaded in {load_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            # Try CPU fallback
            if self.device == "cuda":
                logger.info("Attempting CPU fallback...")
                self.device = "cpu"
                return self.load_model()
            return False
    
    def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
        batch_size: Optional[int] = None,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            normalize: Whether to L2-normalize embeddings
            batch_size: Batch size for processing
            show_progress: Show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        if not self.load_model():
            raise RuntimeError("Failed to load embedding model")
        
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
        
        # Set batch size
        if batch_size is None:
            batch_size = 32 if self.device == "cuda" else 8
        
        try:
            start_time = time.time()
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            
            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"Generated {len(texts)} embeddings in {elapsed:.2f}ms")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query
        Optimized for single queries
        """
        return self.encode(query, normalize=True)[0]
    
    def encode_documents(
        self,
        documents: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for documents
        Optimized for batch processing
        """
        return self.encode(
            documents,
            normalize=True,
            batch_size=batch_size,
            show_progress=show_progress
        )
    
    def similarity(
        self,
        embeddings1: np.ndarray,
        embeddings2: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity between embeddings
        
        Args:
            embeddings1: First set of embeddings (N x D)
            embeddings2: Second set of embeddings (M x D)
            
        Returns:
            Similarity matrix (N x M)
        """
        # Ensure 2D
        if embeddings1.ndim == 1:
            embeddings1 = embeddings1.reshape(1, -1)
        if embeddings2.ndim == 1:
            embeddings2 = embeddings2.reshape(1, -1)
        
        # Normalize if not already
        embeddings1 = embeddings1 / np.linalg.norm(embeddings1, axis=1, keepdims=True)
        embeddings2 = embeddings2 / np.linalg.norm(embeddings2, axis=1, keepdims=True)
        
        return np.dot(embeddings1, embeddings2.T)
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        if not self.load_model():
            return self.model_config.EMBEDDING_DIMENSION
        return self.model.get_sentence_embedding_dimension()
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "model_name": self.model_config.EMBEDDING_MODEL_NAME,
            "dimension": self.get_dimension(),
            "device": self.device,
            "loaded": self.model is not None,
            "max_length": self.model_config.EMBEDDING_MAX_LENGTH
        }
    
    def clear_cache(self):
        """Clear any cached data"""
        if hasattr(self.model, 'clear_cache'):
            self.model.clear_cache()
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None
            if self.device == "cuda":
                torch.cuda.empty_cache()
            logger.info("Embedding model unloaded")


# Singleton accessor
@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Get the embedding service singleton"""
    return EmbeddingService()
