# AI Resume Coach & Mock Interview Platform
## Comprehensive Product Documentation

---

# REPORT 1: PRODUCT PROPOSAL

## 1.1 Executive Summary

**Product Name:** AI Resume Coach  
**Product Type:** AI-powered SaaS Web Application  
**Target Users:** Job seekers seeking personalized resume optimization and interview preparation  
**Core Value Proposition:** Automated resume-to-job matching analysis with AI-powered voice mock interviews

### Problem Statement
Job seekers struggle to tailor resumes to specific positions and lack accessible, personalized interview practice. Traditional coaching is expensive ($100-300/hour), and generic online tools don't provide contextual feedback.

### Solution Overview
A web platform that ingests user resumes and job postings, generates detailed match analysis with actionable recommendations, and provides voice-enabled mock interviews powered by contextual AI understanding of both the user's background and target role requirements.

---

## 1.2 Product Vision & Goals

### Primary Goals
1. Reduce resume-to-job matching analysis time from hours to minutes
2. Provide accessible, personalized mock interview practice 24/7
3. Deliver actionable insights that improve interview success rates

### Success Metrics
- User engagement: Average 3+ mock interview sessions per user
- Analysis accuracy: 85%+ user satisfaction on match analysis relevance
- Conversion: 15% free-to-paid conversion rate

---

## 1.3 Feature Specification (Revised & Corrected)

### Core Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Google OAuth Login | Single sign-on with subscription management | P0 |
| Resume Upload | PDF/DOCX ingestion with text extraction | P0 |
| Job URL Ingestion | Web scraping of job posting content | P0 |
| Match Analysis Report | 5-section analysis with scoring | P0 |
| Voice Mock Interview | Real-time conversational AI practice | P0 |
| Chat Interface | Text display synced with voice agent | P0 |
| User Profile Database | Persistent storage of user context | P0 |
| Interview History Export | Download conversation transcripts | P1 |
| Payment Integration | Stripe subscription management | P1 |

### ⚠️ Requirements Corrections & Clarifications

**ISSUE 1: LoRA/SFT Training Per User (Steps 4, 6)**
- **Original:** "Do LoRA/SFT model training process on curated QA pairs"
- **Problem:** Per-user fine-tuning is computationally impractical (hours of GPU time per user, $5-50 per training run)
- **Correction:** Replace with RAG-based personalization using vector embeddings. User context is retrieved at inference time, not baked into model weights.
- **Revised Architecture:** Resume/job data → Embedding → Vector store (per-user namespace) → Retrieved at query time → Augments base LLM prompt

**ISSUE 2: Real-time Web Knowledge Training (Step 6)**
- **Original:** "Abstract related knowledge from internet, further training the model"
- **Problem:** Cannot train models in real-time; web scraping for training data has legal/quality issues
- **Correction:** Use RAG with curated knowledge bases (interview question banks, skill definitions) pre-indexed. Optionally use web search APIs for current information at query time, not training time.

**ISSUE 3: GPU Availability Constraint**
- **Original:** GPU available for only 1 month
- **Impact:** Eliminates per-user fine-tuning as viable architecture
- **Correction:** Design for inference-only GPU usage (or CPU-compatible models). Use cloud APIs (OpenAI, Anthropic, Groq) for production, local GPU only for development/testing.

**ISSUE 4: Missing Error Handling Specifications**
- Job URL scraping failures (paywalls, anti-bot measures)
- Resume parsing failures (scanned PDFs, unusual formats)
- Voice recognition failures
- **Addition:** Graceful fallbacks and user-friendly error messages required for each

**ISSUE 5: Missing Accessibility Requirements**
- Voice-only interface excludes hearing-impaired users
- **Addition:** Text-based interview mode as alternative to voice

---

## 1.4 User Journey Map

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Login     │────▶│   Upload    │────▶│  Analysis   │
│  (Google)   │     │Resume + Job │     │   Report    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌─────────────┐            │
                    │    Mock     │◀───────────┘
                    │  Interview  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    Self      │  │  Technical   │  │  Soft Skill  │
│   Intro      │  │  Questions   │  │  Questions   │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 1.5 Monetization Strategy

### Freemium Model
- **Free Tier:** 1 resume analysis per account, 1 mock interview session
- **Pro Tier ($9.99/month):** Unlimited analyses, unlimited interviews, history export
- **Implementation:** Stripe subscription with usage tracking in Firebase

