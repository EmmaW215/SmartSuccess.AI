# MatchWise Extension Plan
## Adding RAG & Voice Mock Interview to Your Existing System

---

## Phase 1: RAG Layer (Week 1)
### Goal: Enable context-aware retrieval for personalized interviews

### 1.1 Backend Changes

#### New Dependencies (add to requirements.txt)
```txt
# Vector Store & Embeddings
chromadb>=0.4.0
sentence-transformers>=2.2.0
# OR for cloud deployment:
pinecone-client>=3.0.0
openai>=1.0.0  # Already have this - for embeddings

# Interview Support
groq>=0.4.0    # Fast LLM for real-time voice
```

#### New File Structure
```
resume-matcher-backend/
├── main.py                    # Existing - add new routes
├── requirements.txt           # Update with new deps
│
├── services/                  # NEW FOLDER
│   ├── __init__.py
│   ├── embedding_service.py   # Embedding generation
│   ├── vector_store.py        # ChromaDB/Pinecone operations
│   ├── rag_service.py         # RAG query logic
│   └── interview_service.py   # Interview state machine
│
├── models/                    # NEW FOLDER
│   ├── __init__.py
│   └── schemas.py             # Pydantic models
│
└── prompts/                   # NEW FOLDER
    ├── __init__.py
    └── interview_prompts.py   # Interview question templates
```

#### embedding_service.py
```python
import os
from typing import List
import openai

class EmbeddingService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"  # $0.02/1M tokens
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        return chunks
```

#### vector_store.py (ChromaDB - Free, Local)
```python
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import os

class VectorStore:
    def __init__(self):
        # Persistent storage path
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
        
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
    
    def get_or_create_collection(self, user_id: str):
        """Get or create a collection for a specific user"""
        collection_name = f"user_{user_id.replace('-', '_')}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def upsert_documents(
        self, 
        user_id: str, 
        documents: List[str], 
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: List[str]
    ):
        """Add or update documents in user's collection"""
        collection = self.get_or_create_collection(user_id)
        collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    async def query(
        self, 
        user_id: str, 
        query_embedding: List[float], 
        n_results: int = 5
    ) -> Dict:
        """Query similar documents from user's collection"""
        collection = self.get_or_create_collection(user_id)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return results
    
    def delete_user_collection(self, user_id: str):
        """Delete a user's entire collection"""
        collection_name = f"user_{user_id.replace('-', '_')}"
        try:
            self.client.delete_collection(collection_name)
        except ValueError:
            pass  # Collection doesn't exist
```

#### rag_service.py
```python
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from typing import Dict, List, Optional
import uuid

class RAGService:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.vector_store = VectorStore()
    
    async def build_user_context(
        self, 
        user_id: str, 
        resume_text: str, 
        job_text: str
    ) -> Dict:
        """Build RAG context from resume and job posting"""
        
        # Chunk the documents
        resume_chunks = self.embedder.chunk_text(resume_text, chunk_size=300)
        job_chunks = self.embedder.chunk_text(job_text, chunk_size=300)
        
        # Prepare documents with metadata
        all_chunks = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(resume_chunks):
            all_chunks.append(chunk)
            metadatas.append({"source": "resume", "chunk_index": i})
            ids.append(f"resume_{i}_{uuid.uuid4().hex[:8]}")
        
        for i, chunk in enumerate(job_chunks):
            all_chunks.append(chunk)
            metadatas.append({"source": "job_posting", "chunk_index": i})
            ids.append(f"job_{i}_{uuid.uuid4().hex[:8]}")
        
        # Generate embeddings
        embeddings = await self.embedder.embed_batch(all_chunks)
        
        # Store in vector database
        await self.vector_store.upsert_documents(
            user_id=user_id,
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return {
            "status": "success",
            "resume_chunks": len(resume_chunks),
            "job_chunks": len(job_chunks),
            "total_chunks": len(all_chunks)
        }
    
    async def query_context(
        self, 
        user_id: str, 
        query: str, 
        n_results: int = 5,
        source_filter: Optional[str] = None
    ) -> str:
        """Retrieve relevant context for a query"""
        
        # Embed the query
        query_embedding = await self.embedder.embed_text(query)
        
        # Search vector store
        results = await self.vector_store.query(
            user_id=user_id,
            query_embedding=query_embedding,
            n_results=n_results
        )
        
        # Filter by source if specified
        context_parts = []
        if results["documents"] and results["documents"][0]:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                if source_filter is None or meta.get("source") == source_filter:
                    source_label = meta.get("source", "unknown").upper()
                    context_parts.append(f"[{source_label}]: {doc}")
        
        return "\n\n".join(context_parts)
```

