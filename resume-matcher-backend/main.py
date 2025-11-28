from fastapi import FastAPI, UploadFile, File, Form, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
from bs4 import BeautifulSoup
import PyPDF2
from docx import Document
import io
import aiohttp
import json
import os
import openai
import uuid
from pathlib import Path
from datetime import datetime

import stripe

# Import Interview Services
try:
    from services import RAGService, InterviewService, FeedbackService
    from models import (
        BuildContextRequest, BuildContextResponse,
        InterviewStartResponse, InterviewMessageRequest, InterviewMessageResponse
    )
    INTERVIEW_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Interview services not available: {e}")
    INTERVIEW_SERVICES_AVAILABLE = False

from dotenv import load_dotenv
load_dotenv()
import os
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Initialize Firebase with error handling for missing key
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Warning: Firebase initialization failed: {e}")
    # Mock db for development if needed, or handle gracefully
    db = None

app = FastAPI()  # 必须在最前面

# Initialize Interview Services (if available)
rag_service = None
interview_service = None
feedback_service = None

if INTERVIEW_SERVICES_AVAILABLE:
    try:
        rag_service = RAGService()
        interview_service = InterviewService()
        feedback_service = FeedbackService()
        print("✅ Interview services initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize interview services: {e}")
        INTERVIEW_SERVICES_AVAILABLE = False

# --- Visitor Counter Storage ---
VISITOR_COUNT_FILE = Path("visitor_count.json")

def get_visitor_count() -> int:
    """Get current visitor count from file"""
    try:
        if VISITOR_COUNT_FILE.exists():
            with open(VISITOR_COUNT_FILE, 'r') as f:
                data = json.load(f)
                return data.get('count', 0)
    except Exception as e:
        print(f"Error reading visitor count: {e}")
    return 0

def save_visitor_count(count: int):
    """Save visitor count to file"""
    try:
        with open(VISITOR_COUNT_FILE, 'w') as f:
            json.dump({'count': count, 'updated_at': datetime.now().isoformat()}, f)
    except Exception as e:
        print(f"Error saving visitor count: {e}")

# Initialize count if file doesn't exist
if not VISITOR_COUNT_FILE.exists():
    save_visitor_count(100)  # Start with a base number

@app.get("/api/visitor/count")
async def get_visitor_count_endpoint():
    """Get current visitor count"""
    count = get_visitor_count()
    return JSONResponse(content={"count": count})

@app.post("/api/visitor/increment")
async def increment_visitor_count():
    """Increment and return visitor count"""
    current_count = get_visitor_count()
    new_count = current_count + 1
    save_visitor_count(new_count)
    return JSONResponse(content={"count": new_count})

# 统一的用户状态管理
class UserStatus:
    def __init__(self, uid: str):
        self.uid = uid
        self.user_ref = db.collection("users").document(uid) if db else None
        self.now_month = datetime.now().strftime("%Y-%m")
    
    def get_status(self):
        """获取用户完整状态"""
        if not self.user_ref:
            return self._get_default_status()
            
        try:
            doc = self.user_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return self._process_user_data(data)
            else:
                return self._get_default_status()
        except Exception as e:
            print(f"Error getting user status: {e}")
            return self._get_default_status()
    
    def _process_user_data(self, data):
        """处理用户数据，包括跨月重置"""
        lastScanMonth = data.get("lastScanMonth", "")
        scansUsed = data.get("scansUsed", 0)
        
        # 跨月自动重置
        # if lastScanMonth != self.now_month:
        #     scansUsed = 0
        #     self.user_ref.set({
        #         "scansUsed": 0,
        #         "lastScanMonth": self.now_month
        #     }, merge=True)
        
        subscription_end = data.get("subscriptionEnd")
        is_subscription_active = True
        if subscription_end:
            try:
                is_subscription_active = datetime.utcnow() < datetime.fromisoformat(subscription_end)
            except Exception:
                is_subscription_active = False

        return {
            "trialUsed": data.get("trialUsed", False),
            "isUpgraded": data.get("isUpgraded", False),
            "planType": data.get("planType"),
            "scanLimit": data.get("scanLimit"),
            "scansUsed": scansUsed,
            "lastScanMonth": self.now_month,
            "subscriptionActive": is_subscription_active,
            "subscriptionEnd": subscription_end,
        }
    
    def _get_default_status(self):
        """获取默认状态"""
        return {
            "trialUsed": False,
            "isUpgraded": False,
            "planType": None,
            "scanLimit": None,
            "scansUsed": 0,
            "lastScanMonth": self.now_month
        }
    
    def can_generate(self):
        """检查用户是否可以生成分析"""
        status = self.get_status()
        
        # 新用户或未使用试用
        if not status["trialUsed"]:
            return True, "trial_available"
        
        # 已升级用户
        if status["isUpgraded"]:
            # 新增订阅有效期判断
            if "subscriptionActive" in status and not status["subscriptionActive"]:
                return False, "subscription_expired"
            if status["scanLimit"] is None:
                return True, "unlimited"
            if status["scansUsed"] < status["scanLimit"]:
                return True, "subscription_available"
            else:
                return False, "subscription_limit_reached"
        
        # 试用已用但未升级
        return False, "trial_used"
    
    def mark_trial_used(self):
        """标记试用已使用"""
        if self.user_ref:
            self.user_ref.set({"trialUsed": True}, merge=True)
    
    def increment_scan_count(self):
        """增加扫描次数"""
        if not self.user_ref:
            return
            
        status = self.get_status()
        if status["isUpgraded"] and status["scanLimit"] is not None:
            self.user_ref.set({
                "scansUsed": status["scansUsed"] + 1,
                "lastScanMonth": self.now_month
            }, merge=True)

