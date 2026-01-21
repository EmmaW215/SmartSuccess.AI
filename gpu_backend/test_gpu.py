#!/usr/bin/env python3
"""GPU Verification Script"""
import torch

print("="*50)
print("GPU 验证结果")
print("="*50)
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"PyTorch version: {torch.__version__}")
print(f"Device count: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    print(f"Device name: {torch.cuda.get_device_name(0)}")
    print(f"Device capability: {torch.cuda.get_device_capability(0)}")
    
    # Test GPU computation
    x = torch.randn(3, 3).cuda()
    y = torch.randn(3, 3).cuda()
    z = torch.matmul(x, y)
    print(f"GPU computation test: SUCCESS")
    print(f"Result tensor device: {z.device}")
else:
    print("WARNING: CUDA is not available!")

print("="*50)
print("验证完成!")
print("="*50)
