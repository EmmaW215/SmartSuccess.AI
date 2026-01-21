#!/usr/bin/env python3
"""Complete Setup Verification Script"""
import sys

print("="*60)
print("GPU Backend 环境设置验证")
print("="*60)

# Test 1: PyTorch & CUDA
try:
    import torch
    print("✅ PyTorch:", torch.__version__)
    print("✅ CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("✅ CUDA version:", torch.version.cuda)
        print("✅ Device:", torch.cuda.get_device_name(0))
        print("✅ Device count:", torch.cuda.device_count())
except Exception as e:
    print("❌ PyTorch/CUDA error:", e)
    sys.exit(1)

# Test 2: Core Framework
try:
    import fastapi
    import uvicorn
    import pydantic
    print("✅ FastAPI:", fastapi.__version__)
    print("✅ Uvicorn:", uvicorn.__version__)
    print("✅ Pydantic:", pydantic.__version__)
except Exception as e:
    print("❌ Framework error:", e)
    sys.exit(1)

# Test 3: ML Libraries
try:
    import transformers
    import chromadb
    print("✅ Transformers:", transformers.__version__)
    print("✅ ChromaDB: installed")
except Exception as e:
    print("❌ ML libraries error:", e)
    sys.exit(1)

# Test 4: Audio Processing
try:
    import soundfile
    import librosa
    print("✅ Soundfile:", soundfile.__version__)
    print("✅ Librosa:", librosa.__version__)
except Exception as e:
    print("⚠️  Audio libraries warning:", e)

# Test 5: Utilities
try:
    import redis
    import loguru
    print("✅ Redis: installed")
    print("✅ Loguru: installed")
except Exception as e:
    print("⚠️  Utilities warning:", e)

# Test 6: GPU Computation
try:
    if torch.cuda.is_available():
        x = torch.randn(3, 3).cuda()
        y = torch.randn(3, 3).cuda()
        z = torch.matmul(x, y)
        print("✅ GPU computation test: SUCCESS")
except Exception as e:
    print("❌ GPU computation test failed:", e)
    sys.exit(1)

# Test 7: Directory Structure
import os
dirs = [
    "data/pre_rag/chroma",
    "data/user_rag/chroma",
    "data/voice_presets",
    "models"
]
print("\n📁 目录结构检查:")
for d in dirs:
    if os.path.exists(d):
        print(f"✅ {d}")
    else:
        print(f"❌ {d} - 缺失!")

print("\n" + "="*60)
print("✅ 所有验证完成!")
print("="*60)