# 查询用户完整状态（试用、订阅、使用次数）
@app.get("/api/user/status")
async def get_user_status(uid: str = Query(...)):
    try:
        user_status = UserStatus(uid)
        return user_status.get_status()
    except Exception as e:
        return {"error": str(e)}

# 检查用户是否可以生成分析
@app.get("/api/user/can-generate")
async def can_generate(uid: str = Query(...)):
    try:
        user_status = UserStatus(uid)
        can_gen, reason = user_status.can_generate()
        return {
            "canGenerate": can_gen,
            "reason": reason,
            "status": user_status.get_status()
        }
    except Exception as e:
        return {"error": str(e)}

# CORS configuration - support multiple domains
allowed_origins = [
    "https://matchwise-ai.vercel.app",
    "https://smartsuccess-ai.vercel.app",
    "http://localhost:3000",  # For local development
    "http://localhost:3001",  # Alternative local port
    "http://127.0.0.1:3000",
    "http://192.168.86.47:3000"
]

# Allow environment variable override
if os.getenv("ALLOWED_ORIGINS"):
    additional_origins = os.getenv("ALLOWED_ORIGINS")
    if additional_origins:
        allowed_origins.extend(additional_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def call_xai_api(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise Exception("XAI_API_KEY not set in environment variables")
    
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "grok-3",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000
        }
        try:
            async with session.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"xAI API 调用失败，状态码: {response.status}, 错误信息: {error_text}")
                    raise Exception(f"xAI API error: {response.status} - {error_text}")
                result = await response.json()
                return result["choices"][0]["message"]["content"]
        except aiohttp.ClientError as e:
            print(f"xAI API 网络请求异常: {str(e)}")
            raise Exception(f"xAI API request failed: {str(e)}")

