# SmartSuccess.AI GPU Enhancement - Deployment Guide

## Overview

This guide covers deploying the GPU enhancement package for SmartSuccess.AI, implementing a hybrid architecture with:
- **Render Backend (Always On)**: User management, payments, basic interview
- **GPU Server (When Available)**: Voice processing, RAG, embeddings

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                            │
│                smart-success-ai.vercel.app                      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Request Router (requestRouter.ts)           │   │
│  │                                                          │   │
│  │  GPU Health Check → Route Decision → Fallback Logic      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌───────────────────────┐     ┌───────────────────────┐
│   Render Backend      │     │   GPU Server          │
│   (Always Available)  │     │   (When Online)       │
│                       │     │                       │
│ • /auth/*             │     │ • /api/voice/*        │
│ • /payment/*          │     │ • /api/rag/*          │
│ • /user/*             │     │ • /api/interview/*    │
│ • /interview/* (text) │     │ • /api/embedding/*    │
└───────────────────────┘     └───────────────────────┘
```

---

## Part 1: GPU Server Deployment

### 1.1 Prerequisites

- SSH access to inference.ai GPU server
- 48GB VRAM GPU (e.g., A100, L40)
- Python 3.9+
- CUDA 12.x drivers installed

### 1.2 Initial Server Setup

```bash
# SSH to GPU server
ssh user@gpu.inference.ai

# Create project directory
mkdir -p ~/smartsuccess-gpu
cd ~/smartsuccess-gpu

# Clone or upload the GPU backend
git clone https://github.com/EmmaW215/SmartSuccess.AI.git
# Or upload the gpu_backend folder

# Navigate to GPU backend
cd SmartSuccess.AI/gpu_backend
# Or: cd gpu_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 1.3 Install Dependencies

```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Install other dependencies
pip install -r requirements.txt

# Verify GPU is detected
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0)}')"
```

### 1.4 Download ML Models

```bash
# Create model directories
mkdir -p data/pre_rag/chroma
mkdir -p data/user_rag/chroma
mkdir -p data/voice_presets
mkdir -p models

# Download models (will be cached)
python -c "
import whisper
from sentence_transformers import SentenceTransformer
from TTS.api import TTS

print('Downloading Whisper large-v3...')
whisper.load_model('large-v3')

print('Downloading embedding model...')
SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

print('Downloading TTS model...')
TTS('tts_models/multilingual/multi-dataset/xtts_v2')

print('All models downloaded!')
"
```

### 1.5 Environment Configuration

Create `.env` file:

```bash
cat > .env << 'EOF'
# Application
APP_NAME=SmartSuccess.AI GPU Backend
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# CORS - Add your domains
ALLOWED_ORIGINS=["https://smart-success-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000"]

# Render backend for fallback
RENDER_BACKEND_URL=https://smartsuccess-ai.onrender.com

# Optional: API keys if using external services
OPENAI_API_KEY=
GROQ_API_KEY=

# Data paths
DATA_DIR=./data
PRERAG_DIR=./data/pre_rag
USER_RAG_DIR=./data/user_rag
VOICE_PRESETS_DIR=./data/voice_presets

# GPU settings
GPU_DEVICE=cuda
GPU_MEMORY_FRACTION=0.9
EOF
```

### 1.6 Build Pre-RAG Question Bank

```bash
# Initialize Pre-RAG (builds vector database)
python -c "
from services import get_prerag_service
service = get_prerag_service()
stats = service.get_stats()
print(f'Pre-RAG initialized with {stats.total_questions} questions')
print(f'Categories: {stats.by_category}')
"
```

### 1.7 Start the Server

**Development mode:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Production mode:**
```bash
# Using Uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using Gunicorn with Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 1.8 Systemd Service (Optional)

For persistent deployment, create a systemd service:

```bash
sudo cat > /etc/systemd/system/smartsuccess-gpu.service << 'EOF'
[Unit]
Description=SmartSuccess.AI GPU Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/smartsuccess-gpu/gpu_backend
Environment=PATH=/home/ubuntu/smartsuccess-gpu/gpu_backend/venv/bin
ExecStart=/home/ubuntu/smartsuccess-gpu/gpu_backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable smartsuccess-gpu
sudo systemctl start smartsuccess-gpu
sudo systemctl status smartsuccess-gpu
```

### 1.9 Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# GPU status
curl http://localhost:8000/gpu/status

# Test Pre-RAG
curl -X POST http://localhost:8000/api/rag/general/query \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning interview question", "n_results": 3}'
```

---

## Part 2: Frontend Updates

### 2.1 Add Environment Variables

In Vercel dashboard or `.env.local`:

```bash
NEXT_PUBLIC_GPU_BACKEND_URL=https://your-gpu-server.inference.ai
NEXT_PUBLIC_RENDER_BACKEND_URL=https://smartsuccess-ai.onrender.com
```

### 2.2 Install Frontend Files

Copy the frontend updates to your Next.js project:

```bash
# Copy utilities
cp frontend_updates/utils/requestRouter.ts app/utils/

# Copy hooks
cp frontend_updates/hooks/useGPUBackend.ts app/hooks/
cp frontend_updates/hooks/useVoiceInterview.ts app/hooks/

# Copy components
cp frontend_updates/components/GPUStatusIndicator.tsx app/components/
```

### 2.3 Update Interview Page

Modify `app/interview/page.tsx` to use the new hooks:

```typescript
// At the top of the file
import { useGPUBackend } from '@/hooks/useGPUBackend';
import { useVoiceInterview } from '@/hooks/useVoiceInterview';
import { GPUStatusBadge } from '@/components/GPUStatusIndicator';
import { routedFetch } from '@/utils/requestRouter';

// In your component
export default function InterviewPage() {
  const { gpuAvailable } = useGPUBackend();
  const {
    voiceAvailable,
    usingGPU,
    isRecording,
    startRecording,
    stopRecording,
    speak,
    isSpeaking
  } = useVoiceInterview({
    useGPU: true,
    onTranscription: (text) => {
      // Handle transcribed text
      sendMessage(text);
    }
  });

  // Replace fetch calls with routedFetch
  const startInterview = async () => {
    const response = await routedFetch('/api/interview/start', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        config: {
          categories: selectedCategories,
          use_voice: voiceAvailable,
          difficulty: 'medium'
        }
      })
    });
    // ...
  };

  return (
    <div>
      {/* Add GPU status indicator */}
      <GPUStatusBadge className="mb-4" />
      
      {/* Voice controls */}
      {voiceAvailable && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">
            {usingGPU ? '🚀 GPU Voice' : '🎤 Standard Voice'}
          </span>
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`px-4 py-2 rounded ${
              isRecording ? 'bg-red-500' : 'bg-blue-500'
            } text-white`}
          >
            {isRecording ? 'Stop' : 'Record'}
          </button>
        </div>
      )}
      
      {/* Rest of your interview UI */}
    </div>
  );
}
```

### 2.4 Update Homepage for MatchWise Integration

Add MatchWise data handler in `app/page.tsx`:

```typescript
// Add this useEffect for MatchWise message handling
useEffect(() => {
  const handleMatchWiseMessage = async (event: MessageEvent) => {
    // Verify origin
    const MATCHWISE_ORIGIN = 'https://matchwise-ai.vercel.app';
    if (event.origin !== MATCHWISE_ORIGIN) return;
    
    const { type, data } = event.data;
    
    if (type === 'ANALYSIS_COMPLETE') {
      console.log('📊 Received MatchWise analysis:', data);
      
      // Build personalized RAG on GPU server
      try {
        const response = await routedFetch('/api/rag/personalized/build', {
          method: 'POST',
          body: JSON.stringify({
            user_id: userId,
            matchwise_data: {
              resume_text: data.resumeText,
              job_description: data.jobDescription,
              match_score: data.matchScore,
              strengths: data.strengths,
              gaps: data.gaps,
              recommendations: data.recommendations,
              skills_match: data.skillsMatch,
              keywords_matched: data.keywordsMatched,
              keywords_missing: data.keywordsMissing
            },
            focus_categories: ['technical', 'behavioral', 'scenario'],
            difficulty_preference: 'medium',
            num_questions: 20
          })
        }, { preferGPU: true });
        
        const ragData = await response.json();
        console.log('✅ Personalized RAG built:', ragData);
        
        // Store RAG ID for interview
        setPersonalizedRagId(ragData.rag_id);
        setHasPersonalizedData(true);
        
      } catch (error) {
        console.error('❌ Failed to build personalized RAG:', error);
      }
    }
  };
  
  window.addEventListener('message', handleMatchWiseMessage);
  return () => window.removeEventListener('message', handleMatchWiseMessage);
}, [userId]);
```

### 2.5 Deploy to Vercel

```bash
# Commit changes
git add .
git commit -m "Add GPU backend integration"