---

# REPORT 2: END-TO-END PRODUCT DESIGN PLAN

## 2.1 Architecture Overview

### Design Principles Applied
✅ Modular design with clear service boundaries  
✅ Cost minimization through serverless + managed services  
✅ Performance-complexity balance via strategic API usage  
✅ Extensibility for payments and CPU-only deployment  
✅ GPU-optional architecture for long-term sustainability

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vercel)                        │
│  Next.js 14 + React + TailwindCSS + shadcn/ui                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │  Auth Page  │ │  Main Page  │ │ Interview   │               │
│  │             │ │  (Analysis) │ │    Page     │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY (FastAPI on Render)             │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │  /auth    │ │ /upload   │ │ /analyze  │ │ /interview│       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Firebase   │    │   RAG Pipeline   │    │ Voice Agent  │
│  Auth + DB   │    │  (Vector Store)  │    │   Service    │
└──────────────┘    └──────────────────┘    └──────────────┘
        │                     │                     │
        │           ┌─────────┴─────────┐           │
        │           ▼                   ▼           │
        │    ┌────────────┐      ┌────────────┐     │
        │    │ Embedding  │      │   LLM API  │     │
        │    │   Model    │      │ (Groq/OAI) │◀────┘
        │    └────────────┘      └────────────┘
        │           │
        │           ▼
        │    ┌────────────┐
        └───▶│ Pinecone/  │
             │  Qdrant    │
             └────────────┘
```

---

## 2.2 Frontend Design

### Technology Stack
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | **Next.js 14 (App Router)** | SSR, API routes, Vercel-native |
| Styling | **TailwindCSS + shadcn/ui** | Rapid development, consistent design |
| State | **Zustand** | Lightweight, no boilerplate |
| Voice | **Web Speech API + custom hooks** | Browser-native, no dependencies |
| Hosting | **Vercel** ✅ Your choice confirmed | Free tier generous, edge functions |

### Module Structure
```
frontend/
├── app/
│   ├── (auth)/
│   │   └── login/page.tsx          # Google OAuth flow
│   ├── (dashboard)/
│   │   ├── page.tsx                # Main analysis page
│   │   └── interview/page.tsx      # Mock interview page
│   └── api/                        # Next.js API routes (proxy)
├── components/
│   ├── upload/
│   │   ├── ResumeUploader.tsx
│   │   └── JobUrlInput.tsx
│   ├── analysis/
│   │   ├── MatchScoreCard.tsx
│   │   ├── ComparisonTable.tsx
│   │   └── ReportSection.tsx
│   ├── interview/
│   │   ├── VoiceAgent.tsx
│   │   ├── ChatBox.tsx
│   │   └── InterviewControls.tsx
│   └── shared/
├── hooks/
│   ├── useVoiceRecognition.ts
│   ├── useTextToSpeech.ts
│   └── useInterviewState.ts
├── lib/
│   ├── firebase.ts
│   └── api-client.ts
└── stores/
    └── userStore.ts
```

### Voice Implementation (Browser-Side)
```typescript
// hooks/useVoiceRecognition.ts
export function useVoiceRecognition() {
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  
  const recognition = useMemo(() => {
    if (typeof window === 'undefined') return null;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    return new SpeechRecognition();
  }, []);

  // Continuous recognition with interim results
  recognition.continuous = true;
  recognition.interimResults = true;
  
  // ... implementation
}
```

---

## 2.3 Backend Design

### Technology Stack
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | **FastAPI** | Async, Python-native, OpenAPI docs |
| Hosting | **Render** ✅ Your choice confirmed | Easy deployment, free tier available |
| Task Queue | **Redis + Celery** (optional) | For async processing if needed |
| File Storage | **Firebase Storage** or **Cloudflare R2** | Cost-effective blob storage |

### Why Keep Render (vs. Alternatives)
- ✅ Native Python support
- ✅ Background workers available
- ✅ Auto-scaling on paid tiers
- ⚠️ Cold starts on free tier (mitigate with health checks)

### Module Structure
```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry
│   ├── config.py                  # Environment configuration
│   ├── dependencies.py            # Dependency injection
│   │
│   ├── routers/
│   │   ├── auth.py                # /auth endpoints
│   │   ├── upload.py              # /upload endpoints
│   │   ├── analysis.py            # /analyze endpoints
│   │   └── interview.py           # /interview endpoints
│   │
│   ├── services/
│   │   ├── document_processor.py  # Resume/URL parsing
│   │   ├── embedding_service.py   # Vector embedding
│   │   ├── rag_service.py         # Retrieval logic
│   │   ├── llm_service.py         # LLM API calls
│   │   ├── analysis_service.py    # Report generation
│   │   └── interview_service.py   # Interview logic
│   │
│   ├── models/
│   │   ├── schemas.py             # Pydantic models
│   │   └── database.py            # Firebase/DB models
│   │
│   └── utils/
│       ├── text_extraction.py     # PDF/DOCX parsing
│       ├── web_scraper.py         # Job URL scraping
│       └── prompt_templates.py    # LLM prompts
│
├── tests/
├── requirements.txt
└── Dockerfile
```

### API Endpoints Specification

```python
# Core API Routes

