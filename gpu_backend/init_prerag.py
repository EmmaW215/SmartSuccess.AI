#!/usr/bin/env python3
"""Initialize Pre-RAG Question Bank"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("初始化 Pre-RAG 题库")
print("="*60)

try:
    from services import get_prerag_service
    
    print("\n正在初始化 Pre-RAG 服务...")
    service = get_prerag_service()
    
    print("获取统计信息...")
    stats = service.get_stats()
    
    print("\n" + "="*60)
    print(f"✅ Pre-RAG 初始化完成!")
    print(f"   总问题数: {stats.total_questions}")
    print(f"   分类分布: {stats.by_category}")
    print(f"   难度分布: {stats.by_difficulty}")
    print(f"   最后更新: {stats.last_updated}")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ 初始化错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