async def call_openai_api(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY not set in environment variables")
    
    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # 使用更通用的模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content.strip() if response.choices[0].message.content else ""
    except Exception as e:
        raise Exception(f"OpenAI API request failed: {str(e)}")

async def generate_mock_ai_response(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    if "job posting" in prompt.lower() and "summarize" in prompt.lower():
        return """
<p><b>This is a mock result due to AI not being called!</b></p>
<p><b>Skills & Technical Expertise:</b></p>
<ul>
<li>Technical program management (Agile, Scrum, Kanban)</li>
<li>Software development lifecycle & modern architecture principles</li>
</ul>
"""
    else:
        return "<p>AI analysis completed successfully. Please review the generated content.</p>"

async def call_ai_api(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    """智能AI服务选择器：优先使用OpenAI，失败时自动切换到xAI，最后使用本地模拟"""
    # 首先尝试OpenAI
    try:
        return await call_openai_api(prompt, system_prompt)
    except Exception as openai_error:
        # 如果OpenAI失败（配额不足等），尝试xAI
        try:
            print(f"OpenAI失败，切换到xAI: {str(openai_error)}")
            return await call_xai_api(prompt, system_prompt)
        except Exception as xai_error:
            # 如果xAI也失败，使用本地模拟AI
            print(f"xAI也失败，使用本地模拟AI: {str(xai_error)}")
            return await generate_mock_ai_response(prompt, system_prompt)

def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        content = file.file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract PDF text: {str(e)}")

def extract_text_from_docx(file: UploadFile) -> str:
    try:
        content = file.file.read()
        doc = Document(io.BytesIO(content))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract DOCX text: {str(e)}")

def extract_text_from_url(url: str) -> str:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        full_text = soup.get_text(separator=" ", strip=True)
        return full_text
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch job posting: {str(e)}")

async def compare_texts(job_text: str, resume_text: str) -> dict:
    try:
        # a. Job Summary
        job_summary_prompt = (
            "Please read the following job posting content:\n\n"
            f"{job_text}\n\n"
            "Summarize the job descriptions..."
        )
        job_summary = await call_ai_api(job_summary_prompt)
        job_summary = f"\n\n {job_summary}"

        # b. Resume Summary with Comparison Table
        resume_summary_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job summary:\n\n"
            f"{job_summary}\n\n"
            "Output a comparison table..."
        )
        resume_summary = await call_ai_api(resume_summary_prompt)
        resume_summary = f"\n\n{resume_summary}"

        import re
        lines = resume_summary.strip().splitlines()
        match_score_test = None
        if lines:
            last_line = lines[-1].strip()
            match = re.search(r"([0-9]+(?:\.[0-9]+)?)", last_line)
            if match:
                match_score_test = float(match.group(1))
                if match_score_test <= 1:
                    match_score_test = round(match_score_test * 100, 2)
            else:
                match_score_test = last_line

        try:
            match_score = float(match_score_test.strip().replace("%", "")) if match_score_test else 0
        except Exception:
            match_score = 0

        # d. Tailored Resume Summary
        tailored_resume_summary_prompt = (
            "Provide a revised one-paragraph summary..."
        )
        tailored_resume_summary = await call_ai_api(tailored_resume_summary_prompt)
        tailored_resume_summary = f"\n{tailored_resume_summary}"

        # e. Tailored Work Experience
        tailored_work_experience_prompt = (
            "Find the latest work experiences..."
        )
        tailored_work_experience_html = await call_ai_api(tailored_work_experience_prompt)
        
        # Process output to list
        tailored_work_experience = []
        # Simple processing, assuming AI returns HTML list
        soup = BeautifulSoup(tailored_work_experience_html, "html.parser")
        for li in soup.find_all("li"):
            tailored_work_experience.append(li.get_text())

        # f. Cover Letter
        cover_letter_prompt = (
            "Provide a formal cover letter..."
        )
        cover_letter = await call_ai_api(cover_letter_prompt)
        cover_letter = f"\n{cover_letter}"

        return {
            "job_summary": job_summary,
            "resume_summary": resume_summary,
            "match_score": match_score,
            "tailored_resume_summary": tailored_resume_summary,
            "tailored_work_experience": tailored_work_experience,
            "cover_letter": cover_letter,
        }
    except Exception as e:
        raise Exception(f"Comparison failed: {str(e)}")

@app.post("/api/compare")
async def compare(job_text: str = Form(...), resume: UploadFile = File(...), uid: str = Form(None)):
    try:
        # 1. 检查用户权限
        if uid:
            user_status = UserStatus(uid)
            can_gen, reason = user_status.can_generate()
            
            if not can_gen:
                return JSONResponse(
                    status_code=403, 
                    content={"error": "Trial ended or limit reached."}
                )
        
        # 2. 处理简历文件
        resume_text = ""
        if resume.filename and resume.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume)
        elif resume.filename and resume.filename.endswith((".doc", ".docx")):
            resume_text = extract_text_from_docx(resume)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Unsupported file format. Please upload PDF or DOCX."},
            )
        
        # 3. 调用AI分析
        result = await compare_texts(job_text, resume_text)
        
        # 4. 更新用户状态
        if uid:
            user_status = UserStatus(uid)
            status = user_status.get_status()
            if not status["trialUsed"]:
                user_status.mark_trial_used()
            if status["isUpgraded"]:
                user_status.increment_scan_count()
        
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing error: {str(e)}"},
        )

