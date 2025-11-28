# services/rag_service.py
"""
RAG Service for SmartSuccess.AI
Builds context from resume + job posting for personalized interviews
"""

import uuid
from typing import Dict, List, Optional
from .embedding_service import EmbeddingService
from .vector_store import VectorStore


class RAGService:
    """Build and query RAG context for interview personalization"""
    
    def __init__(self):
        self.embedder = EmbeddingService()
        self.vector_store = VectorStore()
    
    async def build_user_context(
        self, user_id: str, resume_text: str, job_text: str
    ) -> Dict:
        self.vector_store.delete_user_collection(user_id)
        
        resume_chunks = self.embedder.chunk_text_by_sections(resume_text)
        job_chunks = self.embedder.chunk_text_by_sections(job_text)
        
        all_chunks, metadatas, ids = [], [], []
        
        for i, chunk in enumerate(resume_chunks):
            all_chunks.append(chunk)
            metadatas.append({"source": "resume", "chunk_index": i})
            ids.append(f"resume_{i}_{uuid.uuid4().hex[:8]}")
        
        for i, chunk in enumerate(job_chunks):
            all_chunks.append(chunk)
            metadatas.append({"source": "job_posting", "chunk_index": i})
            ids.append(f"job_{i}_{uuid.uuid4().hex[:8]}")
        
        embeddings = await self.embedder.embed_batch(all_chunks)
        
        await self.vector_store.upsert_documents(
            user_id=user_id, documents=all_chunks,
            embeddings=embeddings, metadatas=metadatas, ids=ids
        )
        
        return {
            "status": "success",
            "resume_chunks": len(resume_chunks),
            "job_chunks": len(job_chunks),
            "total_chunks": len(all_chunks)
        }
    
    async def query_context(
        self, user_id: str, query: str,
        n_results: int = 5, source_filter: Optional[str] = None
    ) -> str:
        query_embedding = await self.embedder.embed_text(query)
        where_filter = {"source": source_filter} if source_filter else None
        
        results = await self.vector_store.query(
            user_id=user_id, query_embedding=query_embedding,
            n_results=n_results, where_filter=where_filter
        )
        
        context_parts = []
        if results["documents"] and results["documents"][0]:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                source_label = meta.get("source", "unknown").upper()
                context_parts.append(f"[{source_label}]: {doc}")
        
        return "\n\n---\n\n".join(context_parts)
    
    async def get_technical_context(self, user_id: str) -> str:
        return await self.query_context(
            user_id, "technical skills programming tools technologies", n_results=4
        )
    
    async def get_soft_skills_context(self, user_id: str) -> str:
        return await self.query_context(
            user_id, "teamwork communication leadership collaboration", n_results=4
        )

