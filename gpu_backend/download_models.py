#!/usr/bin/env python3
"""Download ML models for GPU Backend"""
import sys

print("="*60)
print("下载 ML 模型")
print("="*60)

# 1. Whisper
try:
    print("\n1. Downloading Whisper large-v3...")
    import whisper
    model = whisper.load_model('large-v3')
    print("✅ Whisper model downloaded and loaded")
except Exception as e:
    print(f"❌ Whisper error: {e}")
    sys.exit(1)

# 2. Sentence Transformers
try:
    print("\n2. Downloading embedding model...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    print("✅ Embedding model downloaded and loaded")
except Exception as e:
    print(f"❌ Embedding model error: {e}")
    sys.exit(1)

# 3. TTS
try:
    print("\n3. Downloading TTS model...")
    from TTS.api import TTS
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
    print("✅ TTS model downloaded and loaded")
except Exception as e:
    print(f"⚠️  TTS model warning: {e}")
    print("   (TTS is optional, continuing...)")

print("\n" + "="*60)
print("✅ All models downloaded!")
print("="*60)