POST /auth/verify-token
  # Verify Firebase token, create/update user record

POST /upload/resume
  # Accept PDF/DOCX, extract text, return parsed content
  # Request: multipart/form-data with file
  # Response: { text: string, metadata: {...} }

POST /upload/job-url
  # Scrape job posting, extract structured data
  # Request: { url: string }
  # Response: { text: string, structured: {...} }

POST /analyze/generate-report
  # Generate 5-section analysis report
  # Request: { user_id: string, resume_text: string, job_text: string }
  # Response: { report_html: string, match_score: float }

POST /analyze/build-context
  # Build RAG context for user (embeddings + indexing)
  # Request: { user_id: string, resume: string, job: string }
  # Response: { context_id: string, status: string }

POST /interview/start
  # Initialize interview session
  # Request: { user_id: string, interview_type: enum }
  # Response: { session_id: string, greeting: string }

POST /interview/respond
  # Process user response, generate next question
  # Request: { session_id: string, user_message: string }
  # Response: { ai_message: string, is_complete: bool }

GET /interview/history/{session_id}
  # Get full interview transcript
  # Response: { messages: [...], created_at: datetime }
```

---

## 2.4 User Authorization & Database

### Technology Stack
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Auth | **Firebase Auth** ✅ | Google OAuth built-in, free tier generous |
| User DB | **Firebase Firestore** ✅ | Real-time sync, serverless, free tier |
| Vector DB | **Pinecone (Free)** or **Qdrant Cloud** | Managed vector search |
| File Storage | **Firebase Storage** | Integrated with Auth |

### Database Schema (Firestore)

```javascript
// Collection: users
{
  uid: "firebase_auth_uid",
  email: "user@example.com",
  displayName: "User Name",
  subscription: {
    tier: "free" | "pro",
    stripeCustomerId: "cus_xxx",
    usageCount: {
      analysisCount: 1,
      interviewCount: 3
    }
  },
  createdAt: Timestamp,
  updatedAt: Timestamp
}

// Collection: user_contexts
{
  userId: "firebase_auth_uid",
  resumeText: "...",
  resumeMetadata: { fileName, uploadedAt, skills: [...] },
  activeJobPosting: {
    url: "...",
    text: "...",
    structuredData: { title, company, requirements: [...] }
  },
  vectorNamespace: "user_xxx_context",  // Pinecone namespace
  lastUpdated: Timestamp
}

// Collection: analysis_reports
{
  userId: "firebase_auth_uid",
  jobUrl: "...",
  reportHtml: "...",
  matchScore: 0.78,
  createdAt: Timestamp
}

