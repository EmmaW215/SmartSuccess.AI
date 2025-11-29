# services/embedding_service.py
"""
Embedding Service for SmartSuccess.AI
Generates text embeddings using OpenAI-compatible APIs (OpenAI or xAI)
"""

import os
import re
from typing import List
import openai


class EmbeddingService:
    """Generate embeddings for text using OpenAI or xAI API"""
    
    def __init__(self):
        # Try xAI first, then fall back to OpenAI
        xai_key = os.getenv("XAI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if xai_key:
            # Use xAI (Grok) API - OpenAI compatible
            self.client = openai.OpenAI(
                api_key=xai_key,
                base_url="https://api.x.ai/v1"
            )
            self.model = "text-embedding-3-small"  # xAI supports OpenAI-compatible models
            self.provider = "xAI"
            print("EmbeddingService initialized with xAI API")
        elif openai_key:
            # Fall back to OpenAI
            self.client = openai.OpenAI(api_key=openai_key)
            self.model = "text-embedding-3-small"
            self.provider = "OpenAI"
            print("EmbeddingService initialized with OpenAI API")
        else:
            raise ValueError("Neither XAI_API_KEY nor OPENAI_API_KEY environment variable is set")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text string"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error ({self.provider}): {e}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in one API call"""
        if not texts:
            return []
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Batch embedding error ({self.provider}): {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks for better retrieval"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    def chunk_text_by_sections(self, text: str) -> List[str]:
        """Smart chunking that preserves section boundaries"""
        section_patterns = [
            r'\n(?=(?:EXPERIENCE|EDUCATION|SKILLS|SUMMARY|ABOUT|REQUIREMENTS|RESPONSIBILITIES|QUALIFICATIONS))',
            r'\n(?=[A-Z][A-Z\s]{3,}:)',
        ]
        chunks = [text]
        for pattern in section_patterns:
            new_chunks = []
            for chunk in chunks:
                parts = re.split(pattern, chunk, flags=re.IGNORECASE)
                new_chunks.extend([p.strip() for p in parts if p.strip()])
            chunks = new_chunks
        
        final_chunks = []
        for chunk in chunks:
            if len(chunk.split()) > 600:
                final_chunks.extend(self.chunk_text(chunk, chunk_size=400, overlap=50))
            else:
                final_chunks.append(chunk)
        return final_chunks
