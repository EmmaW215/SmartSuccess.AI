"""
SmartSuccess.AI GPU Backend - Pre-RAG Service
Pre-trained general interview question bank for users without resumes
Focused on Tech/AI, AI Engineering, AIOps, AI Product Management domains
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
import json
import os
import logging
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
import hashlib

from config import get_settings, get_model_config, get_data_path
from models.schemas import (
    InterviewQuestion,
    InterviewCategory,
    InterviewDifficulty,
    RAGQueryRequest,
    RAGQueryResponse,
    QuestionBankStats
)
from services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


# Pre-built question bank data for Tech/AI domain
PREBUILT_QUESTIONS = {
    InterviewCategory.SELF_INTRODUCTION: [
        {
            "question": "Tell me about yourself and your journey into AI/ML engineering.",
            "difficulty": "easy",
            "subcategory": "career_journey",
            "tags": ["ai_engineering", "career", "introduction"],
            "sample_answer": "Structure your answer: Current role → Past experience → Why AI/ML → What excites you about this opportunity",
            "evaluation_criteria": ["Clear narrative", "Relevant experience", "Passion for AI", "Concise delivery"]
        },
        {
            "question": "Walk me through a challenging AI project you've worked on and your role in it.",
            "difficulty": "medium",
            "subcategory": "project_experience",
            "tags": ["ai_engineering", "project", "technical"],
            "sample_answer": "Use STAR method: Describe the project context, your specific contributions, technical challenges, and measurable outcomes.",
            "evaluation_criteria": ["Technical depth", "Problem-solving", "Collaboration", "Results-oriented"]
        },
        {
            "question": "What motivated you to transition into AI engineering, and how have you prepared for this role?",
            "difficulty": "medium",
            "subcategory": "career_transition",
            "tags": ["career_change", "motivation", "preparation"],
            "sample_answer": "Share your journey authentically, highlighting specific learning paths, projects, and skills developed.",
            "evaluation_criteria": ["Genuine motivation", "Learning initiative", "Skill development", "Career clarity"]
        },
        {
            "question": "How do you stay current with the rapidly evolving AI landscape?",
            "difficulty": "easy",
            "subcategory": "continuous_learning",
            "tags": ["learning", "industry_awareness", "growth"],
            "sample_answer": "Mention specific resources: papers (arXiv), courses, communities, conferences, hands-on experimentation.",
            "evaluation_criteria": ["Learning habits", "Industry awareness", "Practical application", "Community involvement"]
        },
        {
            "question": "Describe your experience with production ML systems. What challenges have you faced?",
            "difficulty": "hard",
            "subcategory": "production_experience",
            "tags": ["mlops", "production", "challenges"],
            "sample_answer": "Discuss deployment challenges, monitoring, model drift, scaling issues, and how you addressed them.",
            "evaluation_criteria": ["Production experience", "Problem-solving", "Technical depth", "Operational awareness"]
        }
    ],
    
    InterviewCategory.TECHNICAL: [
        # AI/ML Fundamentals
        {
            "question": "Explain the difference between supervised, unsupervised, and reinforcement learning with real-world examples.",
            "difficulty": "easy",
            "subcategory": "ml_fundamentals",
            "tags": ["machine_learning", "fundamentals", "theory"],
            "evaluation_criteria": ["Clear explanations", "Relevant examples", "Technical accuracy"]
        },
        {
            "question": "What is the transformer architecture and why has it been so successful in NLP and beyond?",
            "difficulty": "medium",
            "subcategory": "deep_learning",
            "tags": ["transformers", "attention", "nlp", "architecture"],
            "evaluation_criteria": ["Understanding of attention mechanism", "Historical context", "Applications"]
        },
        {
            "question": "Explain the concept of RAG (Retrieval-Augmented Generation) and how you would implement it.",
            "difficulty": "medium",
            "subcategory": "llm_applications",
            "tags": ["rag", "llm", "embeddings", "vector_db"],
            "evaluation_criteria": ["RAG architecture understanding", "Component knowledge", "Implementation approach"]
        },
        {
            "question": "How would you fine-tune a large language model for a specific domain? Discuss the approaches and trade-offs.",
            "difficulty": "hard",
            "subcategory": "llm_training",
            "tags": ["fine_tuning", "llm", "peft", "lora"],
            "evaluation_criteria": ["Fine-tuning methods knowledge", "Resource considerations", "Data requirements"]
        },
        {
            "question": "Describe the differences between BERT, GPT, and T5 architectures. When would you use each?",
            "difficulty": "medium",
            "subcategory": "model_architectures",
            "tags": ["bert", "gpt", "t5", "transformers"],
            "evaluation_criteria": ["Architecture knowledge", "Use case understanding", "Trade-offs"]
        },
        # MLOps / AI Engineering
        {
            "question": "How would you design a CI/CD pipeline for machine learning models?",
            "difficulty": "medium",
            "subcategory": "mlops",
            "tags": ["cicd", "mlops", "deployment", "automation"],
            "evaluation_criteria": ["Pipeline components", "Testing strategies", "Automation approach"]
        },
        {
            "question": "Explain model drift and how you would detect and handle it in production.",
            "difficulty": "hard",
            "subcategory": "mlops",
            "tags": ["model_drift", "monitoring", "production"],
            "evaluation_criteria": ["Drift types understanding", "Detection methods", "Mitigation strategies"]
        },
        {
            "question": "How would you implement A/B testing for ML models in production?",
            "difficulty": "medium",
            "subcategory": "experimentation",
            "tags": ["ab_testing", "production", "experimentation"],
            "evaluation_criteria": ["Experimental design", "Statistical rigor", "Implementation approach"]
        },
        {
            "question": "Describe your experience with containerization (Docker) and orchestration (Kubernetes) for ML workloads.",
            "difficulty": "medium",
            "subcategory": "infrastructure",
            "tags": ["docker", "kubernetes", "infrastructure", "deployment"],
            "evaluation_criteria": ["Container knowledge", "Orchestration understanding", "ML-specific considerations"]
        },
        {
            "question": "How would you design a feature store? What are the key components and considerations?",
            "difficulty": "hard",
            "subcategory": "mlops",
            "tags": ["feature_store", "data_engineering", "mlops"],
            "evaluation_criteria": ["Feature store components", "Online vs offline", "Data consistency"]
        },
        # AI Product / Systems
        {
            "question": "How would you estimate the infrastructure costs for deploying a large language model?",
            "difficulty": "hard",
            "subcategory": "ai_systems",
            "tags": ["cost_estimation", "infrastructure", "llm_deployment"],
            "evaluation_criteria": ["Cost factors understanding", "Estimation approach", "Optimization strategies"]
        },
        {
            "question": "Design an AI-powered recommendation system. Walk me through your approach.",
            "difficulty": "hard",
            "subcategory": "system_design",
            "tags": ["recommendation_system", "system_design", "ai_product"],
            "evaluation_criteria": ["System architecture", "Algorithm choices", "Scalability", "Evaluation metrics"]
        },
        {
            "question": "How would you handle bias in machine learning models? Discuss detection and mitigation.",
            "difficulty": "hard",
            "subcategory": "ai_ethics",
            "tags": ["bias", "fairness", "ethics", "responsible_ai"],
            "evaluation_criteria": ["Bias types understanding", "Detection methods", "Mitigation approaches"]
        },
        {
            "question": "Explain how you would optimize inference latency for a production ML model.",
            "difficulty": "hard",
            "subcategory": "optimization",
            "tags": ["inference", "optimization", "latency", "production"],
            "evaluation_criteria": ["Optimization techniques", "Trade-offs", "Practical experience"]
        },
        {
            "question": "What are the key considerations when choosing between open-source and proprietary AI models?",
            "difficulty": "medium",
            "subcategory": "ai_strategy",
            "tags": ["open_source", "proprietary", "ai_strategy", "decision_making"],
            "evaluation_criteria": ["Cost considerations", "Control vs convenience", "Use case matching"]
        }
    ],
    
    InterviewCategory.BEHAVIORAL: [
        {
            "question": "Tell me about a time when you had to explain a complex AI concept to non-technical stakeholders.",
            "difficulty": "medium",
            "subcategory": "communication",
            "tags": ["communication", "stakeholder_management", "technical_translation"],
            "evaluation_criteria": ["Clarity of explanation", "Audience awareness", "Outcome"]
        },
        {
            "question": "Describe a situation where an ML project didn't go as planned. How did you handle it?",
            "difficulty": "medium",
            "subcategory": "failure_handling",
            "tags": ["failure", "problem_solving", "resilience"],
            "evaluation_criteria": ["Self-awareness", "Problem-solving", "Learning mindset"]
        },
        {
            "question": "Tell me about a time when you had to make a decision with incomplete data.",
            "difficulty": "medium",
            "subcategory": "decision_making",
            "tags": ["decision_making", "uncertainty", "judgment"],
            "evaluation_criteria": ["Decision process", "Risk assessment", "Outcome handling"]
        },
        {
            "question": "Describe a situation where you disagreed with a technical approach. How did you handle it?",
            "difficulty": "medium",
            "subcategory": "conflict_resolution",
            "tags": ["conflict", "technical_discussion", "collaboration"],
            "evaluation_criteria": ["Professionalism", "Communication", "Resolution approach"]
        },
        {
            "question": "Tell me about your most successful AI project. What made it successful?",
            "difficulty": "easy",
            "subcategory": "success_story",
            "tags": ["success", "achievement", "impact"],
            "evaluation_criteria": ["Impact demonstration", "Role clarity", "Success factors"]
        },
        {
            "question": "Describe a time when you had to learn a new technology quickly to meet a deadline.",
            "difficulty": "medium",
            "subcategory": "learning_agility",
            "tags": ["learning", "adaptability", "time_pressure"],
            "evaluation_criteria": ["Learning approach", "Resource utilization", "Outcome"]
        },
        {
            "question": "Tell me about a time when you improved an existing ML system or process.",
            "difficulty": "medium",
            "subcategory": "improvement",
            "tags": ["optimization", "initiative", "improvement"],
            "evaluation_criteria": ["Problem identification", "Solution approach", "Measurable impact"]
        },
        {
            "question": "Describe a situation where you had to balance speed and quality in an AI project.",
            "difficulty": "hard",
            "subcategory": "trade_offs",
            "tags": ["trade_offs", "prioritization", "judgment"],
            "evaluation_criteria": ["Trade-off analysis", "Decision rationale", "Outcome management"]
        }
    ],
    
    InterviewCategory.SOFT_SKILLS: [
        {
            "question": "How do you prioritize tasks when working on multiple AI projects simultaneously?",
            "difficulty": "medium",
            "subcategory": "time_management",
            "tags": ["prioritization", "time_management", "organization"],
            "evaluation_criteria": ["Framework usage", "Practical examples", "Flexibility"]
        },
        {
            "question": "How do you approach mentoring junior engineers in AI/ML concepts?",
            "difficulty": "medium",
            "subcategory": "mentoring",
            "tags": ["mentoring", "leadership", "teaching"],
            "evaluation_criteria": ["Teaching approach", "Patience", "Knowledge sharing"]
        },
        {
            "question": "How do you handle feedback on your AI models or technical decisions?",
            "difficulty": "easy",
            "subcategory": "feedback",
            "tags": ["feedback", "growth", "collaboration"],
            "evaluation_criteria": ["Openness to feedback", "Growth mindset", "Action orientation"]
        },
        {
            "question": "Describe your approach to collaborating with cross-functional teams (product, design, data).",
            "difficulty": "medium",
            "subcategory": "collaboration",
            "tags": ["collaboration", "cross_functional", "teamwork"],
            "evaluation_criteria": ["Communication style", "Empathy", "Problem-solving"]
        },
        {
            "question": "How do you manage stakeholder expectations for AI projects with uncertain outcomes?",
            "difficulty": "hard",
            "subcategory": "stakeholder_management",
            "tags": ["stakeholder_management", "communication", "expectations"],
            "evaluation_criteria": ["Transparency", "Communication skills", "Risk management"]
        }
    ],
    
    InterviewCategory.SCENARIO: [
        {
            "question": "Your production ML model's performance has dropped 15% overnight. Walk me through how you would diagnose and fix this.",
            "difficulty": "hard",
            "subcategory": "troubleshooting",
            "tags": ["debugging", "production", "incident_response"],
            "evaluation_criteria": ["Systematic approach", "Root cause analysis", "Solution implementation"]
        },
        {
            "question": "A business stakeholder wants to deploy an AI model that you believe is not ready. How do you handle this?",
            "difficulty": "hard",
            "subcategory": "stakeholder_conflict",
            "tags": ["stakeholder_management", "ethics", "communication"],
            "evaluation_criteria": ["Communication approach", "Risk articulation", "Alternative solutions"]
        },
        {
            "question": "You're tasked with reducing inference costs by 50% without significantly impacting model quality. What's your approach?",
            "difficulty": "hard",
            "subcategory": "optimization",
            "tags": ["cost_optimization", "inference", "trade_offs"],
            "evaluation_criteria": ["Optimization techniques", "Trade-off analysis", "Practical approach"]
        },
        {
            "question": "Your team is debating between building a custom ML solution vs using a third-party API. How would you frame the decision?",
            "difficulty": "medium",
            "subcategory": "technical_decision",
            "tags": ["decision_making", "build_vs_buy", "strategy"],
            "evaluation_criteria": ["Decision framework", "Factor consideration", "Recommendation clarity"]
        },
        {
            "question": "A customer reports that your AI chatbot gave a harmful response. How do you respond and prevent future occurrences?",
            "difficulty": "hard",
            "subcategory": "incident_response",
            "tags": ["incident_response", "safety", "responsible_ai"],
            "evaluation_criteria": ["Immediate response", "Root cause analysis", "Prevention measures"]
        },
        {
            "question": "You need to choose between a highly accurate model with high latency vs a less accurate model with low latency. How do you decide?",
            "difficulty": "medium",
            "subcategory": "trade_offs",
            "tags": ["trade_offs", "performance", "user_experience"],
            "evaluation_criteria": ["Use case analysis", "Metric prioritization", "Decision rationale"]
        }
    ]
}


class PreRAGService:
    """
    Pre-trained RAG service for general interview questions
    
    Features:
    - Pre-built question bank for Tech/AI domain
    - GPU-accelerated semantic search
    - Category and difficulty filtering
    - Fallback to keyword search if vector search fails
    """
    
    _instance: Optional["PreRAGService"] = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.settings = get_settings()
        self.model_config = get_model_config()
        self.embedding_service = get_embedding_service()
        self.chroma_client: Optional[chromadb.Client] = None
        self.collections: Dict[str, Any] = {}
        self._initialized = True
        
        logger.info("PreRAGService initialized")
    
    def initialize(self) -> bool:
        """Initialize ChromaDB and load/build question bank"""
        try:
            # Initialize ChromaDB
            persist_dir = get_data_path("pre_rag/chroma")
            os.makedirs(persist_dir, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # Check if collections exist, if not build them
            existing_collections = [c.name for c in self.chroma_client.list_collections()]
            
            for category in InterviewCategory:
                collection_name = f"prerag_{category.value}"
                
                if collection_name not in existing_collections:
                    logger.info(f"Building collection: {collection_name}")
                    self._build_collection(category)
                else:
                    self.collections[category.value] = self.chroma_client.get_collection(
                        name=collection_name
                    )
                    logger.info(f"Loaded existing collection: {collection_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize PreRAGService: {e}")
            return False
    
    def _build_collection(self, category: InterviewCategory):
        """Build a ChromaDB collection for a category"""
        questions = PREBUILT_QUESTIONS.get(category, [])
        if not questions:
            logger.warning(f"No questions for category: {category.value}")
            return
        
        collection_name = f"prerag_{category.value}"
        
        # Create collection
        collection = self.chroma_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Generate embeddings
        question_texts = [q["question"] for q in questions]
        embeddings = self.embedding_service.encode_documents(
            question_texts,
            show_progress=False
        )
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for i, q in enumerate(questions):
            q_id = hashlib.md5(q["question"].encode()).hexdigest()[:16]
            ids.append(f"{category.value}_{q_id}")
            documents.append(q["question"])
            metadatas.append({
                "category": category.value,
                "subcategory": q.get("subcategory", "general"),
                "difficulty": q.get("difficulty", "medium"),
                "tags": ",".join(q.get("tags", [])),
                "sample_answer": q.get("sample_answer", ""),
                "evaluation_criteria": ",".join(q.get("evaluation_criteria", []))
            })
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas
        )
        
        self.collections[category.value] = collection
        logger.info(f"Built collection {collection_name} with {len(questions)} questions")
    
    def query(
        self,
        request: RAGQueryRequest
    ) -> RAGQueryResponse:
        """
        Query the pre-RAG question bank
        
        Args:
            request: Query parameters
            
        Returns:
            Matching questions
        """
        start_time = time.time()
        
        try:
            # Determine which collection(s) to search
            if request.category:
                categories = [request.category]
            else:
                categories = list(InterviewCategory)
            
            all_questions = []
            
            for category in categories:
                collection = self.collections.get(category.value)
                if not collection:
                    continue
                
                # Generate query embedding
                query_embedding = self.embedding_service.encode_query(request.query)
                
                # Build where clause for filtering
                where_clause = {}
                if request.difficulty:
                    where_clause["difficulty"] = request.difficulty.value
                
                # Query collection
                results = collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=request.n_results,
                    where=where_clause if where_clause else None,
                    include=["documents", "metadatas", "distances"]
                )
                
                # Parse results
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i]
                    distance = results["distances"][0][i]
                    
                    question = InterviewQuestion(
                        id=results["ids"][0][i],
                        question=doc,
                        category=InterviewCategory(metadata["category"]),
                        subcategory=metadata.get("subcategory"),
                        difficulty=InterviewDifficulty(metadata.get("difficulty", "medium")),
                        tags=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
                        sample_answer=metadata.get("sample_answer") if request.include_sample_answers else None,
                        evaluation_criteria=metadata.get("evaluation_criteria", "").split(",") if metadata.get("evaluation_criteria") else None,
                        relevance_score=1 - distance  # Convert distance to similarity
                    )
                    all_questions.append(question)
            
            # Sort by relevance and limit
            all_questions.sort(key=lambda x: x.relevance_score or 0, reverse=True)
            all_questions = all_questions[:request.n_results]
            
            query_time = (time.time() - start_time) * 1000
            
            return RAGQueryResponse(
                questions=all_questions,
                query_time_ms=query_time,
                total_results=len(all_questions)
            )
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            # Return empty response on error
            return RAGQueryResponse(
                questions=[],
                query_time_ms=(time.time() - start_time) * 1000,
                total_results=0
            )
    
    def get_random_question(
        self,
        category: InterviewCategory,
        difficulty: Optional[InterviewDifficulty] = None,
        exclude_ids: List[str] = []
    ) -> Optional[InterviewQuestion]:
        """Get a random question from a category"""
        import random
        
        collection = self.collections.get(category.value)
        if not collection:
            return None
        
        # Get all questions from category
        where_clause = {}
        if difficulty:
            where_clause["difficulty"] = difficulty.value
        
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
            if id not in exclude_ids
        ]
        
        if not available:
            return None
        
        # Select random
        q_id, doc, metadata = random.choice(available)
        
        return InterviewQuestion(
            id=q_id,
            question=doc,
            category=InterviewCategory(metadata["category"]),
            subcategory=metadata.get("subcategory"),
            difficulty=InterviewDifficulty(metadata.get("difficulty", "medium")),
            tags=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
            sample_answer=metadata.get("sample_answer"),
            evaluation_criteria=metadata.get("evaluation_criteria", "").split(",") if metadata.get("evaluation_criteria") else None
        )
    
    def get_stats(self) -> QuestionBankStats:
        """Get question bank statistics"""
        by_category = {}
        by_difficulty = {"easy": 0, "medium": 0, "hard": 0}
        by_subcategory = {}
        total = 0
        
        for category in InterviewCategory:
            collection = self.collections.get(category.value)
            if collection:
                count = collection.count()
                by_category[category.value] = count
                total += count
                
                # Get difficulty breakdown
                for diff in InterviewDifficulty:
                    try:
                        results = collection.get(
                            where={"difficulty": diff.value}
                        )
                        by_difficulty[diff.value] += len(results["ids"])
                    except:
                        pass
        
        return QuestionBankStats(
            total_questions=total,
            by_category=by_category,
            by_difficulty=by_difficulty,
            by_subcategory=by_subcategory,
            last_updated=datetime.utcnow()
        )
    
    def rebuild_all(self):
        """Rebuild all collections from scratch"""
        logger.info("Rebuilding all Pre-RAG collections...")
        
        # Delete existing collections
        for category in InterviewCategory:
            collection_name = f"prerag_{category.value}"
            try:
                self.chroma_client.delete_collection(collection_name)
            except:
                pass
        
        self.collections = {}
        
        # Rebuild
        for category in InterviewCategory:
            self._build_collection(category)
        
        logger.info("Pre-RAG rebuild complete")


# Singleton accessor
def get_prerag_service() -> PreRAGService:
    """Get the Pre-RAG service singleton"""
    service = PreRAGService()
    if not service.collections:
        service.initialize()
    return service