# Push to trigger Vercel deployment
git push origin main
```

---

## Part 3: Testing & Verification

### 3.1 Test GPU Server

```bash
# 1. Health check
curl https://your-gpu-server/health

# Expected:
# {"status":"healthy","gpu_available":true,...}

# 2. Test voice transcription
curl -X POST https://your-gpu-server/api/voice/transcribe \
  -F "audio=@test.wav" \
  -F "language=en"

# 3. Test TTS
curl -X POST https://your-gpu-server/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, welcome to your interview.","voice_preset":"professional_male"}'

# 4. Test Pre-RAG
curl -X POST https://your-gpu-server/api/rag/general/query \
  -H "Content-Type: application/json" \
  -d '{"query":"tell me about your AI experience","category":"self_introduction","n_results":3}'
```

### 3.2 Test Frontend Integration

1. Open browser console
2. Navigate to interview page
3. Check for GPU status logs:
   - `🖥️ GPU server health: Available` (good)
   - `⚠️ GPU server unreachable` (fallback mode)

4. Test voice recording:
   - Click record button
   - Speak a response
   - Check transcription appears

5. Test TTS:
   - Interview should speak questions aloud
   - Check audio quality (GPU = natural, Fallback = robotic)

### 3.3 Test Failover

1. Stop GPU server
2. Refresh frontend
3. Verify:
   - Status shows "Standard Mode"
   - Interview still works (text-only or Web Speech)
   - No errors in console

4. Restart GPU server
5. After 30 seconds, verify:
   - Status shows "GPU Enhanced"
   - Voice features restored

---

## Part 4: Monitoring & Maintenance

### 4.1 GPU Server Monitoring

```bash
# View logs
journalctl -u smartsuccess-gpu -f