### 1.2 Update main.py - Add RAG Endpoints

```python
# Add to existing main.py imports
from services.rag_service import RAGService

# Initialize RAG service
rag_service = RAGService()

# NEW ENDPOINT: Build user context
@app.post("/api/build-context")
async def build_context(
    user_id: str = Form(...),
    job_text: str = Form(...),
    resume: UploadFile = File(...)
):
    """Build RAG context from resume and job posting"""
    try:
        # Extract resume text (reuse existing logic)
        resume_text = ""
        if resume.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume)
        elif resume.filename.endswith((".doc", ".docx")):
            resume_text = extract_text_from_docx(resume)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Unsupported file format"}
            )
        
        # Build RAG context
        result = await rag_service.build_user_context(
            user_id=user_id,
            resume_text=resume_text,
            job_text=job_text
        )
        
        return JSONResponse(content={
            "status": "success",
            "message": "Context built successfully",
            "details": result
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to build context: {str(e)}"}
        )

# NEW ENDPOINT: Query context (for testing)
@app.post("/api/query-context")
async def query_context(
    user_id: str = Form(...),
    query: str = Form(...)
):
    """Query the RAG context"""
    try:
        context = await rag_service.query_context(user_id, query)
        return JSONResponse(content={
            "context": context
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Query failed: {str(e)}"}
        )
```

---

## Phase 2: Voice Interview Agent (Week 2)
### Goal: Real-time voice mock interview with RAG context

### 2.1 Interview Service

