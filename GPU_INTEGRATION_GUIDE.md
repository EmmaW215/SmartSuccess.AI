# SmartSuccess.AI GPU Integration Guide

## Overview

This project now supports a hybrid architecture with:
- **Render Backend** (Always On): User management, payments, basic interview services
- **GPU Server** (When Available): Advanced voice processing, RAG, embeddings

The frontend automatically routes requests to the appropriate backend based on availability.

## Environment Variables

### Frontend (Vercel)

Add these environment variables in your Vercel dashboard:

```bash
# Existing backend (Render)
NEXT_PUBLIC_BACKEND_URL=https://smartsuccess-ai.onrender.com

# GPU backend (optional - for enhanced features)
NEXT_PUBLIC_GPU_BACKEND_URL=https://your-gpu-server.inference.ai

# Render backend URL (fallback, defaults to NEXT_PUBLIC_BACKEND_URL)
NEXT_PUBLIC_RENDER_BACKEND_URL=https://smartsuccess-ai.onrender.com
```

### GPU Backend Server

Create a `.env` file in the `gpu_backend/` directory:

```bash
# Application
APP_NAME=SmartSuccess.AI GPU Backend
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# CORS - Add your frontend domains
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
```

## Architecture

```
Frontend (Vercel)
    │
    ├─→ Request Router (requestRouter.ts)
    │       │
    │       ├─→ GPU Server (when available)
    │       │   • Voice processing (Whisper + XTTS)
    │       │   • Advanced RAG
    │       │   • GPU embeddings
    │       │
    │       └─→ Render Backend (fallback)
    │           • User management
    │           • Payments
    │           • Basic interview
```

## Request Routing

The frontend automatically routes requests:

- **Always to Render**: `/auth`, `/payment`, `/user`, `/visitor`
- **Prefer GPU**: `/api/voice/*`, `/api/rag/*`, `/api/embedding/*`
- **Hybrid** (GPU if available): `/api/interview/*`

## Features

### GPU-Enhanced Features (When GPU Server Online)

- ✅ Whisper Large-v3 for speech recognition
- ✅ XTTS-v2 for natural text-to-speech
- ✅ GPU-accelerated embeddings
- ✅ Pre-trained RAG question bank (5000+ questions)
- ✅ Personalized RAG from MatchWise.ai integration

### Fallback Features (When GPU Server Offline)

- ✅ Web Speech API for speech recognition
- ✅ Browser TTS for text-to-speech
- ✅ Standard interview functionality
- ✅ All basic features remain available

## Deployment

### GPU Backend Deployment

1. **SSH to GPU server**
   ```bash
   ssh user@gpu.inference.ai
   ```

2. **Navigate to GPU backend**
   ```bash
   cd smartsuccess-gpu-enhancement/gpu_backend
   ```

3. **Install dependencies**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Configure environment**
   ```bash
   nano .env
   ```

5. **Start server**
   ```bash
   source venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Frontend Deployment

No changes needed! The frontend automatically detects GPU availability and routes requests accordingly.

## Testing

### Test GPU Server

```bash
# Health check
curl https://your-gpu-server/health

# Expected response:
# {"status":"healthy","gpu_available":true,...}
```

### Test Frontend Integration

1. Open browser console
2. Navigate to interview page
3. Check for GPU status logs:
   - `🖥️ GPU server health: Available` (good)
   - `⚠️ GPU server unreachable` (fallback mode)

4. Verify GPU status badge shows:
   - "GPU Enhanced" when GPU is available
   - "Standard Mode" when GPU is offline

## Troubleshooting

### GPU Not Detected

1. Check GPU server is running: `curl https://your-gpu-server/health`
2. Verify `NEXT_PUBLIC_GPU_BACKEND_URL` is set correctly
3. Check browser console for routing logs

### Fallback Not Working

1. Verify `NEXT_PUBLIC_RENDER_BACKEND_URL` is set
2. Check that Render backend is accessible
3. Review request router logs in console

### CORS Errors

Update `ALLOWED_ORIGINS` in GPU backend `.env`:
```bash
ALLOWED_ORIGINS=["https://your-domain.vercel.app","http://localhost:3000"]
```

## Backward Compatibility

✅ **All existing functionality is preserved**
- Existing API calls continue to work
- Render backend remains the primary backend
- GPU features are optional enhancements
- Automatic fallback ensures no service interruption

## File Structure

```
resume-matcher-frontend/
├── src/app/
│   ├── utils/
│   │   └── requestRouter.ts          # Smart routing logic
│   ├── hooks/
│   │   ├── useGPUBackend.ts          # GPU backend hook
│   │   └── useVoiceInterview.ts      # Voice interview hook
│   ├── components/
│   │   └── GPUStatusIndicator.tsx    # GPU status display
│   └── interview/
│       └── page.tsx                  # Updated with GPU support
│
smartsuccess-gpu-enhancement/
└── gpu_backend/                      # Independent GPU server
    ├── main.py
    ├── services/
    ├── routes/
    └── config/
```

## Support

For issues:
1. Check GPU server logs
2. Check browser console for routing errors
3. Verify environment variables are set correctly
4. Review health endpoint: `/health`