// Collection: interview_sessions
{
  userId: "firebase_auth_uid",
  sessionId: "uuid",
  interviewType: "technical" | "soft_skill" | "self_intro",
  messages: [
    { role: "assistant", content: "...", timestamp: Timestamp },
    { role: "user", content: "...", timestamp: Timestamp }
  ],
  status: "active" | "completed",
  createdAt: Timestamp
}
```

---

## 2.5 AI Model Selection & Data Preparation

### ⚠️ CRITICAL ARCHITECTURE DECISION

**Original Requirement:** LoRA/SFT fine-tuning per user  
**Revised Architecture:** RAG-only with prompt engineering

### Rationale for Change
| Factor | Fine-tuning Approach | RAG Approach |
|--------|---------------------|--------------|
| GPU Time | Hours per user | Seconds per query |
| Cost | $5-50 per training | ~$0.01 per query |
| Latency | Minutes to train | Instant retrieval |
| Flexibility | Requires retraining | Dynamic context |
| GPU Dependency | Required | Optional |

### Model Selection

| Component | Recommended Model | Fallback | Notes |
|-----------|------------------|----------|-------|
| **Embedding** | `text-embedding-3-small` (OpenAI) | `BAAI/bge-small-en-v1.5` (local) | 1536 dims, excellent quality/cost |
| **LLM (Analysis)** | `gpt-4o-mini` or `claude-3-haiku` | `llama-3.1-8b` via Groq | Complex structured output |
| **LLM (Interview)** | `groq/llama-3.1-70b` | `gpt-4o-mini` | Fast inference for real-time chat |
| **TTS** | Browser Web Speech API | ElevenLabs API | Cost: Free vs $0.30/1K chars |
| **STT** | Browser Web Speech API | Whisper API | Cost: Free vs $0.006/min |

### Why Groq for Interview
- **Speed:** 300+ tokens/sec (vs 50-80 for OpenAI)
- **Cost:** Free tier with generous limits
- **Quality:** Llama 3.1 70B comparable to GPT-4 for conversation

---

## 2.6 RAG Pipeline Design

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT INGESTION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐        │
│  │  Resume  │────▶│  Text        │────▶│  Chunking    │        │
│  │  (PDF)   │     │  Extraction  │     │  (512 tokens)│        │
│  └──────────┘     │  PyMuPDF     │     └──────┬───────┘        │
│                   └──────────────┘            │                 │
│  ┌──────────┐     ┌──────────────┐            │                 │
│  │  Job URL │────▶│  Web Scrape  │────────────┤                 │
│  │          │     │  (Playwright)│            │                 │
│  └──────────┘     └──────────────┘            │                 │
│                                               ▼                 │
│                                    ┌──────────────────┐         │
│                                    │    Embedding     │         │
│                                    │  (OpenAI/BGE)    │         │
│                                    └────────┬─────────┘         │
│                                             │                   │
│                                             ▼                   │
│                                    ┌──────────────────┐         │
│                                    │   Vector Store   │         │
│                                    │   (Pinecone)     │         │
│                                    │  namespace=user_x│         │
│                                    └──────────────────┘         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    QUERY & RETRIEVAL                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐        │
│  │  User    │────▶│   Embed      │────▶│   Vector     │        │
│  │  Query   │     │   Query      │     │   Search     │        │
│  └──────────┘     └──────────────┘     │  (top-k=5)   │        │
│                                        └──────┬───────┘        │
│                                               │                 │
│       ┌───────────────────────────────────────┘                 │
│       ▼                                                         │
│  ┌─────────────────────────────────────────────────────┐       │
│  │                  PROMPT CONSTRUCTION                 │       │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │       │
│  │  │   System    │ │  Retrieved  │ │    User     │    │       │
│  │  │   Prompt    │ │   Context   │ │   Query     │    │       │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │       │
│  └──────────────────────────┬──────────────────────────┘       │
│                             │                                   │
│                             ▼                                   │
│                    ┌──────────────────┐                         │
│                    │       LLM        │                         │
│                    │    Response      │                         │
│                    └──────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Code Structure

```python
# services/rag_service.py

class RAGService:
    def __init__(self, embedding_client, vector_store, llm_client):
        self.embedder = embedding_client
        self.vector_store = vector_store
        self.llm = llm_client
    
    async def ingest_user_context(
        self, 
        user_id: str, 
        resume_text: str, 
        job_text: str
    ) -> str:
        """Build user's vector namespace with resume + job context"""
        
        # Chunk documents
        resume_chunks = self._chunk_text(resume_text, source="resume")
        job_chunks = self._chunk_text(job_text, source="job_posting")
        
        # Generate embeddings
        all_chunks = resume_chunks + job_chunks
        embeddings = await self.embedder.embed_batch(
            [c.text for c in all_chunks]
        )
        
        # Upsert to vector store with user namespace
        namespace = f"user_{user_id}"
        await self.vector_store.upsert(
            vectors=[
                {
                    "id": f"{namespace}_{i}",
                    "values": emb,
                    "metadata": {"text": chunk.text, "source": chunk.source}
                }
                for i, (chunk, emb) in enumerate(zip(all_chunks, embeddings))
            ],
            namespace=namespace
        )
        
        return namespace
    
    async def query_with_context(
        self, 
        user_id: str, 
        query: str,
        system_prompt: str
    ) -> str:
        """Retrieve context and generate response"""
        
        # Embed query
        query_embedding = await self.embedder.embed(query)
        
        # Retrieve relevant chunks
        results = await self.vector_store.query(
            vector=query_embedding,
            namespace=f"user_{user_id}",
            top_k=5,
            include_metadata=True
        )
        
        # Build context string
        context = "\n\n".join([
            f"[{r.metadata['source']}]: {r.metadata['text']}"
            for r in results.matches
        ])
        
        # Generate response
        response = await self.llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuery: {query}"}
        ])
        
        return response
