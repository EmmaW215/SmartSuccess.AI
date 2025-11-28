import React, { useState } from 'react';

const files = {
  "services/__init__.py": `# services/__init__.py
"""
SmartSuccess.AI Backend Services
Mock Interview with RAG and STAR Feedback
"""

from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from .rag_service import RAGService
from .interview_service import InterviewService, InterviewSession, InterviewSection
from .feedback_service import FeedbackService, SessionFeedback, QuestionFeedback

__all__ = [
    "EmbeddingService",
    "VectorStore", 
    "RAGService",
    "InterviewService",
    "InterviewSession",
    "InterviewSection",
    "FeedbackService",
    "SessionFeedback",
    "QuestionFeedback"
]
`,

  "services/embedding_service.py": `# services/embedding_service.py
"""
Embedding Service for SmartSuccess.AI
Generates text embeddings using OpenAI's text-embedding-3-small model
"""

import os
import re
from typing import List
import openai


class EmbeddingService:
    """Generate embeddings for text using OpenAI API"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text string"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
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
            print(f"Batch embedding error: {e}")
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
            r'\\n(?=(?:EXPERIENCE|EDUCATION|SKILLS|SUMMARY|ABOUT|REQUIREMENTS|RESPONSIBILITIES|QUALIFICATIONS))',
            r'\\n(?=[A-Z][A-Z\\s]{3,}:)',
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
`,

  "services/vector_store.py": `# services/vector_store.py
"""
Vector Store Service for SmartSuccess.AI
Uses ChromaDB for persistent local vector storage
"""

import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings


class VectorStore:
    """ChromaDB wrapper for vector storage and retrieval"""
    
    def __init__(self):
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        print(f"ChromaDB initialized at: {persist_dir}")
    
    def _get_collection_name(self, user_id: str) -> str:
        clean_id = user_id.replace("-", "_").replace("@", "_at_")[:50]
        return f"user_{clean_id}"
    
    def get_or_create_collection(self, user_id: str):
        collection_name = self._get_collection_name(user_id)
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def upsert_documents(
        self, user_id: str, documents: List[str],
        embeddings: List[List[float]], metadatas: List[Dict], ids: List[str]
    ) -> Dict:
        collection = self.get_or_create_collection(user_id)
        try:
            collection.upsert(
                documents=documents, embeddings=embeddings,
                metadatas=metadatas, ids=ids
            )
            return {"status": "success", "documents_added": len(documents)}
        except Exception as e:
            print(f"Upsert error: {e}")
            raise
    
    async def query(
        self, user_id: str, query_embedding: List[float],
        n_results: int = 5, where_filter: Optional[Dict] = None
    ) -> Dict:
        collection = self.get_or_create_collection(user_id)
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_filter:
            query_params["where"] = where_filter
        try:
            return collection.query(**query_params)
        except Exception as e:
            print(f"Query error: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    
    def delete_user_collection(self, user_id: str) -> bool:
        collection_name = self._get_collection_name(user_id)
        try:
            self.client.delete_collection(collection_name)
            return True
        except ValueError:
            return False
`,

  "services/rag_service.py": `# services/rag_service.py
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
        
        return "\\n\\n---\\n\\n".join(context_parts)
    
    async def get_technical_context(self, user_id: str) -> str:
        return await self.query_context(
            user_id, "technical skills programming tools technologies", n_results=4
        )
    
    async def get_soft_skills_context(self, user_id: str) -> str:
        return await self.query_context(
            user_id, "teamwork communication leadership collaboration", n_results=4
        )
`,

  "services/interview_service.py": `# services/interview_service.py
"""
Interview Service for SmartSuccess.AI
State machine for managing mock interview flow
"""

import os
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from groq import AsyncGroq
from .rag_service import RAGService


class InterviewSection(Enum):
    GREETING = "greeting"
    MENU = "menu"
    SELF_INTRO = "self_intro"
    TECHNICAL = "technical"
    SOFT_SKILL = "soft_skill"
    COMPLETE = "complete"


@dataclass
class InterviewSession:
    session_id: str
    user_id: str
    current_section: InterviewSection = InterviewSection.GREETING
    question_index: int = 0
    messages: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    job_title: str = ""
    
    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role, "content": content,
            "timestamp": datetime.now().isoformat()
        })


class InterviewService:
    
    SELF_INTRO_QUESTIONS = [
        "Please introduce yourself and give me a brief overview of your background.",
        "Why are you interested in this particular role?",
        "Why are you looking to leave your current position?",
        "What makes you the best fit for this position?",
        "What are your greatest strengths and areas for improvement?"
    ]
    
    def __init__(self):
        self.rag_service = RAGService()
        groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = AsyncGroq(api_key=groq_key) if groq_key else None
        self.sessions: Dict[str, InterviewSession] = {}
    
    async def create_session(self, session_id: str, user_id: str) -> InterviewSession:
        session = InterviewSession(session_id=session_id, user_id=user_id)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self.sessions.get(session_id)
    
    async def get_greeting(self) -> str:
        return (
            "Welcome to your Mock Interview!\\n\\n"
            "I'm your AI interviewer today. I've reviewed your resume and job requirements.\\n\\n"
            "When you're ready, just say 'I'm ready' or 'Yes'."
        )
    
    async def get_menu(self) -> str:
        return (
            "Please choose an interview section:\\n\\n"
            "1. Self-Introduction - Tell me about yourself\\n"
            "2. Technical Questions - Based on your skills\\n"
            "3. Soft-Skill Questions - Behavioral questions\\n\\n"
            "Say the number or section name. Say 'STOP' to return here."
        )
    
    async def process_message(self, session_id: str, user_message: str) -> Dict:
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        session.add_message("user", user_message)
        
        if "stop" in user_message.lower():
            session.current_section = InterviewSection.MENU
            session.question_index = 0
            response = "Let's take a break.\\n\\n" + await self.get_menu()
            session.add_message("assistant", response)
            return {"response": response, "section": session.current_section.value}
        
        response = ""
        
        if session.current_section == InterviewSection.GREETING:
            if self._is_ready(user_message):
                session.current_section = InterviewSection.MENU
                response = await self.get_menu()
            else:
                response = "Let me know when you're ready!"
        
        elif session.current_section == InterviewSection.MENU:
            section = self._parse_section_choice(user_message)
            if section:
                session.current_section = section
                session.question_index = 0
                response = await self._get_next_question(session)
            else:
                response = "Please say 1, 2, or 3."
        
        else:
            feedback = await self._generate_feedback(session, user_message)
            session.question_index += 1
            
            if session.question_index >= 5:
                session.current_section = InterviewSection.MENU
                session.question_index = 0
                response = f"{feedback}\\n\\nSection complete! " + await self.get_menu()
            else:
                next_q = await self._get_next_question(session)
                response = f"{feedback}\\n\\n---\\n\\n{next_q}"
        
        session.add_message("assistant", response)
        return {"response": response, "section": session.current_section.value, "question_index": session.question_index}
    
    async def _get_next_question(self, session: InterviewSession) -> str:
        if session.current_section == InterviewSection.SELF_INTRO:
            if session.question_index < len(self.SELF_INTRO_QUESTIONS):
                return self.SELF_INTRO_QUESTIONS[session.question_index]
            return "Tell me about your career goals."
        
        elif session.current_section == InterviewSection.TECHNICAL:
            context = await self.rag_service.get_technical_context(session.user_id)
            prompt = f"Based on: {context}\\n\\nGenerate ONE technical interview question. Return ONLY the question."
            return await self._call_llm(prompt)
        
        elif session.current_section == InterviewSection.SOFT_SKILL:
            context = await self.rag_service.get_soft_skills_context(session.user_id)
            prompt = f"Based on: {context}\\n\\nGenerate ONE behavioral STAR question. Return ONLY the question."
            return await self._call_llm(prompt)
        
        return "Tell me more about your experience."
    
    async def _generate_feedback(self, session: InterviewSession, answer: str) -> str:
        prompt = f"Give brief encouraging feedback (2 sentences) on this answer: {answer[:500]}"
        return await self._call_llm(prompt)
    
    async def _call_llm(self, prompt: str) -> str:
        if not self.groq_client:
            return "That's a great point. Can you elaborate?"
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional interview coach."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300, temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM error: {e}")
            return "That's interesting. Tell me more."
    
    def _is_ready(self, message: str) -> bool:
        ready = ["ready", "yes", "start", "begin", "ok", "okay", "sure"]
        return any(r in message.lower() for r in ready)
    
    def _parse_section_choice(self, message: str) -> Optional[InterviewSection]:
        msg = message.lower()
        if "1" in msg or "self" in msg or "intro" in msg:
            return InterviewSection.SELF_INTRO
        elif "2" in msg or "tech" in msg:
            return InterviewSection.TECHNICAL
        elif "3" in msg or "soft" in msg or "behavior" in msg:
            return InterviewSection.SOFT_SKILL
        return None
`,

  "services/feedback_service.py": `# services/feedback_service.py
"""
STAR Method Feedback Service for SmartSuccess.AI
"""

import os
import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter
from groq import AsyncGroq
import openai


@dataclass
class STARScore:
    situation: int = 0
    task: int = 0
    action: int = 0
    result: int = 0
    
    @property
    def average(self) -> float:
        scores = [self.situation, self.task, self.action, self.result]
        return sum(scores) / len(scores) if any(scores) else 0
    
    def to_dict(self) -> Dict:
        return {
            "situation": self.situation, "task": self.task,
            "action": self.action, "result": self.result,
            "average": round(self.average, 1)
        }


@dataclass
class DeliveryMetrics:
    filler_words: int = 0
    word_count: int = 0
    speaking_time_seconds: float = 0
    pacing: str = "good"
    
    def to_dict(self) -> Dict:
        return {
            "fillerWords": self.filler_words, "wordCount": self.word_count,
            "speakingTime": round(self.speaking_time_seconds, 1), "pacing": self.pacing
        }


@dataclass
class QuestionFeedback:
    question: str
    response: str
    timestamp: str
    active_listening_score: int = 0
    active_listening_insight: str = ""
    star_score: STARScore = field(default_factory=STARScore)
    star_insights: Dict[str, str] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    growth_areas: List[str] = field(default_factory=list)
    delivery: DeliveryMetrics = field(default_factory=DeliveryMetrics)
    
    def to_dict(self) -> Dict:
        return {
            "question": self.question, "response": self.response,
            "timestamp": self.timestamp,
            "activeListening": {"score": self.active_listening_score, "insight": self.active_listening_insight},
            "starScore": self.star_score.to_dict(),
            "starInsights": self.star_insights,
            "strengths": self.strengths, "growthAreas": self.growth_areas,
            "delivery": self.delivery.to_dict()
        }


@dataclass
class SessionFeedback:
    session_id: str
    user_id: str
    job_title: str = ""
    overall_score: float = 0.0
    questions_feedback: List[QuestionFeedback] = field(default_factory=list)
    aggregated_strengths: List[str] = field(default_factory=list)
    aggregated_growth_areas: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def calculate_overall_score(self) -> float:
        if not self.questions_feedback:
            return 0.0
        total = sum((qf.active_listening_score * 0.2) + (qf.star_score.average * 0.8) 
                    for qf in self.questions_feedback)
        avg = total / len(self.questions_feedback)
        self.overall_score = round((avg / 5) * 100, 1)
        return self.overall_score
    
    def to_dict(self) -> Dict:
        return {
            "sessionId": self.session_id, "userId": self.user_id,
            "jobTitle": self.job_title, "overallScore": self.overall_score,
            "questionsFeedback": [qf.to_dict() for qf in self.questions_feedback],
            "aggregatedStrengths": self.aggregated_strengths,
            "aggregatedGrowthAreas": self.aggregated_growth_areas,
            "createdAt": self.created_at
        }


class FeedbackService:
    FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "actually", "literally", "honestly"]
    
    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = AsyncGroq(api_key=groq_key) if groq_key else None
        openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = openai.AsyncOpenAI(api_key=openai_key) if openai_key else None
        self.session_feedback: Dict[str, SessionFeedback] = {}
    
    async def analyze_response(
        self, session_id: str, user_id: str, question: str,
        response: str, job_context: Optional[str] = None
    ) -> QuestionFeedback:
        feedback = QuestionFeedback(
            question=question, response=response,
            timestamp=datetime.now().isoformat()
        )
        feedback.delivery = self._analyze_delivery(response)
        ai_feedback = await self._get_ai_feedback(question, response, job_context)
        
        feedback.active_listening_score = ai_feedback.get("activeListening", {}).get("score", 3)
        feedback.active_listening_insight = ai_feedback.get("activeListening", {}).get("insight", "")
        feedback.star_score = STARScore(
            situation=ai_feedback.get("situation", {}).get("score", 3),
            task=ai_feedback.get("task", {}).get("score", 3),
            action=ai_feedback.get("action", {}).get("score", 3),
            result=ai_feedback.get("result", {}).get("score", 3)
        )
        feedback.star_insights = {k: ai_feedback.get(k, {}).get("insight", "") 
                                   for k in ["situation", "task", "action", "result"]}
        feedback.strengths = ai_feedback.get("strengths", [])
        feedback.growth_areas = ai_feedback.get("growthAreas", [])
        
        if session_id not in self.session_feedback:
            self.session_feedback[session_id] = SessionFeedback(session_id=session_id, user_id=user_id)
        self.session_feedback[session_id].questions_feedback.append(feedback)
        return feedback
    
    def _analyze_delivery(self, text: str) -> DeliveryMetrics:
        metrics = DeliveryMetrics()
        words = text.split()
        metrics.word_count = len(words)
        text_lower = text.lower()
        for filler in self.FILLER_WORDS:
            metrics.filler_words += text_lower.count(filler)
        metrics.speaking_time_seconds = (metrics.word_count / 150) * 60
        metrics.pacing = "too_brief" if metrics.word_count < 50 else "too_long" if metrics.word_count > 350 else "good"
        return metrics
    
    async def _get_ai_feedback(self, question: str, response: str, job_context: Optional[str] = None) -> Dict:
        ctx = f"JOB CONTEXT: {job_context}" if job_context else ""
        prompt = f'''Analyze this interview response. Rate 1-5 for each STAR category.
QUESTION: {question}
RESPONSE: {response}
{ctx}

Return JSON only:
{{"activeListening": {{"score": 3, "insight": "..."}}, "situation": {{"score": 3, "insight": "..."}}, "task": {{"score": 3, "insight": "..."}}, "action": {{"score": 3, "insight": "..."}}, "result": {{"score": 3, "insight": "..."}}, "strengths": ["...", "..."], "growthAreas": ["...", "..."]}}'''

        if self.groq_client:
            try:
                resp = await self.groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[{"role": "system", "content": "Return only valid JSON."},
                              {"role": "user", "content": prompt}],
                    max_tokens=500, temperature=0.3
                )
                return self._parse_json(resp.choices[0].message.content.strip())
            except Exception as e:
                print(f"Groq error: {e}")
        
        if self.openai_client:
            try:
                resp = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Return only valid JSON."},
                              {"role": "user", "content": prompt}],
                    max_tokens=500, temperature=0.3
                )
                return self._parse_json(resp.choices[0].message.content.strip())
            except Exception as e:
                print(f"OpenAI error: {e}")
        
        return self._default_feedback()
    
    def _parse_json(self, text: str) -> Dict:
        try:
            text = re.sub(r'^[\\s\\S]*?\\{', '{', text, count=1)
            text = re.sub(r'\\}[\\s\\S]*$', '}', text, count=1)
            return json.loads(text)
        except:
            return self._default_feedback()
    
    def _default_feedback(self) -> Dict:
        return {
            "activeListening": {"score": 3, "insight": "Response noted."},
            "situation": {"score": 3, "insight": "Context provided."},
            "task": {"score": 3, "insight": "Role explained."},
            "action": {"score": 3, "insight": "Actions described."},
            "result": {"score": 3, "insight": "Outcomes mentioned."},
            "strengths": ["Clear communication", "Relevant example"],
            "growthAreas": ["Add specifics", "Quantify results"]
        }
    
    def get_session_summary(self, session_id: str) -> Optional[SessionFeedback]:
        if session_id not in self.session_feedback:
            return None
        session = self.session_feedback[session_id]
        session.calculate_overall_score()
        all_strengths = [s for qf in session.questions_feedback for s in qf.strengths]
        all_growth = [g for qf in session.questions_feedback for g in qf.growth_areas]
        session.aggregated_strengths = [i for i, _ in Counter(all_strengths).most_common(3)]
        session.aggregated_growth_areas = [i for i, _ in Counter(all_growth).most_common(3)]
        return session
`,

  "models/__init__.py": `# models/__init__.py
"""Pydantic models for SmartSuccess.AI API"""

from .schemas import (
    BuildContextRequest, BuildContextResponse,
    InterviewStartResponse, InterviewMessageRequest,
    InterviewMessageResponse, FeedbackResponse
)

__all__ = [
    "BuildContextRequest", "BuildContextResponse",
    "InterviewStartResponse", "InterviewMessageRequest",
    "InterviewMessageResponse", "FeedbackResponse"
]
`,

  "models/schemas.py": `# models/schemas.py
"""Pydantic schemas for API request/response validation"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class BuildContextRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    job_text: str = Field(..., description="Job posting text")


class BuildContextResponse(BaseModel):
    status: str
    message: str
    details: Dict


class InterviewStartResponse(BaseModel):
    session_id: str
    message: str
    section: str


class InterviewMessageRequest(BaseModel):
    session_id: str
    message: str


class STARScoreSchema(BaseModel):
    situation: int = Field(ge=1, le=5)
    task: int = Field(ge=1, le=5)
    action: int = Field(ge=1, le=5)
    result: int = Field(ge=1, le=5)
    average: float


class DeliveryMetricsSchema(BaseModel):
    fillerWords: int
    wordCount: int
    speakingTime: float
    pacing: str


class QuestionFeedbackSchema(BaseModel):
    question: str
    response: str
    timestamp: str
    activeListening: Dict
    starScore: STARScoreSchema
    strengths: List[str]
    growthAreas: List[str]
    delivery: DeliveryMetricsSchema


class InterviewMessageResponse(BaseModel):
    response: str
    section: str
    question_index: Optional[int] = None
    is_complete: bool = False
    feedback: Optional[QuestionFeedbackSchema] = None


class FeedbackResponse(BaseModel):
    sessionId: str
    userId: str
    overallScore: float
    questionsFeedback: List[QuestionFeedbackSchema]
    aggregatedStrengths: List[str]
    aggregatedGrowthAreas: List[str]
`,

  "prompts/__init__.py": `# prompts/__init__.py
"""Prompt templates for SmartSuccess.AI"""

from .interview_prompts import SELF_INTRO_QUESTIONS, STAR_ANALYSIS_PROMPT

__all__ = ["SELF_INTRO_QUESTIONS", "STAR_ANALYSIS_PROMPT"]
`,

  "prompts/interview_prompts.py": `# prompts/interview_prompts.py
"""Prompt templates for interview question generation and feedback"""

SELF_INTRO_QUESTIONS = [
    "Please introduce yourself and give me a brief overview of your professional background.",
    "What interests you about this particular role and our company?",
    "Why are you looking to make a change from your current position?",
    "What makes you the ideal candidate for this position?",
    "What are your greatest professional strengths, and what areas are you working to improve?"
]

TECHNICAL_QUESTION_PROMPT = """Based on this candidate's background and job requirements:

{context}

Generate ONE specific technical interview question that:
1. References a specific skill from their background
2. Relates to the job requirements
3. Asks about challenges or practical application

Question #{question_number} of 5.
Return ONLY the question, no preamble."""

SOFT_SKILL_QUESTION_PROMPT = """Based on this job context:

{context}

Generate ONE behavioral STAR question about: teamwork, communication, or problem-solving.

Question #{question_number} of 5.
Start with "Tell me about a time when..." or "Describe a situation where..."
Return ONLY the question."""

STAR_ANALYSIS_PROMPT = """Analyze this interview response using STAR method.

QUESTION: {question}
RESPONSE: {response}

Rate 1-5 for: activeListening, situation, task, action, result
Identify 2 strengths and 2 growth areas.

Return valid JSON only."""
`,

  "requirements_additions.txt": `# Add these to your existing requirements.txt

# Vector Store & Embeddings
chromadb>=0.4.0

# Fast LLM for real-time interview
groq>=0.4.0

# Your existing deps (keep these):
# fastapi, uvicorn, python-multipart
# requests, beautifulsoup4, PyPDF2
# python-docx, aiohttp, openai>=1.0.0
# stripe, firebase-admin, python-dotenv
`
};

