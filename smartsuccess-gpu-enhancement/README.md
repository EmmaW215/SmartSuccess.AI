# SmartSuccess.AI GPU Enhancement Package

## Overview

This package provides GPU-powered enhancements for SmartSuccess.AI, implementing a hybrid architecture that seamlessly integrates with the existing Render-based backend while leveraging GPU acceleration for advanced features.

## Key Features

| Module | Description | GPU Requirement |
|--------|-------------|-----------------|
| **GPU Server Parallel Architecture** | Hybrid CPU/GPU backend with automatic failover | Required for GPU features |
| **Pre-trained General RAG Question Bank** | 5000+ Tech/AI interview questions | Optional (works on CPU) |
| **MatchWise.ai Deep Integration** | One-way data flow for personalized RAG | Optional (works on CPU) |
| **Advanced Voice Models** | Whisper Large-v3 + XTTS-v2 | Recommended |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (Vercel)                           │
│                   smart-success-ai.vercel.app                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Request Router / Load Balancer                    │
│                  (Frontend determines routing)                       │
└─────────────────────────────────────────────────────────────────────┘
                    │                               │
                    ▼                               ▼
┌───────────────────────────────┐   ┌────────────────────────────────┐
│   Render Backend (CPU)        │   │    GPU Server (inference.ai)   │
│   smartsuccess-ai.onrender.com│   │    gpu.smartsuccess.ai         │
│                               │   │                                │
│   • User Management           │   │   • Voice Processing           │
│   • Payment Processing        │   │   • Advanced RAG               │
│   • Basic AI Services         │   │   • LLM Inference              │
│   • Database Operations       │   │   • Embedding Generation       │
│   • Fallback Interview        │   │   • Pre-RAG Question Bank      │
└───────────────────────────────┘   └────────────────────────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Shared Storage (Cloud)                           │
│   • User RAG Documents                                              │
│   • Pre-trained Vector Store                                        │
│   • Voice Model Cache                                               │
└─────────────────────────────────────────────────────────────────────┘
```

## Failover Strategy

When GPU server is offline, the system automatically falls back to Render:

| Feature | GPU Mode | Fallback Mode |
|---------|----------|---------------|
| Voice Interview | Whisper + XTTS-v2 | Web Speech API |
| RAG Questions | GPU-accelerated embeddings | Pre-computed embeddings |
| LLM Inference | Local Llama/Mistral | OpenAI/Groq API |
| Interview Service | Full featured | Basic (current) |

## Directory Structure

```
smartsuccess-gpu-enhancement/
├── gpu_backend/                    # GPU Server Backend
│   ├── main.py                     # FastAPI entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py             # Configuration management
│   │   ├── gpu_config.py           # GPU-specific settings
│   │   └── model_config.py         # Model paths & settings
│   ├── services/
│   │   ├── __init__.py
│   │   ├── voice_service.py        # ASR + TTS
│   │   ├── rag_service.py          # Enhanced RAG with GPU
│   │   ├── prerag_service.py       # Pre-trained question bank
│   │   ├── embedding_service.py    # GPU embeddings
│   │   ├── llm_service.py          # Local LLM inference
│   │   ├── interview_service.py    # GPU interview service
│   │   └── matchwise_service.py    # MatchWise integration
│   ├── models/
│   │   └── schemas.py              # Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── voice_routes.py
│   │   ├── rag_routes.py
│   │   ├── interview_routes.py
│   │   └── health_routes.py
│   ├── data/
│   │   ├── pre_rag/                # Pre-trained vector DB
│   │   ├── user_rag/               # User-specific vectors
│   │   └── voice_presets/          # TTS voice presets
│   ├── scripts/
│   │   ├── build_prerag.py         # Build question bank
│   │   ├── download_models.py      # Download ML models
│   │   └── collect_questions.py    # Data collection
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── gpu_utils.py            # GPU management
│   │   ├── cache_utils.py          # Redis caching
│   │   └── audio_utils.py          # Audio processing
│   ├── tests/
│   │   └── test_services.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend_updates/               # Frontend modifications
│   ├── components/
│   │   ├── VoiceInterviewV2.tsx    # Enhanced voice component
│   │   └── GPUStatusIndicator.tsx  # GPU status display
│   ├── hooks/
│   │   ├── useGPUBackend.ts        # GPU backend hook
│   │   └── useVoiceInterview.ts    # Voice interview hook
│   └── utils/
│       ├── requestRouter.ts        # Request routing logic
│       └── gpuHealthCheck.ts       # Health check utility
├── docs/
│   ├── DEPLOYMENT_GUIDE.md
│   ├── API_REFERENCE.md
│   └── CONFIGURATION.md
└── deployment/
    ├── docker-compose.yml
    ├── nginx.conf
    └── systemd/
        └── gpu-backend.service
```

## Quick Start

### 1. GPU Server Setup

```bash
# SSH to GPU server
ssh user@gpu.inference.ai

# Clone and setup
git clone https://github.com/EmmaW215/SmartSuccess.AI.git
cd SmartSuccess.AI/gpu_backend

# Install dependencies
pip install -r requirements.txt

# Download models
python scripts/download_models.py

# Build pre-RAG question bank
python scripts/build_prerag.py

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Configure Frontend

Update environment variables in Vercel:

```
NEXT_PUBLIC_GPU_BACKEND_URL=https://gpu.smartsuccess.ai
NEXT_PUBLIC_RENDER_BACKEND_URL=https://smartsuccess-ai.onrender.com
```

### 3. Test Integration

```bash
# Check GPU server health
curl https://gpu.smartsuccess.ai/health

# Test voice transcription
curl -X POST https://gpu.smartsuccess.ai/api/voice/transcribe \
  -F "audio=@test.wav"
```

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU VRAM | 24GB | 48GB |
| CPU Cores | 4 | 8 |
| RAM | 32GB | 96GB |
| Storage | 50GB | 100GB |

## Cost Estimation

| Item | Monthly Cost |
|------|-------------|
| GPU Server (48GB) | $500-800 |
| Cloud Storage | $50 |
| Bandwidth | $100 |
| **Total** | **$650-950** |

## License

MIT License - See LICENSE file for details.

## Support

For issues and questions, please open a GitHub issue or contact the development team.
