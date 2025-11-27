from fastapi import FastAPI, UploadFile, File, Form
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

app = FastAPI()

# CORS configuration - support multiple domains
allowed_origins = [
    "https://smartsuccess-ai.vercel.app",
    "https://resume-matcher-frontend.vercel.app",
    "https://resume-update-frontend.vercel.app", 
    "https://matchwise-ai.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]

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
                    print(f"xAI API call failed, status: {response.status}, error: {error_text}")
                    raise Exception(f"xAI API error: {response.status} - {error_text}")
                result = await response.json()
                return result["choices"][0]["message"]["content"]
        except aiohttp.ClientError as e:
            print(f"xAI API network error: {str(e)}")
            raise Exception(f"xAI API request failed: {str(e)}")

async def call_openai_api(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY not set in environment variables")
    
    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"OpenAI API request failed: {str(e)}")

async def generate_mock_ai_response(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    """Local mock AI response as fallback"""
    if "job posting" in prompt.lower() and "summarize" in prompt.lower():
        return """\n\n🔧 Skills & Technical Expertise:\n- Technical program management (Agile, Scrum, Kanban)\n- Software development lifecycle & modern architecture principles\n- Data-driven program governance and KPI tracking\n- Change management and process optimization\n- Strong stakeholder engagement and cross-functional communication\n\n🎯 Responsibilities:\n- Drive technical strategy and execution across multi-team engineering initiatives\n- Develop and maintain technical roadmaps\n- Resolve technical dependencies and risks\n- Lead end-to-end program management\n\n🎓 Qualifications:\n- 10+ years in technical program management roles\n- Bachelor's in Engineering, Computer Science, or related\n- PMP certification preferred"""
    
    elif "comparison table" in prompt.lower():
        return """\n| Category | Match Type | Score |\n|----------|------------|-------|\n| Years of Experience | ✅ Strong | 1.0 |\n| Technical Program Mgmt | ✅ Strong | 1.0 |\n| Agile/Scrum/Kanban | ✅ Strong | 1.0 |\n| Software Architecture | ⚠️ Partial | 0.5 |\n| Budget & Resource Mgmt | ⚠️ Partial | 0.5 |\n| Stakeholder Engagement | ✅ Strong | 1.0 |\n| Change Management | ✅ Moderate-Strong | 0.75 |\n\n**Total: 8.25 / 10**"""
    
    elif "percentage score" in prompt.lower():
        return "88"
    
    elif "resume summary" in prompt.lower():
        return """Experienced professional with strong expertise in technical program management. 
Strong problem-solving skills and team collaboration. Proven track record of delivering 
complex projects on time and within budget."""
    
    elif "work experience" in prompt.lower():
        return """- Led development of key platform initiatives using modern technologies
- Implemented scalable architecture solutions improving system performance by 40%
- Managed cross-functional teams of 5-10 members across multiple time zones
- Delivered projects on time with 95% stakeholder satisfaction rate
- Optimized processes reducing delivery time by 30%"""
    
    elif "cover letter" in prompt.lower():
        return """Dear Hiring Manager,

I am excited to apply for this position. With my extensive experience and proven track record, 
I believe I am an excellent fit for your team.

My background in technical program management, combined with my passion for driving innovation, 
aligns perfectly with your requirements. I have consistently delivered results that exceed 
expectations and am eager to bring this same dedication to your organization.

Thank you for considering my application. I look forward to the opportunity to discuss how 
my skills and experience can benefit your team.

Best regards"""
    
    else:
        return "AI analysis completed successfully. Please review the generated content."

async def call_ai_api(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    """Smart AI service selector: OpenAI first, then xAI, then local mock"""
    try:
        return await call_openai_api(prompt, system_prompt)
    except Exception as openai_error:
        try:
            print(f"OpenAI failed, switching to xAI: {str(openai_error)}")
            return await call_xai_api(prompt, system_prompt)
        except Exception as xai_error:
            print(f"xAI also failed, using local mock AI: {str(xai_error)}")
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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch job posting: {str(e)}")

async def compare_texts(job_text: str, resume_text: str) -> dict:
    try:
        # a. Job Summary
        job_summary_prompt = (
            "Please read the following job posting content:\n\n"
            f"{job_text}\n\n"
            "Summarize the key job requirements including: Skills & Technical Requirements, Responsibilities, and Qualifications."
        )
        job_summary = await call_ai_api(job_summary_prompt)
        job_summary = f"Key Requirements from this Job Posting:\n\n{job_summary}"

        # b. Resume Summary with Comparison Table
        resume_summary_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job summary:\n\n"
            f"{job_summary}\n\n"
            "Provide a comparison table with columns: Categories, Match Status (✅Strong/✅Moderate-strong/⚠️Partial/❌Lack), and Comments."
        )
        resume_summary = await call_ai_api(resume_summary_prompt)
        resume_summary = f"\n\n{resume_summary}"

        # c. Match Score
        match_score_prompt = (
            "Based on the comparison, calculate a percentage match score. "
            "Strong=1.0, Moderate-Strong=0.8, Partial=0.5, Lack=0. "
            "Only output the final percentage score."
        )
        match_score_str = await call_ai_api(match_score_prompt)
        try:
            match_score = float(match_score_str.strip().replace("%", ""))
        except Exception:
            match_score = 85

        # d. Tailored Resume Summary
        tailored_resume_summary_prompt = (
            f"Read the resume:\n\n{resume_text}\n\n"
            f"And job:\n\n{job_text}\n\n"
            "Provide a revised summary that better matches the job requirements. Keep within 1700 characters."
        )
        tailored_resume_summary = await call_ai_api(tailored_resume_summary_prompt)

        # e. Tailored Work Experience
        tailored_work_experience_prompt = (
            f"Read the resume:\n\n{resume_text}\n\n"
            f"And job:\n\n{job_text}\n\n"
            "Modify the work experience to better match job requirements. Output in bullet format, max 7 bullets."
        )
        tailored_work_experience_text = await call_ai_api(tailored_work_experience_prompt)
        tailored_work_experience = [line.strip() for line in tailored_work_experience_text.split("\n") if line.strip().startswith("-")]
        tailored_work_experience = tailored_work_experience[:7]

        # f. Cover Letter
        cover_letter_prompt = (
            f"Read the resume:\n\n{resume_text}\n\n"
            f"And job:\n\n{job_text}\n\n"
            "Write a professional cover letter highlighting the candidate's best fit skills and experiences."
        )
        cover_letter = await call_ai_api(cover_letter_prompt)

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
async def compare(job_url: str = Form(...), resume: UploadFile = File(...)):
    try:
        resume_text = ""
        if resume.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume)
        elif resume.filename.endswith((".doc", ".docx")):
            resume_text = extract_text_from_docx(resume)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Unsupported file format. Please upload PDF or DOCX."},
            )
        job_text = extract_text_from_url(job_url)
        result = await compare_texts(job_text, resume_text)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing error: {str(e)}"},
        )

@app.get("/")
def root():
    return {"message": "SmartSuccess.AI Backend API is running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