export default function ServicesPackage() {
  const [selectedFile, setSelectedFile] = useState("services/__init__.py");
  const [copied, setCopied] = useState("");

  const copyToClipboard = (filename, content) => {
    navigator.clipboard.writeText(content);
    setCopied(filename);
    setTimeout(() => setCopied(""), 2000);
  };

  const downloadAll = () => {
    const content = Object.entries(files)
      .map(([name, code]) => `${"=".repeat(60)}\n// FILE: ${name}\n${"=".repeat(60)}\n\n${code}`)
      .join("\n\n\n");
    
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "smartsuccess-services-package.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  const fileList = Object.keys(files);
  
  const getIcon = (name) => {
    if (name.includes("__init__")) return "📦";
    if (name.includes("service")) return "⚙️";
    if (name.includes("schema")) return "📋";
    if (name.includes("prompt")) return "💬";
    if (name.includes("requirements")) return "📝";
    return "📄";
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 text-gray-100 rounded-lg overflow-hidden">
      <div className="bg-gray-800 px-4 py-3 border-b border-gray-700 flex justify-between items-center">
        <div>
          <h1 className="text-lg font-bold text-blue-400">SmartSuccess.AI Services</h1>
          <p className="text-sm text-gray-400">{fileList.length} files</p>
        </div>
        <button onClick={downloadAll} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium">
          📥 Download All
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <div className="w-56 bg-gray-850 border-r border-gray-700 overflow-y-auto p-2">
          {fileList.map((f) => (
            <button
              key={f}
              onClick={() => setSelectedFile(f)}
              className={`w-full text-left px-3 py-2 rounded text-sm flex items-center gap-2 mb-1 ${
                selectedFile === f ? "bg-blue-600" : "hover:bg-gray-700"
              }`}
            >
              <span>{getIcon(f)}</span>
              <span className="truncate">{f.split("/").pop()}</span>
            </button>
          ))}
        </div>

        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex justify-between items-center">
            <span className="text-sm font-mono text-gray-300">{selectedFile}</span>
            <button
              onClick={() => copyToClipboard(selectedFile, files[selectedFile])}
              className={`px-3 py-1 rounded text-sm ${
                copied === selectedFile ? "bg-green-600" : "bg-gray-700 hover:bg-gray-600"
              }`}
            >
              {copied === selectedFile ? "✓ Copied!" : "📋 Copy"}
            </button>
          </div>
          <div className="flex-1 overflow-auto p-4">
            <pre className="text-sm font-mono text-gray-300 whitespace-pre-wrap">{files[selectedFile]}</pre>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 px-4 py-2 border-t border-gray-700 text-sm text-gray-400">
        Create folders: <code className="bg-gray-700 px-1 rounded">services/</code>{" "}
        <code className="bg-gray-700 px-1 rounded">models/</code>{" "}
        <code className="bg-gray-700 px-1 rounded">prompts/</code> in resume-matcher-backend/
      </div>
    </div>
  );
}