```

---

## 2.7 Analysis Report Generation

### Prompt Engineering for 5-Section Report

```python
# utils/prompt_templates.py

ANALYSIS_SYSTEM_PROMPT = """You are an expert career counselor and resume analyst. 
Generate a comprehensive analysis comparing a resume to a job posting.

Your output must be valid HTML with modern, clean styling.
Use the exact section structure provided.
Be specific and actionable in your recommendations."""

SECTION_1_PROMPT = """
## Section 1: Job Description Summary

Extract and organize the following from the job posting into a clean bullet list:
- Position Title, Company Name, Department, Location
- Employment Type, Requisition ID, Reporting To
- Compensation (Salary, Benefits, Culture)
- Key Responsibilities (bullet list)
- Core Requirements: Technical Skills, Soft Skills
- Preferred/Nice-to-Have: Technical Skills, Soft Skills  
- Cultural Fit indicators

Use 'Not specified' for missing information.
Format as HTML with proper bullet lists and 1.2 line-height.

JOB POSTING:
{job_text}
"""

SECTION_2_PROMPT = """
## Section 2: Match Analysis Table

Create an HTML table comparing job requirements to the resume:

Columns:
1. Category (each key requirement from job posting)
2. Match Status (use exactly these symbols):
   - ✅ Strong
   - 🔷 Moderate-strong  
   - ⚠️ Partial
   - ❌ Lack
3. Comments (precise explanation of match)
4. Match Weight (Strong=1, Moderate=0.8, Partial=0.5, Lack=0.1)

After the table, calculate:
- Sum of Match Weights
- Count of Match Weights
- Match Score = Sum/Count (as percentage, 2 decimal places)

Style the table with modern CSS (borders, alternating rows, proper padding).

RESUME:
{resume_text}

JOB POSTING:
{job_text}
"""

# ... Similar templates for Sections 3-5
```

---

## 2.8 Voice Agent & Interview System

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     BROWSER (Frontend)                          │
│  ┌─────────────────┐     ┌─────────────────┐                   │
│  │  Web Speech API │     │  Web Speech API │                   │
│  │  (Recognition)  │     │  (Synthesis)    │                   │
│  └────────┬────────┘     └────────▲────────┘                   │
│           │                       │                             │
│           ▼                       │                             │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              Interview Controller                    │       │
│  │  - State machine for interview flow                 │       │
│  │  - Message history management                       │       │
│  │  - "STOP" keyword detection                         │       │
│  └────────────────────────┬────────────────────────────┘       │
└───────────────────────────┼─────────────────────────────────────┘
                            │ WebSocket / REST
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              Interview Service                       │       │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │       │
│  │  │   State     │  │    RAG      │  │    LLM      │  │       │
│  │  │   Manager   │  │   Context   │  │   (Groq)    │  │       │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### Interview State Machine

```python
# services/interview_service.py

from enum import Enum
from typing import Optional

class InterviewState(Enum):
    GREETING = "greeting"
    MENU_SELECTION = "menu_selection"
    SELF_INTRO = "self_intro"
    TECHNICAL = "technical"
    SOFT_SKILL = "soft_skill"
    COMPLETED = "completed"

