#!/bin/bash
# 检查 GPU 后端服务状态

echo "=========================================="
echo "GPU 后端服务状态检查"
echo "=========================================="
echo ""

# 检查进程
echo "1. 检查运行中的进程:"
echo "------------------------------------------"
PROCESSES=$(ps aux | grep "uvicorn main:app" | grep -v grep)
if [ -n "$PROCESSES" ]; then
    echo "⚠️  发现运行中的进程:"
    echo "$PROCESSES"
    echo ""
    echo "进程 ID (PID):"
    echo "$PROCESSES" | awk '{print $2}'
else
    echo "✅ 没有运行中的 uvicorn 进程"
fi

echo ""
echo "------------------------------------------"

# 检查端口
echo "2. 检查端口 8000:"
echo "------------------------------------------"
PORT_CHECK=$(netstat -tuln 2>/dev/null | grep ":8000" || ss -tuln 2>/dev/null | grep ":8000" || lsof -i :8000 2>/dev/null)
if [ -n "$PORT_CHECK" ]; then
    echo "⚠️  端口 8000 被占用:"
    echo "$PORT_CHECK"
else
    echo "✅ 端口 8000 未被占用"
fi

echo ""
echo "------------------------------------------"

# 检查 PID 文件
echo "3. 检查 PID 文件:"
echo "------------------------------------------"
if [ -f "gpu_backend.pid" ]; then
    PID=$(cat gpu_backend.pid)
    echo "PID 文件存在，内容: $PID"
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  PID $PID 对应的进程仍在运行"
    else
        echo "✅ PID $PID 对应的进程已停止（可以删除 PID 文件）"
        echo "   建议删除: rm gpu_backend.pid"
    fi
else
    echo "✅ 没有 PID 文件"
fi

echo ""
echo "------------------------------------------"

# 测试健康端点
echo "4. 测试健康端点:"
echo "------------------------------------------"
HEALTH_RESPONSE=$(curl -s -w "\nHTTP Status: %{http_code}" http://localhost:8000/health 2>&1)
if echo "$HEALTH_RESPONSE" | grep -q "HTTP Status: 200"; then
    echo "⚠️  健康端点响应正常 - 服务可能仍在运行"
    echo "$HEALTH_RESPONSE" | head -5
else
    echo "✅ 健康端点无响应 - 服务已停止"
    if echo "$HEALTH_RESPONSE" | grep -q "Connection refused"; then
        echo "   (连接被拒绝 - 这是正常的，说明服务已停止)"
    fi
fi

echo ""
echo "=========================================="

# 总结
echo ""
echo "总结:"
if [ -z "$PROCESSES" ] && [ -z "$PORT_CHECK" ]; then
    echo "✅ 服务已完全停止，可以安全启动新服务"
else
    echo "⚠️  服务可能仍在运行，建议再次停止:"
    echo "   pkill -f 'uvicorn main:app'"
    echo "   或"
    echo "   kill -9 <PID>"
fi
echo ""
