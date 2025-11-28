# SmartSuccess.AI - Mock Interview & RAG Implementation Roadmap

## 📊 Current State Analysis

### ✅ What You Have
| Component | Status | Location |
|-----------|--------|----------|
| Resume Matcher Backend | ✅ Working | `resume-matcher-backend/main.py` |
| AI Service (OpenAI/xAI) | ✅ Working | `call_ai_api()` with fallback |
| User Management | ✅ Working | Firebase + Stripe integration |
| Frontend (Next.js) | ✅ Deployed | Vercel: smartsuccess-ai.vercel.app |
| Extension Plan | ✅ Documented | `extension-plan.md` |

### 🎯 What to Build (Yoodli-Inspired Features)

Based on the Yoodli screenshot you provided:
1. **Mock Interview Chat Interface** - Real-time conversation with AI interviewer
2. **Transcript Panel** - Timestamped conversation with copy function
3. **STAR Rubric Scoring** - Situation/Task/Action/Result (each 1-5)
4. **Active Listening Score** - Engagement rating
5. **Coaching Feedback Panel** - Strength & Growth areas
6. **Analytics Dashboard** - Visual metrics

---

## 🏗️ Implementation Phases

### Phase 1: RAG Layer Foundation (Week 1)
**Goal: Context-aware interview questions based on resume + job posting**

### Phase 2: Interview Engine (Week 2)
**Goal: State machine for interview flow + feedback generation**

### Phase 3: Voice Integration (Week 3)
**Goal: Speech-to-text input, text-to-speech output**

### Phase 4: Feedback Dashboard (Week 4)
**Goal: Yoodli-style scoring UI with analytics**

---

## 📁 Proposed File Structure

```
SmartSuccess.AI/
├── resume-matcher-backend/
│   ├── main.py                      # Existing + new routes
│   ├── requirements.txt             # Updated dependencies
│   │
│   ├── services/                    # 🆕 NEW FOLDER
│   │   ├── __init__.py
│   │   ├── embedding_service.py     # OpenAI embeddings
│   │   ├── vector_store.py          # ChromaDB operations
│   │   ├── rag_service.py           # RAG query logic
│   │   ├── interview_service.py     # Interview state machine
│   │   └── feedback_service.py      # 🆕 STAR scoring & analysis
│   │
│   ├── models/                      # 🆕 NEW FOLDER
│   │   ├── __init__.py
│   │   ├── schemas.py               # Pydantic models
│   │   └── feedback_models.py       # 🆕 Feedback rubrics
│   │
│   └── prompts/                     # 🆕 NEW FOLDER
│       ├── __init__.py
│       ├── interview_prompts.py     # Question templates
│       └── feedback_prompts.py      # 🆕 Scoring prompts
│
└── resume-matcher-frontend/
    └── src/
        └── app/
            ├── page.tsx             # Existing main page
            ├── interview/           # 🆕 NEW FOLDER
            │   ├── page.tsx         # Main interview UI
            │   └── components/
            │       ├── ChatPanel.tsx
            │       ├── TranscriptPanel.tsx
            │       ├── FeedbackPanel.tsx
            │       ├── VoiceControls.tsx
            │       └── RubricDisplay.tsx
            └── dashboard/           # 🆕 Analytics page
                └── page.tsx
```

---

## 🔧 Backend Implementation Details

### New Dependencies (add to requirements.txt)
```txt
# Vector Store & Embeddings
chromadb>=0.4.0
sentence-transformers>=2.2.0

# Interview Support  
groq>=0.4.0              # Fast LLM for real-time voice
whisper-openai>=1.0.0    # Optional: server-side transcription

# Analytics
numpy>=1.24.0
```

