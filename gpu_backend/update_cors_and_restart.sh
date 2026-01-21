#!/bin/bash
# 更新 GPU 后端 CORS 配置并重启服务

set -e

GPU_BACKEND_DIR="/home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend"
ENV_FILE="$GPU_BACKEND_DIR/.env"

echo "=========================================="
echo "GPU 后端 CORS 配置更新和服务重启"
echo "=========================================="
echo ""

# 检查目录是否存在
if [ ! -d "$GPU_BACKEND_DIR" ]; then
    echo "❌ GPU 后端目录不存在: $GPU_BACKEND_DIR"
    echo "   请确认正确的路径"
    exit 1
fi

cd "$GPU_BACKEND_DIR"
echo "✅ 进入目录: $(pwd)"
echo ""

# 步骤 1: 创建或更新 .env 文件
echo "步骤 1: 更新 .env 文件..."
echo "------------------------------------------"

if [ -f "$ENV_FILE" ]; then
    echo "📝 .env 文件已存在，备份中..."
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ 已备份到: ${ENV_FILE}.backup.*"
else
    echo "📝 .env 文件不存在，创建新文件..."
fi

# 使用 Python 更新或创建 .env 文件
python3 << 'PYTHON_SCRIPT'
import os
import re
from datetime import datetime

env_file = '.env'
backup_file = f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'

# 备份现有文件
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        content = f.read()
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"✅ 已备份到: {backup_file}")

# 读取现有内容
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        lines = f.readlines()
else:
    lines = []

# 新的 CORS 配置
new_cors = 'ALLOWED_ORIGINS=["https://smart-success-ai.vercel.app","https://smartsuccess-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000","http://localhost:3001"]\n'

# 更新或添加 ALLOWED_ORIGINS
found = False
for i, line in enumerate(lines):
    if line.strip().startswith('ALLOWED_ORIGINS='):
        lines[i] = new_cors
        found = True
        print(f"✅ 更新了第 {i+1} 行的 ALLOWED_ORIGINS")
        break

if not found:
    # 查找插入位置（在 CORS 注释后）
    insert_pos = len(lines)
    for i, line in enumerate(lines):
        if '# CORS' in line or 'CORS' in line:
            insert_pos = i + 1
            break
    lines.insert(insert_pos, new_cors)
    print(f"✅ 在第 {insert_pos+1} 行添加了 ALLOWED_ORIGINS")

# 写入文件
with open(env_file, 'w') as f:
    f.writelines(lines)

print(f"✅ .env 文件已更新")
print(f"   ALLOWED_ORIGINS={new_cors.strip()}")
PYTHON_SCRIPT

echo ""
echo "验证 .env 文件:"
grep "ALLOWED_ORIGINS" "$ENV_FILE" || echo "⚠️  警告: 未找到 ALLOWED_ORIGINS"
echo ""

# 步骤 2: 停止服务
echo "步骤 2: 停止 GPU 后端服务..."
echo "------------------------------------------"

if [ -f "./stop_service.sh" ]; then
    ./stop_service.sh
else
    echo "⚠️  stop_service.sh 不存在，尝试手动停止..."
    PID=$(pgrep -f "uvicorn main:app" || true)
    if [ -n "$PID" ]; then
        echo "   找到进程 PID: $PID"
        kill $PID 2>/dev/null || true
        sleep 2
        echo "✅ 服务已停止"
    else
        echo "✅ 服务未运行"
    fi
fi

echo ""
sleep 2

# 步骤 3: 启动服务
echo "步骤 3: 启动 GPU 后端服务..."
echo "------------------------------------------"

if [ -f "./start_service.sh" ]; then
    ./start_service.sh
else
    echo "⚠️  start_service.sh 不存在，尝试手动启动..."
    source /home/jovyan/miniconda3/etc/profile.d/conda.sh 2>/dev/null || true
    conda activate gpu_backend 2>/dev/null || source activate gpu_backend 2>/dev/null || true
    
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &
    echo $! > gpu_backend.pid
    echo "✅ 服务已启动 (PID: $(cat gpu_backend.pid))"
fi

echo ""
sleep 3

# 步骤 4: 验证服务
echo "步骤 4: 验证服务状态..."
echo "------------------------------------------"

if [ -f "./status_service.sh" ]; then
    ./status_service.sh
else
    echo "检查服务状态..."
    PID=$(pgrep -f "uvicorn main:app" || true)
    if [ -n "$PID" ]; then
        echo "✅ 服务正在运行 (PID: $PID)"
        echo ""
        echo "健康检查:"
        curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null | head -10 || echo "⚠️  健康检查失败"
    else
        echo "❌ 服务未运行"
    fi
fi

echo ""
echo "=========================================="
echo "✅ 完成！"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 在 Vercel 中设置环境变量: NEXT_PUBLIC_GPU_BACKEND_URL"
echo "2. 重新部署 Vercel 应用"
echo "3. 在浏览器中测试 CORS 是否正常"
echo ""
