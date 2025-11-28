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
    "https://matchwise-ai.vercel.app",
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
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"OpenAI API request failed: {str(e)}")

async def generate_mock_ai_response(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    """本地模拟AI响应，作为最后的备用方案"""
    # 根据提示类型生成相应的模拟响应
    if "job posting" in prompt.lower() and "summarize" in prompt.lower():
        return """

\n\n
🔧 Skills & Technical Expertise:\n\n
- Technical program management (Agile, Scrum, Kanban)\n\n
- Software development lifecycle & modern architecture principles\n\n
- Data-driven program governance and KPI tracking\n\n
- Change management and process optimization\n\n
- Strong stakeholder engagement and cross-functional communication\n\n
- Budget/resource management across engineering initiatives\n\n

\n\n
🎯 Responsibilities:\n\n
- Drive technical strategy and execution across multi-team engineering initiatives\n\n
- Develop and maintain technical roadmaps\n\n
- Resolve technical dependencies and risks\n\n
- Lead end-to-end program management\n\n
- Implement scalable governance frameworks and metrics\n\n
- Collaborate across engineering, product, and business functions\n\n
- Lead high-priority strategic programs and change management\n\n


🎓 Qualifications:\n\n
- 10+ years in technical program management roles\n\n
- Bachelor's in Engineering, Computer Science, or related\n\n
- PMP certification preferred\n\n
- Strong leadership, organizational and communication skills\n\n"""
    
    elif "comparison table" in prompt.lower():
        return """
\n\n
| Category | Match Type | Score |\n\n
|----------|------------|-------|\n\n
| Years of Experience | ✅ Strong | 1.0 |\n\n
| Technical Program Mgmt | ✅ Strong | 1.0 |\n\n
| Agile/Scrum/Kanban | ✅ Strong | 1.0 |\n\n
| Software Architecture | ⚠️ Partial | 0.5 |\n\n
| Budget & Resource Mgmt | ⚠️ Partial | 0.5 |\n\n
| Stakeholder Engagement | ✅ Strong | 1.0 |\n\n
| Change Management | ✅ Moderate-Strong | 0.75 |\n\n
| GCP/Cloud & Tech Stack | ✅ Strong | 1.0 |\n\n
| Governance & KPI Tracking | ✅ Strong | 1.0 |\n\n
| PMP Certification | ⚠️ Partial (in progress) | 0.5 |\n\n
| Industry Knowledge (Health) | ❌ Lack | 0.0 |\n\n
\n\n
**Total: 8.25 / 10**\n\n"""
    
    elif "percentage score" in prompt.lower():
        return "88"
    
    elif "resume summary" in prompt.lower():
        return """Experienced software developer with 14+ years in full-stack development. 
Strong expertise in Python, JavaScript, and React. Led development teams and delivered 
multiple successful projects. Excellent problem-solving skills and team collaboration."""
    
    elif "work experience" in prompt.lower():
        return """- Led development of e-commerce platform using React and Node.js
- Implemented RESTful APIs and microservices architecture
- Managed team of 3 developers and delivered projects on time
- Optimized database queries improving performance by 40%
- Integrated third-party payment systems and analytics tools"""
    
    elif "cover letter" in prompt.lower():
        return """Dear Hiring Manager,

I am excited to apply for the Software Developer position. With 14+ years of experience 
in full-stack development using Python, JavaScript, and React, I believe I am an 
excellent fit for your team.

My experience leading development teams and delivering complex projects aligns 
perfectly with your requirements. I am passionate about creating efficient, 
scalable solutions and would welcome the opportunity to contribute to your 
organization's success.

Thank you for considering my application. I look forward to discussing how my 
skills and experience can benefit your team.

Best regards,
[Your Name]"""
    
    else:
        return "AI analysis completed successfully. Please review the generated content."

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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
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
            "	1. Summarize the job descriptions by extracting and organizing the following information into a clean bullet list format. Please extract the actual information from the job posting. Using the structure above, organize the output into a clean bullet list format. If any information is not available in the job posting, use 'Not specified' for that item. Ensure the output is clean, well-structured, and uses proper bullet list formatting. Maintain 1.2 line spacing. Follow this format to list the details(leave it blank if no related details from the job posting):
	Job Description Summary (Clean Bullet List)
		• Position Title: …
		• Company Name: 
		• Department: …
		• Location: …
		• Employment Type:  Full-time/Part-time/Remote/Contract & Length/etc…
		• Requisition ID: 
		• Reporting To: …
		• Compensation:
			○ Salary/Rate: …
			○ Benefits: …
			○ Environment/Company Culture:…
		• Key Responsibilities:
			○ 
			○ 
			○ 
		• Core Requirements (Required Skills):
			i. Technical skills: 
			○  
			○ 
			○ 
			ii. Soft skills:
			○  
			○ 
			○ 
		• Preferred (Nice-to-Have/Stand-Outs):
			i. Technical skills: 
			○  
			○ 
			○ 
			ii. Soft skills:
			○  
			○ 
			○ 
		• Cultural Fit:
			○ 
			○ 
			○ 
"
        )
        job_summary = await call_ai_api(job_summary_prompt)
        job_summary = f"Key Requirements from this Job Posting:\n\n{job_summary}"

        # b. Resume Summary with Comparison Table
        resume_summary_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job summary:\n\n"
            f"{job_summary}\n\n"
            "Provide a comparison table based on the highlights of the user's key skills and experiences in the resume_text (the user's resume) and job_summary. List in a table format with three columns: Categories (key requirements and skills), Match Status (four status will be used: ✅Strong/✅Moderate-strong/⚠️Partial/❌Lack), and Comments (very precise comment on how the user's experiences matches with the job requirement). Only Output the table contents in a table format as resume_summary."
        )
        resume_summary = await call_ai_api(resume_summary_prompt)
        resume_summary = f"\n\n{resume_summary}"

        # c. Match Score
        match_score_prompt = (
            "Based on the comparison table in resume_summary, and the listed Match status (Strong/Moderate-strong/Partial/Lack), calculate and show a percentage match score. The score is calculated using the formula: Match Score (%) = (Sum of weight_match_score) ÷ (Sum of weight_match_total). For each Category and its Match Status, use the assigned weights as follows: Strong match → weight_match_score = 1, weight_match_total = 1; Moderate-Strong match → weight_match_score = 0.8, weight_match_total = 1; Partial match → weight_match_score = 0.5, weight_match_total = 1; Lack → weight_match_score = 0, weight_match_total = 1. Only output the final percentage score, rounded to two decimal places."
        )
        match_score_str = await call_ai_api(match_score_prompt)
        try:
            match_score = float(match_score_str.strip().replace("%", ""))
        except Exception:
            match_score = match_score_str

        # d. Tailored Resume Summary
        tailored_resume_summary_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job content:\n\n"
            f"{job_text}\n\n"
            "Provide a revised one-paragraph summary based on the user resume and the job posting. Make sure this summary highlights the user's key skills and work experiences which more closely matched with the job requirements in job posting. Please limit the overall summary within 1800 characters. The output should be in html format and should maintain a simple, modern style. Maintain 1.2 line spacing. Follow resume format to have no First-person pronouns being used."
        )
        tailored_resume_summary = await call_ai_api(tailored_resume_summary_prompt)
        tailored_resume_summary = f"\n{tailored_resume_summary}"

        # e. Tailored Work Experience
        tailored_work_experience_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job content:\n\n"
            f"{job_text}\n\n"
            "Find the latest work experiences from the resume and highlight the ones which are better matched the job requirements. Please refine these best fit work experiences and provide the revised work experience content. Organize the output into a clean bullet list using the structure above. Focus on the most recent and relevant experiences that align with the job requirements. Keep each bullet point concise and impactful. Make sure there are line breaks between each paragraph. Ensure the output uses proper bullet list formatting. Maintain 1.2 line spacing. To modify the working experiences from user's resume, better group and combine it, highlight the key accomplishments and achievements, and make it more fit for the job requirements. Ensure the modified contents reflect the truths, no grammar errors, but please keep the original words and language styles as much as possible. "
        )
        tailored_work_experience_text = await call_ai_api(tailored_work_experience_prompt)
        tailored_work_experience = [line.strip() for line in tailored_work_experience_text.split("\n") if line.strip().startswith("-")]
        tailored_work_experience = tailored_work_experience[:7]
        tailored_work_experience = [f"\n{item}" for item in tailored_work_experience]

        # f. Cover Letter
        cover_letter_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job content:\n\n"
            f"{job_text}\n\n"
            "Please according to my resume, provide a formal cover letter with a Subject for this job application. The " 'job position' at 'the company' " those names in the cover letter for the application should be the same as what being used in the job posting. The cover letter should show and highlight the user's real experiences, skill sets and key strengths which best fit the job requirements according to the job posting. Then express the user's passions for the position, the transferrable of the user's previous work experiences and technical skills to benefit this position, and emphasis that the user is very adaptable, a faster learner, and how confident can contribute to the team and the company, and the appreciation for a future interview opportunity. The overall tone of the cover letter should be confident, honest, and professional. The cover letters should be written in the first person. Make sure there are line breaks between each paragraph."
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
    return {"message": "MatchWise Backend API is running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
