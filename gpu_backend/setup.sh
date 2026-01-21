#!/bin/bash

# SmartSuccess.AI GPU Backend - Setup Script
# Run this script to set up the GPU backend server

set -e

echo "=============================================="
echo "SmartSuccess.AI GPU Backend Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo -e "${GREEN}✓ Python $python_version found${NC}"
else
    echo -e "${RED}✗ Python 3.9+ required (found $python_version)${NC}"
    exit 1
fi

# Check CUDA
echo -e "\n${YELLOW}Checking CUDA...${NC}"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo -e "${GREEN}✓ CUDA available${NC}"
else
    echo -e "${RED}✗ nvidia-smi not found - GPU features may not work${NC}"
fi

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}! Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install PyTorch with CUDA
echo -e "\n${YELLOW}Installing PyTorch with CUDA support...${NC}"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 > /dev/null 2>&1
echo -e "${GREEN}✓ PyTorch installed${NC}"

# Install other dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create directories
echo -e "\n${YELLOW}Creating data directories...${NC}"
mkdir -p data/pre_rag/chroma
mkdir -p data/user_rag/chroma
mkdir -p data/voice_presets
mkdir -p models
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"

# Copy environment file
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created - please edit it with your settings${NC}"
else
    echo -e "${YELLOW}! .env file already exists${NC}"
fi

# Download models
echo -e "\n${YELLOW}Downloading ML models (this may take a while)...${NC}"
python3 << 'PYTHON_SCRIPT'
import sys
import torch

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA memory: {torch.cuda.mem_get_info()[1] / (1024**3):.1f} GB")

# Download Whisper
print("\nDownloading Whisper large-v3...")
try:
    import whisper
    whisper.load_model("large-v3", download_root="./models")
    print("✓ Whisper downloaded")
except Exception as e:
    print(f"✗ Whisper download failed: {e}")

# Download embedding model
print("\nDownloading embedding model...")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2', cache_folder="./models")
    print("✓ Embedding model downloaded")
except Exception as e:
    print(f"✗ Embedding model download failed: {e}")

# Download TTS model
print("\nDownloading TTS model (XTTS-v2)...")
try:
    from TTS.api import TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    print("✓ TTS model downloaded")
except Exception as e:
    print(f"✗ TTS model download failed: {e}")

print("\nModel download complete!")
PYTHON_SCRIPT

# Initialize Pre-RAG
echo -e "\n${YELLOW}Initializing Pre-RAG question bank...${NC}"
python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '.')
from services import get_prerag_service

try:
    service = get_prerag_service()
    stats = service.get_stats()
    print(f"✓ Pre-RAG initialized with {stats.total_questions} questions")
    print(f"  Categories: {', '.join(stats.by_category.keys())}")
except Exception as e:
    print(f"✗ Pre-RAG initialization failed: {e}")
PYTHON_SCRIPT

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '.')

checks = []

# Check imports
try:
    from fastapi import FastAPI
    checks.append(("FastAPI", True))
except:
    checks.append(("FastAPI", False))

try:
    import torch
    checks.append(("PyTorch", True))
    checks.append(("CUDA", torch.cuda.is_available()))
except:
    checks.append(("PyTorch", False))

try:
    import whisper
    checks.append(("Whisper", True))
except:
    checks.append(("Whisper", False))

try:
    from TTS.api import TTS
    checks.append(("TTS", True))
except:
    checks.append(("TTS", False))

try:
    import chromadb
    checks.append(("ChromaDB", True))
except:
    checks.append(("ChromaDB", False))

try:
    from sentence_transformers import SentenceTransformer
    checks.append(("SentenceTransformers", True))
except:
    checks.append(("SentenceTransformers", False))

print("\nInstallation verification:")
for name, status in checks:
    symbol = "✓" if status else "✗"
    print(f"  {symbol} {name}")

all_passed = all(status for _, status in checks)
if all_passed:
    print("\n✓ All checks passed!")
else:
    print("\n✗ Some checks failed - please review the output above")
PYTHON_SCRIPT

echo -e "\n=============================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your settings"
echo "2. Start the server:"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "3. Test the server:"
echo "   curl http://localhost:8000/health"
echo ""
echo "4. View API documentation:"
echo "   http://localhost:8000/docs"
echo ""