class InterviewSession:
    def __init__(self, user_id: str, user_context: dict):
        self.user_id = user_id
        self.state = InterviewState.GREETING
        self.current_section: Optional[str] = None
        self.question_index = 0
        self.messages = []
        self.user_context = user_context  # From RAG
        
    def get_greeting(self) -> str:
        return (
            "Welcome to the Mock Interview! I'm your AI interviewer today. "
            "I've reviewed your resume and the job posting. "
            "Please let me know when you're ready to begin."
        )
    
    def get_menu(self) -> str:
        return (
            "Please select an interview section:\n"
            "1. Self-introduction questions\n"
            "2. Technical questions\n"
            "3. Soft-skill questions\n\n"
            "You can say 'STOP' at any time to return to this menu."
        )
    
    async def process_response(self, user_message: str, rag_service, llm_service) -> str:
        # Detect STOP command
        if "stop" in user_message.lower():
            self.state = InterviewState.MENU_SELECTION
            self.question_index = 0
            return "No problem! " + self.get_menu()
        
        # State machine logic
        if self.state == InterviewState.GREETING:
            if self._is_affirmative(user_message):
                self.state = InterviewState.MENU_SELECTION
                return self.get_menu()
            return "Just let me know when you're ready!"
            
        elif self.state == InterviewState.MENU_SELECTION:
            section = self._parse_section_choice(user_message)
            if section:
                self.current_section = section
                self.state = InterviewState[section.upper()]
                return await self._get_next_question(rag_service, llm_service)
            return "Please choose 1, 2, or 3."
            
        else:
            # In interview section - provide feedback and next question
            feedback = await self._generate_feedback(user_message, llm_service)
            self.question_index += 1
            
            if self.question_index >= 5:
                self.state = InterviewState.MENU_SELECTION
                return (
                    f"{feedback}\n\n"
                    "Congratulations! You've completed this section's mock interview. "
                    "Great job! Feel free to download your transcript from the chat box. "
                    "Would you like to continue with another section?\n\n"
                    + self.get_menu()
                )
            
            next_q = await self._get_next_question(rag_service, llm_service)
            return f"{feedback}\n\n{next_q}"
```

### Question Generation with RAG Context

```python
TECHNICAL_QUESTION_PROMPT = """Based on the candidate's resume and job requirements, 
generate a relevant technical interview question.

Resume context:
{resume_context}

Job requirements (technical skills):
{job_requirements}

Previously asked questions: {previous_questions}

Generate ONE specific question that:
1. References a skill/experience from their resume that matches job requirements
2. Asks about challenges, achievements, or specific implementations
3. Is conversational and encouraging in tone

Example formats:
- "In your resume, I noticed you mentioned [X] which aligns with our need for [Y]. Could you tell me about a challenging situation you faced with [X]?"
- "I see you have experience with [tool/platform]. What would you say was your biggest achievement using it?"
"""
```

---

## 2.9 GPU & Deployment Strategy

### Phase 1: Development (Month 1 - GPU Available)

| Component | Deployment | Notes |
|-----------|------------|-------|
| Local Dev | GPU Machine (16GB VRAM) | Testing local models |
| Embedding | Local `bge-small-en-v1.5` | GPU-accelerated |
| LLM Testing | Local `llama-3.1-8b` | Validate prompts |
| Vector DB | Qdrant (Docker local) | Free, self-hosted |

### Phase 2: Production (Post GPU)

| Component | Deployment | Cost/Month |
|-----------|------------|------------|
| Frontend | Vercel (Free tier) | $0 |
| Backend | Render (Free tier) | $0 |
| Auth/DB | Firebase (Spark plan) | $0 |
| Vector DB | Pinecone (Free tier) | $0 |
| Embedding | OpenAI API | ~$5 (low volume) |
| LLM | Groq API (Free tier) | $0 |
| LLM Fallback | OpenAI gpt-4o-mini | ~$10 |

**Estimated Monthly Cost: $0-20 for MVP**

### CPU-Compatible Deployment Path

```python
# config.py - Environment-aware model selection

import os

class Settings:
    # Detect GPU availability
    USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
    
    # Model selection based on environment
    if USE_GPU:
        EMBEDDING_MODEL = "local:BAAI/bge-small-en-v1.5"
        LLM_MODEL = "local:llama-3.1-8b"
    else:
        EMBEDDING_MODEL = "openai:text-embedding-3-small"
        LLM_MODEL = "groq:llama-3.1-70b-versatile"
