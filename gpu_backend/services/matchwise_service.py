"""
SmartSuccess.AI GPU Backend - MatchWise Integration Service
One-way data flow: MatchWise.ai → SmartSuccess.AI Personalized RAG
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
import json
import os
import logging
import time
import asyncio
import aiohttp
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import hashlib
import re

from config import get_settings, get_model_config, get_data_path
from models.schemas import (
    InterviewQuestion,
    InterviewCategory,
    InterviewDifficulty,
    MatchWiseAnalysisData,
    PersonalizedRAGRequest,
    PersonalizedRAGResponse,
    PersonalizedQuestionRequest
)
from services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


# Question templates for generating personalized questions
QUESTION_TEMPLATES = {
    InterviewCategory.TECHNICAL: [
        "Can you explain your experience with {skill}?",
        "How have you applied {skill} in your previous projects?",
        "What challenges have you faced when working with {skill}?",
        "Describe a project where you used {skill} to solve a complex problem.",
        "How would you approach improving {skill} implementation in a production environment?",
        "What are the key considerations when using {skill} for {domain}?",
        "Can you walk me through your approach to debugging {skill}-related issues?",
        "How do you stay updated with the latest developments in {skill}?",
    ],
    InterviewCategory.BEHAVIORAL: [
        "Tell me about a time when you had to learn {skill} quickly for a project.",
        "Describe a situation where your knowledge of {skill} made a significant impact.",
        "How did you handle a challenge related to {skill} in your work at {company}?",
        "Give an example of when you collaborated with others on a {skill} project.",
        "Tell me about a time when you had to explain {skill} to non-technical stakeholders.",
    ],
    InterviewCategory.SCENARIO: [
        "If you were tasked with implementing {skill} from scratch, how would you approach it?",
        "Your team is facing performance issues with {skill}. How would you diagnose and fix this?",
        "A client wants to use {skill} for a use case you think is inappropriate. How do you handle this?",
        "You need to choose between {skill} and an alternative approach. What factors do you consider?",
    ],
    InterviewCategory.SOFT_SKILLS: [
        "How do you prioritize learning new skills like {skill} alongside your regular work?",
        "Describe how you would mentor a junior developer on {skill}.",
        "How do you handle disagreements about technical approaches when using {skill}?",
    ]
}

# Gap-focused question templates
GAP_QUESTION_TEMPLATES = [
    "The job requires {gap}. While this may not be your primary experience, how would you approach learning it?",
    "Tell me about any exposure you've had to {gap}, even in a limited capacity.",
    "How would you bridge the gap in {gap} to meet the role's requirements?",
    "If you were to work on a project involving {gap}, what would be your learning strategy?",
    "What transferable skills from your experience could help you succeed with {gap}?",
]


class MatchWiseIntegrationService:
    """
    Service for integrating MatchWise.ai analysis data into SmartSuccess.AI
    
    Features:
    - Receives analysis data from MatchWise.ai via iframe postMessage
    - Builds personalized RAG from resume and job analysis
    - Generates targeted interview questions based on:
      - User's strengths (to showcase)
      - User's gaps (to prepare for)
      - Job requirements (to target)
    - GPU-accelerated embedding and retrieval
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.model_config = get_model_config()
        self.embedding_service = get_embedding_service()
        self.chroma_client: Optional[chromadb.Client] = None
        self.user_collections: Dict[str, Any] = {}
        
        # Initialize ChromaDB for user RAGs
        self._initialize_chroma()
        
        logger.info("MatchWiseIntegrationService initialized")
    
    def _initialize_chroma(self):
        """Initialize ChromaDB for user-specific RAGs"""
        try:
            persist_dir = get_data_path("user_rag/chroma")
            os.makedirs(persist_dir, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            logger.info("User RAG ChromaDB initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
    
    async def build_personalized_rag(
        self,
        request: PersonalizedRAGRequest
    ) -> PersonalizedRAGResponse:
        """
        Build personalized RAG from MatchWise analysis data
        
        Args:
            request: Contains user_id, matchwise_data, and preferences
            
        Returns:
            PersonalizedRAGResponse with rag_id and stats
        """
        start_time = time.time()
        matchwise_data = request.matchwise_data
        
        try:
            # Generate unique RAG ID
            rag_id = self._generate_rag_id(request.user_id)
            
            # Extract structured information
            resume_info = self._extract_resume_info(matchwise_data.resume_text)
            job_info = self._extract_job_info(matchwise_data.job_description)
            
            # Generate personalized questions
            questions = await self._generate_personalized_questions(
                resume_info=resume_info,
                job_info=job_info,
                matchwise_data=matchwise_data,
                focus_categories=request.focus_categories,
                difficulty=request.difficulty_preference,
                num_questions=request.num_questions
            )
            
            # Create ChromaDB collection for this user
            collection = self._create_user_collection(rag_id, questions)
            
            # Calculate covered categories
            categories_covered = list(set(q.category for q in questions))
            
            # Extract focus areas
            focus_areas = list(set(
                matchwise_data.strengths[:3] + 
                matchwise_data.gaps[:2] + 
                matchwise_data.keywords_matched[:3]
            ))
            
            build_time = time.time() - start_time
            logger.info(f"Built personalized RAG {rag_id} in {build_time:.2f}s with {len(questions)} questions")
            
            return PersonalizedRAGResponse(
                rag_id=rag_id,
                user_id=request.user_id,
                status="ready",
                question_bank_size=len(questions),
                categories_covered=categories_covered,
                focus_areas=focus_areas,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=7)  # 7-day expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to build personalized RAG: {e}")
            raise
    
    def _generate_rag_id(self, user_id: str) -> str:
        """Generate unique RAG ID"""
        timestamp = int(time.time())
        unique_string = f"{user_id}_{timestamp}"
        hash_suffix = hashlib.md5(unique_string.encode()).hexdigest()[:8]
        return f"rag_{user_id}_{hash_suffix}"
    
    def _extract_resume_info(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured information from resume text"""
        # Basic extraction - in production, could use LLM for better extraction
        info = {
            "skills": [],
            "experience": [],
            "education": [],
            "projects": [],
            "companies": []
        }
        
        # Extract skills (simple pattern matching)
        skill_patterns = [
            r"(?:skills?|technologies?|tools?)[\s:]+([^\n]+)",
            r"(?:proficient in|experienced with|expertise in)[\s:]+([^\n]+)",
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                skills = [s.strip() for s in re.split(r'[,;|]', match) if s.strip()]
                info["skills"].extend(skills)
        
        # Extract company names (simple pattern)
        company_patterns = [
            r"(?:at|@|worked at|employed by)\s+([A-Z][A-Za-z\s]+(?:Inc|Corp|LLC|Ltd)?)",
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, resume_text)
            info["companies"].extend(matches)
        
        # Deduplicate
        info["skills"] = list(set(info["skills"]))[:20]
        info["companies"] = list(set(info["companies"]))[:5]
        
        return info
    
    def _extract_job_info(self, job_description: str) -> Dict[str, Any]:
        """Extract structured information from job description"""
        info = {
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": []
        }
        
        # Extract required skills
        required_patterns = [
            r"(?:required|must have|essential)[\s:]+([^\n]+)",
            r"requirements?[\s:]+([^\n]+)",
        ]
        
        for pattern in required_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            for match in matches:
                skills = [s.strip() for s in re.split(r'[,;|]', match) if s.strip()]
                info["required_skills"].extend(skills)
        
        # Extract preferred skills
        preferred_patterns = [
            r"(?:preferred|nice to have|bonus)[\s:]+([^\n]+)",
        ]
        
        for pattern in preferred_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            for match in matches:
                skills = [s.strip() for s in re.split(r'[,;|]', match) if s.strip()]
                info["preferred_skills"].extend(skills)
        
        # Deduplicate
        info["required_skills"] = list(set(info["required_skills"]))[:15]
        info["preferred_skills"] = list(set(info["preferred_skills"]))[:10]
        
        return info
    
    async def _generate_personalized_questions(
        self,
        resume_info: Dict[str, Any],
        job_info: Dict[str, Any],
        matchwise_data: MatchWiseAnalysisData,
        focus_categories: Optional[List[InterviewCategory]],
        difficulty: InterviewDifficulty,
        num_questions: int
    ) -> List[InterviewQuestion]:
        """Generate personalized interview questions"""
        questions = []
        
        # Determine categories to cover
        if focus_categories:
            categories = focus_categories
        else:
            categories = [
                InterviewCategory.TECHNICAL,
                InterviewCategory.BEHAVIORAL,
                InterviewCategory.SCENARIO,
                InterviewCategory.SOFT_SKILLS
            ]
        
        # Calculate questions per category
        base_per_category = num_questions // len(categories)
        
        # Generate strength-based questions (40%)
        strength_count = int(num_questions * 0.4)
        for i, strength in enumerate(matchwise_data.strengths[:strength_count]):
            category = categories[i % len(categories)]
            templates = QUESTION_TEMPLATES.get(category, [])
            
            if templates:
                template = templates[i % len(templates)]
                question_text = template.format(
                    skill=strength,
                    domain="AI/ML",
                    company=resume_info["companies"][0] if resume_info["companies"] else "your previous role"
                )
                
                questions.append(InterviewQuestion(
                    id=f"strength_{i}",
                    question=question_text,
                    category=category,
                    subcategory="strength_showcase",
                    difficulty=difficulty,
                    tags=[strength.lower().replace(" ", "_"), "strength"],
                    evaluation_criteria=[
                        f"Demonstrates expertise in {strength}",
                        "Provides concrete examples",
                        "Shows depth of knowledge"
                    ]
                ))
        
        # Generate gap-focused questions (30%)
        gap_count = int(num_questions * 0.3)
        for i, gap in enumerate(matchwise_data.gaps[:gap_count]):
            template = GAP_QUESTION_TEMPLATES[i % len(GAP_QUESTION_TEMPLATES)]
            question_text = template.format(gap=gap)
            
            questions.append(InterviewQuestion(
                id=f"gap_{i}",
                question=question_text,
                category=InterviewCategory.BEHAVIORAL if i % 2 == 0 else InterviewCategory.SCENARIO,
                subcategory="gap_preparation",
                difficulty=InterviewDifficulty.MEDIUM,
                tags=[gap.lower().replace(" ", "_"), "gap", "growth"],
                evaluation_criteria=[
                    "Acknowledges the gap honestly",
                    "Shows willingness to learn",
                    "Identifies transferable skills"
                ]
            ))
        
        # Generate skill-match questions (30%)
        skill_count = int(num_questions * 0.3)
        matched_skills = matchwise_data.keywords_matched[:skill_count]
        
        for i, skill in enumerate(matched_skills):
            category = categories[i % len(categories)]
            templates = QUESTION_TEMPLATES.get(category, [])
            
            if templates:
                template = templates[(i + 2) % len(templates)]
                question_text = template.format(
                    skill=skill,
                    domain="AI/ML engineering",
                    company=resume_info["companies"][0] if resume_info["companies"] else "your experience"
                )
                
                questions.append(InterviewQuestion(
                    id=f"skill_{i}",
                    question=question_text,
                    category=category,
                    subcategory="skill_demonstration",
                    difficulty=difficulty,
                    tags=[skill.lower().replace(" ", "_"), "matched_skill"],
                    evaluation_criteria=[
                        f"Shows practical experience with {skill}",
                        "Connects to job requirements",
                        "Demonstrates impact"
                    ]
                ))
        
        # Ensure we have the requested number of questions
        while len(questions) < num_questions:
            # Add generic questions if needed
            questions.append(InterviewQuestion(
                id=f"generic_{len(questions)}",
                question=f"How would you contribute to our team given your background in {resume_info['skills'][0] if resume_info['skills'] else 'AI/ML'}?",
                category=InterviewCategory.BEHAVIORAL,
                subcategory="general",
                difficulty=difficulty,
                tags=["general", "contribution"],
                evaluation_criteria=["Shows enthusiasm", "Identifies value-add", "Team orientation"]
            ))
        
        return questions[:num_questions]
    
    def _create_user_collection(
        self,
        rag_id: str,
        questions: List[InterviewQuestion]
    ) -> Any:
        """Create ChromaDB collection for user's personalized questions"""
        # Delete existing collection if exists
        try:
            self.chroma_client.delete_collection(rag_id)
        except:
            pass
        
        # Create new collection
        collection = self.chroma_client.create_collection(
            name=rag_id,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Generate embeddings for questions
        question_texts = [q.question for q in questions]
        embeddings = self.embedding_service.encode_documents(
            question_texts,
            show_progress=False
        )
        
        # Add to collection
        collection.add(
            ids=[q.id for q in questions],
            embeddings=embeddings.tolist(),
            documents=question_texts,
            metadatas=[{
                "category": q.category.value,
                "subcategory": q.subcategory or "general",
                "difficulty": q.difficulty.value,
                "tags": ",".join(q.tags),
                "evaluation_criteria": ",".join(q.evaluation_criteria or [])
            } for q in questions]
        )
        
        self.user_collections[rag_id] = collection
        return collection
    
    def get_personalized_question(
        self,
        request: PersonalizedQuestionRequest
    ) -> Optional[InterviewQuestion]:
        """Get a personalized question from user's RAG"""
        collection = self.user_collections.get(request.rag_id)
        
        if not collection:
            # Try to load from disk
            try:
                collection = self.chroma_client.get_collection(request.rag_id)
                self.user_collections[request.rag_id] = collection
            except:
                logger.error(f"Collection not found: {request.rag_id}")
                return None
        
        # Build where clause
        where_clause = {}
        if request.category:
            where_clause["category"] = request.category.value
        if request.difficulty:
            where_clause["difficulty"] = request.difficulty.value
        
        # Get questions
        try:
            results = collection.get(
                where=where_clause if where_clause else None,
                include=["documents", "metadatas"]
            )
            
            if not results["ids"]:
                return None
            
            # Filter out excluded IDs
            available = [
                (id, doc, meta) for id, doc, meta in zip(
                    results["ids"],
                    results["documents"],
                    results["metadatas"]
                )
                if id not in request.exclude_ids
            ]
            
            if not available:
                return None
            
            # Select random
            import random
            q_id, doc, metadata = random.choice(available)
            
            return InterviewQuestion(
                id=q_id,
                question=doc,
                category=InterviewCategory(metadata["category"]),
                subcategory=metadata.get("subcategory"),
                difficulty=InterviewDifficulty(metadata.get("difficulty", "medium")),
                tags=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
                evaluation_criteria=metadata.get("evaluation_criteria", "").split(",") if metadata.get("evaluation_criteria") else None
            )
            
        except Exception as e:
            logger.error(f"Failed to get personalized question: {e}")
            return None
    
    def query_personalized_rag(
        self,
        rag_id: str,
        query: str,
        n_results: int = 5
    ) -> List[InterviewQuestion]:
        """Query user's personalized RAG"""
        collection = self.user_collections.get(rag_id)
        
        if not collection:
            try:
                collection = self.chroma_client.get_collection(rag_id)
                self.user_collections[rag_id] = collection
            except:
                logger.error(f"Collection not found: {rag_id}")
                return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.encode_query(query)
            
            # Query collection
            results = collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            questions = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                
                questions.append(InterviewQuestion(
                    id=results["ids"][0][i],
                    question=doc,
                    category=InterviewCategory(metadata["category"]),
                    subcategory=metadata.get("subcategory"),
                    difficulty=InterviewDifficulty(metadata.get("difficulty", "medium")),
                    tags=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
                    evaluation_criteria=metadata.get("evaluation_criteria", "").split(",") if metadata.get("evaluation_criteria") else None,
                    relevance_score=1 - distance
                ))
            
            return questions
            
        except Exception as e:
            logger.error(f"Failed to query personalized RAG: {e}")
            return []
    
    def delete_user_rag(self, rag_id: str) -> bool:
        """Delete a user's personalized RAG"""
        try:
            self.chroma_client.delete_collection(rag_id)
            if rag_id in self.user_collections:
                del self.user_collections[rag_id]
            logger.info(f"Deleted user RAG: {rag_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete RAG {rag_id}: {e}")
            return False
    
    def get_rag_info(self, rag_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a user's RAG"""
        try:
            collection = self.chroma_client.get_collection(rag_id)
            return {
                "rag_id": rag_id,
                "question_count": collection.count(),
                "metadata": collection.metadata
            }
        except:
            return None


# Singleton accessor
_service_instance: Optional[MatchWiseIntegrationService] = None

def get_matchwise_service() -> MatchWiseIntegrationService:
    """Get the MatchWise integration service singleton"""
    global _service_instance
    if _service_instance is None:
        _service_instance = MatchWiseIntegrationService()
    return _service_instance
