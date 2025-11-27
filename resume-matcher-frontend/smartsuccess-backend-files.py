# ============================================
# FILE: resume-matcher-backend/main.py
# ============================================
# (Same as root main.py - copy from that artifact)

# ============================================
# FILE: resume-matcher-backend/requirements.txt
# ============================================
"""
fastapi
uvicorn[standard]
python-multipart
pydantic
openai
python-docx
PyPDF2
aiohttp
beautifulsoup4
requests
"""

# ============================================
# FILE: resume-matcher-backend/.gitignore
# ============================================
"""
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/
.env
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
"""

# ============================================
# FILE: resume-matcher-backend/DEPLOYMENT.md
# ============================================
"""
# SmartSuccess.AI Backend Deployment Guide

## Render Deployment

### Prerequisites
- GitHub account with repository access
- Render account (https://render.com)

### Setup Steps

1. **Create New Web Service on Render**
   - Connect your GitHub repository
   - Select the `resume-matcher-backend` directory

2. **Configure Build Settings**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**
   Set the following in Render dashboard:
   ```
   OPENAI_API_KEY=your_openai_api_key
   XAI_API_KEY=your_xai_api_key
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

### Health Check
- Endpoint: `GET /health`
- Expected Response: `{"status": "ok"}`

### API Endpoints
- `POST /api/compare` - Resume comparison
- `GET /` - Root endpoint
- `GET /health` - Health check

## Local Development

```bash
cd resume-matcher-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Troubleshooting

### CORS Issues
Ensure frontend domain is in `ALLOWED_ORIGINS` environment variable.

### API Key Issues
Verify API keys are correctly set in environment variables.
"""

# ============================================
# FILE: resume-matcher-backend/test_connection.py
# ============================================
import requests
import sys

def test_backend():
    """Test backend connectivity"""
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

if __name__ == "__main__":
    test_backend()