#### services/interview_service.py
```python
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import os
from groq import AsyncGroq
from services.rag_service import RAGService

class InterviewSection(Enum):
    GREETING = "greeting"
    MENU = "menu"
    SELF_INTRO = "self_intro"
    TECHNICAL = "technical"
    SOFT_SKILL = "soft_skill"

@dataclass
class InterviewSession:
    session_id: str
    user_id: str
    current_section: InterviewSection = InterviewSection.GREETING
    question_index: int = 0
    messages: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

class InterviewService:
    def __init__(self):
        self.rag_service = RAGService()
        self.groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.sessions: Dict[str, InterviewSession] = {}
        
        # Question banks
        self.self_intro_questions = [
            "Please introduce yourself briefly.",
            "Why did you leave or why are you looking to leave your current position?",
            "What interests you about this particular role?",
            "What makes you the best fit for this position?",
            "What would you say are your greatest strengths and areas for improvement?"
        ]
    
    async def create_session(self, session_id: str, user_id: str) -> InterviewSession:
        """Create a new interview session"""
        session = InterviewSession(session_id=session_id, user_id=user_id)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get an existing session"""
        return self.sessions.get(session_id)
    
    async def get_greeting(self) -> str:
        return (
            "Welcome to your Mock Interview! I'm your AI interviewer today. "
            "I've reviewed your resume and the job requirements. "
            "When you're ready to begin, just say 'I'm ready' or 'Yes'."
        )
    
    async def get_menu(self) -> str:
        return (
            "Great! Please choose an interview section:\n\n"
            "1. Self-Introduction - Tell me about yourself and your background\n"
            "2. Technical Questions - Based on your skills and the job requirements\n"
            "3. Soft-Skill Questions - Behavioral and situational questions\n\n"
            "Just say the number or the section name. "
            "You can say 'STOP' at any time to return to this menu."
        )
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str
    ) -> Dict:
        """Process user message and return AI response"""
        
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Record user message
        session.add_message("user", user_message)
        
        # Check for STOP command
        if "stop" in user_message.lower():
            session.current_section = InterviewSection.MENU
            session.question_index = 0
            response = "No problem! Let's take a break.\n\n" + await self.get_menu()
            session.add_message("assistant", response)
            return {
                "response": response,
                "section": session.current_section.value,
                "is_complete": False
            }
        
        # State machine logic
        response = ""
        is_complete = False
        
        if session.current_section == InterviewSection.GREETING:
            if self._is_ready(user_message):
                session.current_section = InterviewSection.MENU
                response = await self.get_menu()
            else:
                response = "Just let me know when you're ready to start!"
        
        elif session.current_section == InterviewSection.MENU:
            section = self._parse_section_choice(user_message)
            if section:
                session.current_section = section
                session.question_index = 0
                response = await self._get_next_question(session)
            else:
                response = "I didn't catch that. Please say 1, 2, or 3, or the section name."
        
        else:
            # In an interview section
            feedback = await self._generate_feedback(session, user_message)
            session.question_index += 1
            
            if session.question_index >= 5:
                # Section complete
                session.current_section = InterviewSection.MENU
                session.question_index = 0
                response = (
                    f"{feedback}\n\n"
                    "🎉 Congratulations! You've completed this section. "
                    "You did a great job! Feel free to download your transcript "
                    "or continue with another section.\n\n"
                    + await self.get_menu()
                )
            else:
                next_question = await self._get_next_question(session)
                response = f"{feedback}\n\n{next_question}"
        
        session.add_message("assistant", response)
        
        return {
            "response": response,
            "section": session.current_section.value,
            "question_index": session.question_index,
            "is_complete": is_complete
        }
    
    async def _get_next_question(self, session: InterviewSession) -> str:
        """Generate the next interview question"""
        
        if session.current_section == InterviewSection.SELF_INTRO:
            if session.question_index < len(self.self_intro_questions):
                return self.self_intro_questions[session.question_index]
            return "Tell me more about your career goals."
        
        elif session.current_section == InterviewSection.TECHNICAL:
            # Use RAG to generate contextual technical questions
            context = await self.rag_service.query_context(
                session.user_id,
                "technical skills requirements tools platforms experience",
                n_results=3
            )
            
            prompt = f"""Based on this candidate's background and job requirements:

{context}

Generate ONE technical interview question that:
1. References a specific skill or experience from their resume
2. Relates to the job requirements
3. Asks about challenges, achievements, or practical application
4. Is conversational and encouraging

Question #{session.question_index + 1} of 5. 
Previously asked about: {self._get_previous_topics(session)}

Return ONLY the question, no preamble."""

            return await self._call_groq(prompt)
        
        elif session.current_section == InterviewSection.SOFT_SKILL:
            context = await self.rag_service.query_context(
                session.user_id,
                "soft skills teamwork communication leadership collaboration",
                n_results=3
            )
            
            prompt = f"""Based on these job requirements:

{context}

Generate ONE behavioral/soft-skill interview question using the STAR method format.
Focus on: teamwork, communication, problem-solving, leadership, or adaptability.

Question #{session.question_index + 1} of 5.
Previously asked about: {self._get_previous_topics(session)}

Return ONLY the question, no preamble."""

            return await self._call_groq(prompt)
        
        return "Tell me more about your experience."
    
    async def _generate_feedback(self, session: InterviewSession, answer: str) -> str:
        """Generate positive feedback on user's answer"""
        
        prompt = f"""The candidate answered an interview question. Provide brief, 
encouraging feedback (2-3 sentences max). Be specific but positive. 
Focus on what they did well.

Their answer: {answer[:500]}

Feedback:"""
        
        return await self._call_groq(prompt)
    
    async def _call_groq(self, prompt: str) -> str:
        """Call Groq API for fast inference"""
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful, encouraging interview coach."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Fallback to simpler response
            return "That's a great point. Can you elaborate on that?"
    
    def _is_ready(self, message: str) -> bool:
        ready_phrases = ["ready", "yes", "let's go", "start", "begin", "ok", "okay"]
        return any(phrase in message.lower() for phrase in ready_phrases)
    
    def _parse_section_choice(self, message: str) -> Optional[InterviewSection]:
        msg = message.lower()
        if "1" in msg or "self" in msg or "intro" in msg:
            return InterviewSection.SELF_INTRO
        elif "2" in msg or "technical" in msg or "tech" in msg:
            return InterviewSection.TECHNICAL
        elif "3" in msg or "soft" in msg or "behavior" in msg:
            return InterviewSection.SOFT_SKILL
        return None
    
    def _get_previous_topics(self, session: InterviewSession) -> str:
        # Extract topics from previous questions in this section
        topics = []
        for msg in session.messages[-10:]:
            if msg["role"] == "assistant" and "?" in msg["content"]:
                topics.append(msg["content"][:50])
        return ", ".join(topics) if topics else "None yet"
```

### 2.2 Add Interview Endpoints to main.py