### API Endpoints to Add

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/build-context` | POST | Build RAG from resume + job |
| `/api/interview/start` | POST | Start new session |
| `/api/interview/message` | POST | Send/receive messages |
| `/api/interview/feedback` | POST | Generate STAR feedback |
| `/api/interview/history/{id}` | GET | Get full transcript |
| `/api/interview/analytics/{uid}` | GET | User analytics |

---

## 🎨 Frontend UI Layout (Matching Yoodli)

```
┌──────────────────────────────────────────────────────────────────────┐
│  SmartSuccess.AI Logo    │  🏠 Home  📊 Dashboard  📹 My Recordings  │
├──────────────────────────────────────────────────────────────────────┤
│                          │                          │                │
│   SIDEBAR                │    CHAT PANEL            │  FEEDBACK      │
│   ─────────              │    ──────────            │  PANEL         │
│   🏠 Home                │                          │  ──────────    │
│   🛠️ Builder             │   Job Title + Date       │                │
│   📊 Dashboard           │                          │  🎭 Roleplay   │
│   📹 My Recordings       │   ┌─────────────────┐   │   complete     │
│   📚 My Learning         │   │                 │   │   Score: 50%   │
│                          │   │  AI Interviewer │   │                │
│                          │   │  + Chat Area    │   │  ┌─────────┐  │
│                          │   │                 │   │  │Coaching │  │
│                          │   │                 │   │  │Analytics│  │
│                          │   └─────────────────┘   │  └─────────┘  │
│                          │                          │                │
│                          │   TRANSCRIPT             │  📋 Rubric     │
│                          │   ──────────             │  ──────────    │
│                          │   0:01 AI: Hi...         │  Active        │
│                          │   0:07 You: Thanks...    │  Listening 2/5 │
│                          │   0:11 AI: Walk me...    │                │
│                          │                          │  Use STAR 3/5  │
│   ┌──────────────────┐   │   [Copy transcript]      │  S: 3/5 T: 3/5│
│   │ User Avatar      │   │                          │  A: 3/5 R: 3/5│
│   │ user@email.com   │   │                          │                │
│   │ powered by       │   │                          │  ✅ Strength   │
│   │ SmartSuccess.AI  │   │                          │  ⚠️ Growth    │
│   └──────────────────┘   │                          │                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Feedback Scoring System (STAR Method)

### Rubric Categories
```typescript
interface InterviewFeedback {
  overallScore: number;           // 0-100%
  
  activeListening: {
    score: number;                // 1-5
    insights: string[];           // What they did well/poorly
  };
  
  starMethod: {
    situation: number;            // 1-5
    task: number;                 // 1-5
    action: number;               // 1-5
    result: number;               // 1-5
    insights: string[];
  };
  
  strengths: string[];            // 2-3 positive points
  growthAreas: string[];          // 2-3 improvement areas
  
  deliveryMetrics: {
    fillerWords: number;          // Count of "um", "uh", "like"
    pacing: 'too_fast' | 'good' | 'too_slow';
    wordCount: number;
    speakingTime: number;         // seconds
  };
}
```

### Scoring Prompt Template
```python
FEEDBACK_PROMPT = """
Analyze this interview response using the STAR method rubric.

QUESTION: {question}
CANDIDATE RESPONSE: {response}
JOB CONTEXT: {job_summary}

Rate each category from 1-5 and provide specific feedback:

1. ACTIVE LISTENING (Did they address the actual question?)
2. SITUATION (Did they set clear context?)
3. TASK (Did they explain their specific responsibility?)
4. ACTION (Did they describe concrete steps taken?)
5. RESULT (Did they quantify outcomes/impact?)

Also identify:
- 2-3 STRENGTHS (specific things they did well)
- 2-3 GROWTH AREAS (specific improvements needed)

Return as JSON:
{
  "activeListening": {"score": X, "insight": "..."},
  "situation": {"score": X, "insight": "..."},
  "task": {"score": X, "insight": "..."},
  "action": {"score": X, "insight": "..."},
  "result": {"score": X, "insight": "..."},
  "strengths": ["...", "..."],
  "growthAreas": ["...", "..."]
}
"""
```