```

---

## 2.10 Stripe Payment Integration (Extensibility)

### Implementation Plan

```
┌─────────────────────────────────────────────────────────────────┐
│                    PAYMENT FLOW                                 │
│                                                                 │
│  Free User                                                      │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────────────┐     ┌─────────────────┐                   │
│  │ Uses 1 Free     │────▶│ Paywall Modal   │                   │
│  │ Analysis        │     │ "Upgrade to Pro"│                   │
│  └─────────────────┘     └────────┬────────┘                   │
│                                   │                             │
│                                   ▼                             │
│                          ┌─────────────────┐                   │
│                          │ Stripe Checkout │                   │
│                          │ (Hosted Page)   │                   │
│                          └────────┬────────┘                   │
│                                   │                             │
│                                   ▼                             │
│                          ┌─────────────────┐                   │
│                          │ Webhook: Update │                   │
│                          │ Firestore tier  │                   │
│                          └─────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### Database Schema for Billing

```javascript
// users collection - extended
{
  uid: "...",
  subscription: {
    tier: "free" | "pro",
    stripeCustomerId: "cus_xxx",
    stripeSubscriptionId: "sub_xxx",
    currentPeriodEnd: Timestamp,
    usageThisPeriod: {
      analysisCount: 1,
      interviewMinutes: 15
    }
  }
}
```

---

# REPORT 3: RISK ANALYSIS

## 3.1 Critical Design Challenges

### Challenge 1: Real-Time Voice Latency (HIGHEST PRIORITY)

**Risk Level:** 🔴 Critical

**Problem:** Voice conversation requires <500ms response time for natural feel. Full RAG retrieval + LLM generation can take 2-5 seconds.

**Mitigation Strategies:**
1. **Use Groq API** - 300+ tokens/sec, ~500ms for typical response
2. **Streaming responses** - Start TTS as tokens arrive, not after completion
3. **Pre-fetch likely responses** - Cache common follow-ups
4. **Shorter prompts** - Minimize context window for interview responses

**Implementation:**
```python
async def stream_interview_response(session, user_input):
    async for chunk in llm.stream_chat(prompt):
        yield chunk  # Frontend begins TTS immediately
```

### Challenge 2: Job URL Scraping Reliability

**Risk Level:** 🟠 High

**Problem:** Job posting sites have varying structures, anti-bot measures, and dynamic content (JavaScript rendering).

**Mitigation Strategies:**
1. **Playwright** over Requests - Handles JS-rendered content
2. **Multiple parsing strategies** - JSON-LD structured data, meta tags, body text
3. **Graceful fallback** - Allow manual paste if scraping fails
4. **Known site adapters** - Custom parsers for LinkedIn, Indeed, Greenhouse

**Implementation:**
```python
class JobScraper:
    async def scrape(self, url: str) -> JobPosting:
        try:
            # Try structured data first (most reliable)
            structured = await self._extract_json_ld(url)
            if structured:
                return structured
            
            # Fall back to DOM parsing
            return await self._parse_dom(url)
        except ScrapingError:
            raise UserFacingError(
                "Unable to automatically extract job posting. "
                "Please paste the job description text directly."
            )
```

### Challenge 3: Embedding Cost at Scale

**Risk Level:** 🟡 Medium

**Problem:** OpenAI embedding costs ($0.02/1M tokens) can escalate with many users.

**Mitigation Strategies:**
1. **Local embedding model** (bge-small-en-v1.5) for CPU deployment
2. **Caching** - Hash-based deduplication of identical documents
3. **Batch processing** - Reduce API calls via batching
4. **Lazy embedding** - Only embed new content, not full re-index

---

## 3.2 Technical Implementation Challenges

### Challenge 4: State Management Across Voice/Chat/Backend

**Risk Level:** 🟡 Medium

**Problem:** Interview state must be synchronized between browser (voice), chat display, and backend session.

**Solution Architecture:**
```
Single Source of Truth: Backend Session Store

Browser ──WebSocket──▶ Backend Session ◀──REST──── Chat History
   │                        │
   └── Local state is       └── Authoritative state
       display-only             persisted in Firestore
```

### Challenge 5: PDF Resume Parsing Quality

**Risk Level:** 🟡 Medium

**Problem:** PDFs vary widely - scanned images, multi-column layouts, tables, creative designs.

**Mitigation:**
1. **PyMuPDF** for text-based PDFs (fast, accurate)
2. **Fallback to OCR** (Tesseract) for scanned documents
3. **LLM-based cleanup** - Use GPT to reformat messy extractions
4. **User confirmation** - Show extracted text for verification

### Challenge 6: Browser Speech API Compatibility