```python
# Add to imports
from services.interview_service import InterviewService
import uuid

# Initialize
interview_service = InterviewService()

# Interview endpoints
@app.post("/api/interview/start")
async def start_interview(user_id: str = Form(...)):
    """Start a new interview session"""
    try:
        session_id = str(uuid.uuid4())
        session = await interview_service.create_session(session_id, user_id)
        greeting = await interview_service.get_greeting()
        session.add_message("assistant", greeting)
        
        return JSONResponse(content={
            "session_id": session_id,
            "message": greeting,
            "section": "greeting"
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/interview/message")
async def interview_message(
    session_id: str = Form(...),
    message: str = Form(...)
):
    """Send a message in the interview"""
    try:
        result = await interview_service.process_message(session_id, message)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/interview/history/{session_id}")
async def get_interview_history(session_id: str):
    """Get the full interview transcript"""
    try:
        session = interview_service.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
        
        return JSONResponse(content={
            "session_id": session_id,
            "messages": session.messages,
            "current_section": session.current_section.value
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
```

---

## Phase 3: Frontend Voice Integration (Week 3)
### Goal: Voice-enabled chat interface

### 3.1 New Interview Page

Create `resume-matcher-frontend/src/app/interview/page.tsx`:

```typescript
"use client";

import { useState, useEffect, useRef, useCallback } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export default function InterviewPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [userId] = useState("demo-user"); // Replace with actual auth
  
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "https://your-backend.onrender.com";

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        
        recognitionRef.current.onresult = (event) => {
          let interimTranscript = "";
          let finalTranscript = "";
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }
          
          setTranscript(finalTranscript || interimTranscript);
          
          if (finalTranscript) {
            handleSendMessage(finalTranscript);
            setTranscript("");
          }
        };
        
        recognitionRef.current.onerror = (event) => {
          console.error("Speech recognition error:", event.error);
          setIsListening(false);
        };
      }
      
      synthRef.current = window.speechSynthesis;
    }
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Start interview session
  const startInterview = async () => {
    try {
      const formData = new FormData();
      formData.append("user_id", userId);
      
      const response = await fetch(`${BACKEND_URL}/api/interview/start`, {
        method: "POST",
        body: formData,
      });
      
      const data = await response.json();
      setSessionId(data.session_id);
      
      const welcomeMessage: Message = {
        role: "assistant",
        content: data.message,
        timestamp: new Date().toISOString(),
      };
      setMessages([welcomeMessage]);
      
      // Speak the greeting
      speak(data.message);
    } catch (error) {
      console.error("Failed to start interview:", error);
    }
  };

  // Send message to backend
  const handleSendMessage = async (text: string) => {
    if (!sessionId || !text.trim()) return;
    
    // Add user message to chat
    const userMessage: Message = {
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const formData = new FormData();
      formData.append("session_id", sessionId);
      formData.append("message", text);
      
      const response = await fetch(`${BACKEND_URL}/api/interview/message`, {
        method: "POST",
        body: formData,
      });
      
      const data = await response.json();
      
      // Add assistant response
      const assistantMessage: Message = {
        role: "assistant",
        content: data.response,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // Speak the response
      speak(data.response);
    } catch (error) {
      console.error("Failed to send message:", error);
    }
  };

  // Text-to-speech
  const speak = (text: string) => {
    if (!synthRef.current) return;
    
    // Cancel any ongoing speech
    synthRef.current.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    
    synthRef.current.speak(utterance);
  };

  // Toggle microphone
  const toggleListening = () => {
    if (!recognitionRef.current) return;
    
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  // Download transcript
  const downloadTranscript = () => {
    const text = messages.map(m => 
      `[${m.role.toUpperCase()}]: ${m.content}`
    ).join("\n\n");
    
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `interview-transcript-${sessionId}.txt`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-t-2xl shadow-lg p-6 border-b">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-blue-600">Mock Interview</h1>
              <p className="text-gray-500">AI-Powered Interview Practice</p>
            </div>
            <div className="flex gap-3">
              <a 
                href="/" 
                className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                ← Back to Main
              </a>
              {messages.length > 0 && (
                <button
                  onClick={downloadTranscript}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                >
                  Download Transcript
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* Chat Area */}
        <div className="bg-white shadow-lg min-h-[500px] max-h-[600px] overflow-y-auto p-6">
          {!sessionId ? (
            <div className="flex flex-col items-center justify-center h-full">
              <div className="text-6xl mb-6">🎤</div>
              <h2 className="text-xl font-semibold mb-4">Ready for your mock interview?</h2>
              <p className="text-gray-500 mb-6 text-center max-w-md">
                Practice answering interview questions with our AI interviewer. 
                Your responses will be based on your resume and the job you're applying for.
              </p>
              <button
                onClick={startInterview}
                className="px-8 py-4 bg-blue-600 text-white rounded-xl text-lg font-semibold hover:bg-blue-700 transition"
              >
                Start Interview
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] p-4 rounded-2xl ${
                      message.role === "user"
                        ? "bg-blue-600 text-white rounded-br-md"
                        : "bg-gray-100 text-gray-800 rounded-bl-md"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
        
        {/* Voice Controls */}
        {sessionId && (
          <div className="bg-white rounded-b-2xl shadow-lg p-6 border-t">
            <div className="flex items-center justify-center gap-4">
              {/* Microphone Button */}
              <button
                onClick={toggleListening}
                className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                  isListening
                    ? "bg-red-500 animate-pulse"
                    : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                <span className="text-white text-2xl">
                  {isListening ? "🔴" : "🎤"}
                </span>
              </button>
              
              {/* Status Indicators */}
              <div className="text-center">
                {isListening && (
                  <p className="text-red-500 font-medium">Listening...</p>
                )}
                {isSpeaking && (
                  <p className="text-blue-500 font-medium">Speaking...</p>
                )}
                {transcript && (
                  <p className="text-gray-500 italic">"{transcript}"</p>
                )}
                {!isListening && !isSpeaking && !transcript && (
                  <p className="text-gray-400">Click the mic to speak</p>
                )}
              </div>
            </div>
            
            {/* Text Input Fallback */}
            <div className="mt-4">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const input = e.currentTarget.elements.namedItem("message") as HTMLInputElement;
                  if (input.value.trim()) {
                    handleSendMessage(input.value);
                    input.value = "";
                  }
                }}
                className="flex gap-2"
              >
                <input
                  type="text"
                  name="message"
                  placeholder="Or type your response here..."
                  className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Send
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
```