@app.post("/api/create-checkout-session")
async def create_checkout_session(uid: str = Form(...), price_id: str = Form(...), mode: str = Form(...)):
    try:
        success_url = "https://matchwise-ai.vercel.app/success?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = "https://matchwise-ai.vercel.app/cancel"
        if mode == "payment":
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"uid": uid}
            )
        elif mode == "subscription":
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"uid": uid}
            )
        else:
            return {"error": "Invalid mode"}
        return {"checkout_url": session.url}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/stripe-webhook")
async def stripe_webhook(request: Request):
    # ... existing webhook code ...
    return {"status": "success"}

@app.get("/")
def root():
    return {"message": "MatchWise Backend API is running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/user/use-trial")
async def use_trial(request: Request):
    data = await request.json()
    return JSONResponse({"success": True, "message": "Trial used."})


# ============================================
# MOCK INTERVIEW API ENDPOINTS
# ============================================

@app.post("/api/interview/build-context")
async def build_interview_context(
    user_id: str = Form(...),
    job_text: str = Form(...),
    resume: UploadFile = File(...)
):
    """Build RAG context from resume and job posting for personalized interview"""
    if not INTERVIEW_SERVICES_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"error": "Interview services not available"}
        )
    
    try:
        # Extract resume text
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


@app.post("/api/interview/start")
async def start_interview(user_id: str = Form(...)):
    """Start a new mock interview session"""
    if not INTERVIEW_SERVICES_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"error": "Interview services not available"}
        )
    
    try:
        session_id = str(uuid.uuid4())
        session = await interview_service.create_session(session_id, user_id)
        greeting = await interview_service.get_greeting()
        session.add_message("assistant", greeting)
        
        return JSONResponse(content={
            "session_id": session_id,
            "message": greeting,
            "section": session.current_section.value
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to start interview: {str(e)}"}
        )


@app.post("/api/interview/message")
async def send_interview_message(
    session_id: str = Form(...),
    message: str = Form(...)
):
    """Send a message in the interview and get AI response"""
    if not INTERVIEW_SERVICES_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"error": "Interview services not available"}
        )
    
    try:
        result = await interview_service.process_message(session_id, message)
        
        if "error" in result:
            return JSONResponse(
                status_code=404,
                content={"error": result["error"]}
            )
        
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process message: {str(e)}"}
        )


@app.get("/api/interview/session/{session_id}")
async def get_interview_session(session_id: str):
    """Get current interview session state"""
    if not INTERVIEW_SERVICES_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"error": "Interview services not available"}
        )
    
    try:
        session = interview_service.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
        
        return JSONResponse(content={
            "session_id": session.session_id,
            "user_id": session.user_id,
            "current_section": session.current_section.value,
            "question_index": session.question_index,
            "message_count": len(session.messages),
            "created_at": session.created_at.isoformat()
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get session: {str(e)}"}
        )


@app.post("/api/interview/analyze-response")
async def analyze_interview_response(
    session_id: str = Form(...),
    user_id: str = Form(...),
    question: str = Form(...),
    response: str = Form(...)
):
    """Analyze a single interview response using STAR method"""
    if not INTERVIEW_SERVICES_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"error": "Interview services not available"}
        )
    
    try:
        # Get job context for better analysis
        job_context = await rag_service.query_context(
            user_id, "job requirements responsibilities", n_results=3
        )
        
        feedback = await feedback_service.analyze_response(
            session_id=session_id,
            user_id=user_id,
            question=question,
            response=response,
            job_context=job_context
        )
        
        return JSONResponse(content=feedback.to_dict())
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to analyze response: {str(e)}"}
        )


@app.get("/api/interview/feedback/{session_id}")
async def get_interview_feedback(session_id: str):
    """Get complete feedback summary for an interview session"""
    if not INTERVIEW_SERVICES_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"error": "Interview services not available"}
        )
    
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
            content={"error": f"Failed to get feedback: {str(e)}"}
        )


@app.get("/api/interview/status")
async def get_interview_service_status():
    """Check if interview services are available"""
    return JSONResponse(content={
        "available": INTERVIEW_SERVICES_AVAILABLE,
        "services": {
            "rag": rag_service is not None,
            "interview": interview_service is not None,
            "feedback": feedback_service is not None
        }
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