**Risk Level:** 🟡 Medium

**Problem:** Web Speech API has inconsistent support (Safari limited, mobile issues).

**Mitigation:**
1. **Feature detection** with graceful degradation
2. **Text-only mode** as fallback
3. **Consider Deepgram/AssemblyAI** for production reliability

---

## 3.3 Operational Risks

### Challenge 7: Free Tier Limits

| Service | Free Tier Limit | Risk | Mitigation |
|---------|-----------------|------|------------|
| Vercel | 100GB bandwidth | Low | Optimize assets |
| Render | 750 hours/month | Medium | Sleep during low usage |
| Pinecone | 100K vectors | Medium | Namespace cleanup for inactive users |
| Firebase | 1GB storage | Low | Compress documents |
| Groq | Rate limited | Medium | Implement retry logic, queue |

### Challenge 8: Data Privacy & Security

**Risk Level:** 🟠 High

**Concerns:**
- Resumes contain PII (names, emails, addresses, phone numbers)
- Job search activity is sensitive
- LLM providers process user data

**Mitigation:**
1. **Privacy policy** clearly stating data usage
2. **Data retention limits** - Auto-delete after 30 days inactive
3. **PII scrubbing** before sending to LLM (optional mode)
4. **SOC2-compliant providers** (Firebase, OpenAI)

---

## 3.4 Future Risks & Contingency Plans

### Risk 1: API Provider Changes

**Scenario:** Groq removes free tier, OpenAI increases prices

**Contingency:**
- Abstract LLM calls behind interface
- Maintain compatibility with multiple providers
- Local model fallback (llama.cpp for CPU)

```python
# Abstract interface allows swapping providers
class LLMProvider(Protocol):
    async def chat(self, messages: list) -> str: ...
    
class GroqProvider(LLMProvider): ...
class OpenAIProvider(LLMProvider): ...
class LocalLlamaProvider(LLMProvider): ...
```

### Risk 2: Scaling Beyond Free Tiers

**Scenario:** Product gains traction, exceeds free limits

**Contingency Plan:**
| Users | Monthly Cost | Action |
|-------|-------------|--------|
| 0-100 | $0-20 | Free tiers sufficient |
| 100-1000 | $50-200 | Enable Stripe, convert to Pro |
| 1000+ | $500+ | Requires sustainable revenue |

### Risk 3: Voice Technology Evolution

**Scenario:** Native browser APIs become deprecated; new standards emerge

**Contingency:**
- Modular voice components
- Prepare integration paths for WebRTC, Whisper API, ElevenLabs

---

## 3.5 Risk Summary Matrix

| Risk | Probability | Impact | Priority | Status |
|------|-------------|--------|----------|--------|
| Voice latency issues | High | High | 🔴 P0 | Mitigated via Groq |
| Job scraping failures | High | Medium | 🟠 P1 | Fallback ready |
| PDF parsing quality | Medium | Medium | 🟡 P2 | Multi-strategy approach |
| Free tier exhaustion | Medium | High | 🟠 P1 | Monetization path defined |
| Data privacy concerns | Low | High | 🟠 P1 | Privacy measures planned |
| API provider changes | Low | Medium | 🟡 P2 | Provider abstraction |
| Browser compatibility | Medium | Low | 🟢 P3 | Fallback modes |

---

## APPENDIX: Implementation Timeline

### Phase 1: Foundation (Weeks 1-2)
- [ ] Project scaffolding (Next.js + FastAPI)
- [ ] Firebase Auth integration
- [ ] Basic file upload flow
- [ ] Database schema implementation

### Phase 2: Core Analysis (Weeks 3-4)
- [ ] Resume text extraction
- [ ] Job URL scraping
- [ ] RAG pipeline (embedding + Pinecone)
- [ ] Report generation prompts
- [ ] HTML report rendering

### Phase 3: Voice Interview (Weeks 5-6)
- [ ] Interview state machine
- [ ] Browser voice integration
- [ ] Chat synchronization
- [ ] Question generation with RAG

### Phase 4: Polish & Deploy (Weeks 7-8)
- [ ] Error handling & edge cases
- [ ] UI/UX refinement
- [ ] Performance optimization
- [ ] Production deployment
- [ ] Stripe integration (if time permits)

---

*Document Version: 1.0*  
*Last Updated: Generated for Emma's Capstone Project*
