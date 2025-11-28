# ============================================================
# ADD THESE TO YOUR EXISTING main.py in resume-matcher-backend
# ============================================================

# 1. ADD TO IMPORTS (at the top of main.py)
# ============================================================
import uuid
from services.rag_service import RAGService
from services.interview_service import InterviewService
from services.feedback_service import FeedbackService

# 2. INITIALIZE SERVICES (after app = FastAPI())
# ============================================================
rag_service = RAGService()
interview_service = InterviewService()
feedback_service = FeedbackService()

# 3. ADD RAG ENDPOINTS
# ============================================================

@app.post("/api/build-context")
async def build_context(
    user_id: str = Form(...),
    job_text: str = Form(...),
    resume: UploadFile = File(...)
):
    """Build RAG context from resume and job posting for personalized interviews"""
    try:
        # Extract resume text (reuse existing logic)
        resume_text = ""
        if resume.filename and resume.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume)
        elif resume.filename and resume.filename.endswith((".doc", ".docx")):
            resume_text = extract_text_from_docx(resume)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Unsupported file format. Please upload PDF or DOCX."}
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


@app.post("/api/query-context")
async def query_context(
    user_id: str = Form(...),
    query: str = Form(...)
):
    """Query the RAG context for relevant information"""
    try:
        context = await rag_service.query_context(user_id, query)
        return JSONResponse(content={"context": context})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Query failed: {str(e)}"}
        )


# 4. ADD INTERVIEW ENDPOINTS
# ============================================================

@app.post("/api/interview/start")
async def start_interview(user_id: str = Form(...)):
    """Start a new mock interview session"""
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
    """Send a message in the interview and get response with feedback"""
    try:
        # Get interview response
        result = await interview_service.process_message(session_id, message)
        
        # Get the session to access user_id
        session = interview_service.get_session(session_id)
        if session:
            # Get the last question (before this response)
            last_question = ""
            for msg in reversed(session.messages[:-2]):  # Skip last user msg and assistant response
                if msg["role"] == "assistant" and "?" in msg["content"]:
                    last_question = msg["content"]
                    break
            
            # Generate STAR feedback if there was a question
            if last_question and message.lower() not in ["yes", "ready", "1", "2", "3", "stop"]:
                feedback = await feedback_service.analyze_response(
                    session_id=session_id,
                    user_id=session.user_id,
                    question=last_question,
                    response=message
                )
                result["feedback"] = feedback.to_dict()
                
                # Get session summary
                summary = feedback_service.get_session_summary(session_id)
                if summary:
                    result["sessionFeedback"] = summary.to_dict()
        
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/interview/history/{session_id}")
async def get_interview_history(session_id: str):
    """Get the full interview transcript and feedback"""
    try:
        session = interview_service.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
        
        # Get feedback summary
        feedback_summary = feedback_service.get_session_summary(session_id)
        
        return JSONResponse(content={
            "session_id": session_id,
            "messages": session.messages,
            "current_section": session.current_section.value,
            "feedback": feedback_summary.to_dict() if feedback_summary else None
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/api/interview/feedback/{session_id}")
async def get_final_feedback(session_id: str):
    """Get final aggregated feedback for completed interview"""
    try:
        summary = feedback_service.get_session_summary(session_id)
        if not summary:
            return JSONResponse(
                status_code=404,
                content={"error": "No feedback found for this session"}
            )
        
        return JSONResponse(content=summary.to_dict())
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/interview/analytics/{user_id}")
async def get_user_analytics(user_id: str):
    """Get analytics across all user's interview sessions"""
    try:
        # Get all sessions for this user
        user_sessions = [
            s for s in feedback_service.session_feedback.values() 
            if s.user_id == user_id
        ]
        
        if not user_sessions:
            return JSONResponse(content={
                "totalSessions": 0,
                "averageScore": 0,
                "improvementTrend": [],
                "topStrengths": [],
                "focusAreas": []
            })
        
        # Calculate analytics
        scores = [s.overall_score for s in user_sessions]
        all_strengths = []
        all_growth = []
        
        for s in user_sessions:
            all_strengths.extend(s.aggregated_strengths)
            all_growth.extend(s.aggregated_growth_areas)
        
        # Get most common
        from collections import Counter
        top_strengths = [item for item, _ in Counter(all_strengths).most_common(5)]
        focus_areas = [item for item, _ in Counter(all_growth).most_common(5)]
        
        return JSONResponse(content={
            "totalSessions": len(user_sessions),
            "averageScore": round(sum(scores) / len(scores), 1),
            "improvementTrend": scores[-10:],  # Last 10 sessions
            "topStrengths": top_strengths,
            "focusAreas": focus_areas
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# 5. UPDATED REQUIREMENTS.TXT
# ============================================================
"""
Add these to your requirements.txt:

# Vector Store & Embeddings
chromadb>=0.4.0
sentence-transformers>=2.2.0

# Interview Support
groq>=0.4.0

# Existing deps (keep these)
fastapi
uvicorn
python-multipart
requests
beautifulsoup4
PyPDF2
python-docx
aiohttp
openai>=1.0.0
stripe
firebase-admin
python-dotenv
"""

# 6. ENVIRONMENT VARIABLES NEEDED
# ============================================================
"""
Add to Render environment variables:

OPENAI_API_KEY=sk-xxx          # Already have
XAI_API_KEY=xxx                # Already have
GROQ_API_KEY=gsk_xxx           # NEW - get from console.groq.com
CHROMA_PERSIST_DIR=./chroma_data
"""