### 3.2 Add Interview Button to Main Page

Update `resume-matcher-frontend/src/app/page.tsx` - add after the analysis results:

```typescript
{/* Add this after your existing results section */}
<div className="mt-8 text-center">
  <a
    href="/interview"
    className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl text-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition shadow-lg"
  >
    🎤 Start Mock Interview
  </a>
  <p className="text-gray-500 mt-2">
    Practice answering questions based on your resume and job posting
  </p>
</div>
```

---

## Environment Variables

### Backend (.env or Render Environment)
```
OPENAI_API_KEY=sk-xxx
GROQ_API_KEY=gsk_xxx
XAI_API_KEY=xxx  # Existing
CHROMA_PERSIST_DIR=./chroma_data
```

### Frontend (.env.local or Vercel Environment)
```
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
```

---

## Deployment Checklist

### Backend (Render)
1. Add new dependencies to requirements.txt
2. Add GROQ_API_KEY to environment variables
3. Ensure persistent disk for ChromaDB (or switch to Pinecone for stateless)
4. Redeploy

### Frontend (Vercel)
1. Add new interview page
2. Update NEXT_PUBLIC_BACKEND_URL if needed
3. Redeploy

---

## Testing Plan

### Phase 1 Tests (RAG)
```bash
# Test context building
curl -X POST https://your-backend/api/build-context \
  -F "user_id=test123" \
  -F "job_text=We need a Python developer..." \
  -F "resume=@test_resume.pdf"

# Test context query
curl -X POST https://your-backend/api/query-context \
  -F "user_id=test123" \
  -F "query=Python experience"
```

### Phase 2 Tests (Interview)
```bash
# Start interview
curl -X POST https://your-backend/api/interview/start \
  -F "user_id=test123"

# Send message
curl -X POST https://your-backend/api/interview/message \
  -F "session_id=xxx" \
  -F "message=Yes, I'm ready"
```

---

## Cost Estimate

| Service | Free Tier | Estimated Cost |
|---------|-----------|----------------|
| OpenAI Embeddings | - | ~$0.02/1M tokens |
| Groq LLM | 6K req/day free | $0 |
| ChromaDB | Self-hosted | $0 |
| Render | 750 hrs/mo | $0 |
| Vercel | 100GB | $0 |

**Monthly estimate: $0-5** for moderate usage