# Check GPU usage
nvidia-smi -l 1

# Check memory
free -h

# Check disk
df -h
```

### 4.2 Health Check Endpoint

Set up monitoring to ping `/health` endpoint:

```bash
# Add to crontab for alerts
*/5 * * * * curl -sf https://your-gpu-server/health || echo "GPU server down" | mail -s "Alert" admin@example.com
```

### 4.3 Graceful Shutdown

Before taking GPU server offline:

1. Update frontend environment variable (optional):
   ```
   NEXT_PUBLIC_GPU_BACKEND_URL=
   ```

2. Or simply stop the service - frontend will auto-failover:
   ```bash
   sudo systemctl stop smartsuccess-gpu
   ```

3. To restart:
   ```bash
   sudo systemctl start smartsuccess-gpu
   ```

---

## Troubleshooting

### GPU Not Detected

```bash
# Check CUDA
nvidia-smi
nvcc --version

# Check PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### Model Loading Fails

```bash
# Clear cache and retry
rm -rf ~/.cache/huggingface
rm -rf ~/.cache/torch

# Reinstall models
python scripts/download_models.py
```

### CORS Errors

Update `ALLOWED_ORIGINS` in `.env`:
```
ALLOWED_ORIGINS=["https://your-domain.vercel.app","http://localhost:3000"]
```

### High Latency

1. Check GPU utilization
2. Reduce `WORKERS` if memory constrained
3. Enable model caching
4. Consider model quantization

---

## Cost Optimization

1. **Use spot/preemptible instances** when possible
2. **Implement request batching** for embeddings
3. **Cache common TTS responses**
4. **Set user quotas** for voice features
5. **Monitor usage patterns** and scale accordingly

---

## Security Checklist

- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] API keys secured in environment
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] Logs don't contain sensitive data
- [ ] Regular security updates

---

## Support

For issues:
1. Check server logs: `journalctl -u smartsuccess-gpu`
2. Check browser console for frontend errors
3. Review health endpoint: `/health`
4. Check GPU status: `/gpu/status`
