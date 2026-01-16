# SmartSuccess.AI - AI-Powered Resume Matching Platform

## 🚀 Project Overview

SmartSuccess.AI is an intelligent resume comparison platform that uses AI to analyze job postings and optimize resumes for specific positions. The platform also provides mock interview preparation for better practices.

## ✨ Features

### Core Functionality
- **AI Resume Analysis**: Intelligent comparison between resume and job requirements
- **Job Posting Scraping**: Automatic extraction of job details from URLs
- **Matching Score**: Percentage-based compatibility assessment
- **Tailored Resume Summary**: AI-generated resume optimization suggestions
- **Custom Work Experience**: Enhanced experience descriptions for specific roles
- **Cover Letter Generation**: Professional cover letters tailored to job postings
- **Visitor Counter**: Real-time visitor tracking with admin panel
- **Multi-format Support**: PDF and DOCX resume upload support

### AI Service Integration
- **Triple-layer AI System**:
  1. **OpenAI GPT-3.5-turbo** (Primary)
  2. **xAI Grok-3** (Fallback)
  3. **Local Mock AI** (Emergency backup)
- **Automatic Failover**: Seamless switching between AI services

## 🛠️ Technology Stack

### Frontend
- **Next.js 15.3.4** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Vercel** - Deployment and hosting platform

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.9+** - Backend programming language
- **Render** - Cloud deployment platform
- **aiohttp** - Async HTTP client/server
- **PyPDF2** - PDF text extraction
- **python-docx** - DOCX file processing
- **BeautifulSoup4** - Web scraping
- **OpenAI API** - AI text generation
- **xAI API** - Alternative AI service

## 📁 Project Structure

```
SmartSuccess.AI/
├── resume-matcher-frontend/          # Next.js frontend application
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx             # Main application page
│   │       ├── layout.tsx           # Root layout component
│   │       ├── globals.css          # Global styles
│   │       ├── components/          # React components
│   │       ├── api/                 # API routes
│   │       └── admin/               # Admin pages
│   ├── public/                      # Static assets
│   ├── package.json                 # Frontend dependencies
│   └── next.config.ts              # Next.js configuration
├── resume-matcher-backend/          # FastAPI backend application
│   ├── main.py                     # Main backend application
│   ├── requirements.txt            # Python dependencies
│   └── DEPLOYMENT.md               # Deployment guide
├── main.py                         # Root backend entry point
├── requirements.txt                # Root Python dependencies
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Git

### Frontend Setup
```bash
cd resume-matcher-frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd resume-matcher-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Environment Variables

#### Frontend (.env.local)
```env
NEXT_PUBLIC_BACKEND_URL=https://smartsuccess-ai.onrender.com
```

#### Backend (Render Environment Variables)
```env
OPENAI_API_KEY=your_openai_api_key
XAI_API_KEY=your_xai_api_key
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

## 🔧 API Endpoints

### Backend API
- `POST /api/compare` - Resume and job comparison
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint

### Frontend API
- `GET /api/visitor-count` - Visitor counter
- `POST /api/visitor-count` - Increment visitor count

## 🎯 Usage Guide

1. **Upload Resume**: Drag and drop or select PDF/DOCX file
2. **Enter Job URL**: Paste the job posting URL
3. **Generate Analysis**: Click "Generate Comparison" button
4. **Review Results**: View matching score, tailored resume, and cover letter

## 🔒 Security Features

- **CORS Configuration**: Secure cross-origin requests
- **Environment Variables**: Secure API key management
- **Input Validation**: File type and size validation
- **Error Handling**: Comprehensive error management

## 📄 License

This project is licensed under the MIT License.

---

**SmartSuccess.AI** - Making job applications smarter with AI-powered resume optimization.
