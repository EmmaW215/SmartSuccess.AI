#!/bin/bash
# 启动 GPU 后端服务（修复版 - 使用 base conda 环境）

cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend

echo "=========================================="
echo "启动 SmartSuccess.AI GPU Backend"
echo "=========================================="
echo ""

# 检查是否已在运行
if [ -f gpu_backend.pid ]; then
    PID=$(cat gpu_backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  服务已在运行 (PID: $PID)"
        echo "   如需重启，请先运行: ./stop_service.sh"
        exit 1
    else
        rm gpu_backend.pid
    fi
fi

# 激活 conda base 环境
echo "激活 conda 环境..."
source /home/jovyan/miniconda3/etc/profile.d/conda.sh
conda activate base

# 检查 uvicorn 是否安装
echo "检查依赖..."
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "⚠️  uvicorn 未安装，正在安装..."
    pip install uvicorn[standard] fastapi pydantic pydantic-settings
fi

# 检查其他关键依赖
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  fastapi 未安装，正在安装..."
    pip install fastapi
fi

# 启动服务
echo ""
echo "启动服务..."
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &
PID=$!

# 保存 PID
echo $PID > gpu_backend.pid

echo "✅ 服务已启动"
echo "   PID: $PID"
echo "   日志: gpu_backend_service.log"
echo "   PID 文件: gpu_backend.pid"
echo ""

# 等待几秒
sleep 3

# 验证
echo "验证服务状态..."
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ 进程正在运行"
    
    # 测试健康端点
    sleep 2
    HEALTH=$(curl -s http://localhost:8000/health 2>&1)
    if echo "$HEALTH" | grep -q '"status"'; then
        echo "✅ 健康检查通过"
        echo "$HEALTH" | python -m json.tool 2>/dev/null | head -10
    else
        echo "⚠️  健康检查失败，查看日志:"
        tail -10 gpu_backend_service.log
    fi
else
    echo "❌ 进程启动失败，查看日志:"
    tail -20 gpu_backend_service.log
fi

echo ""
echo "=========================================="
echo "检查状态: ./status_service.sh"
echo "停止服务: ./stop_service.sh"
echo "查看日志: tail -f gpu_backend_service.log"
echo "=========================================="
