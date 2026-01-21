#!/bin/bash
# Check SmartSuccess.AI GPU Backend Service Status

cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend

echo "=========================================="
echo "Service Status"
echo "=========================================="
echo ""

# Check PID file
if [ -f gpu_backend.pid ]; then
    PID=$(cat gpu_backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Service is running (PID: $PID)"
        ps -p $PID -o pid,ppid,cmd,etime
    else
        echo "⚠️  PID file exists but process not running"
        rm gpu_backend.pid
    fi
else
    # Check by process name
    PID=$(pgrep -f "uvicorn main:app")
    if [ -n "$PID" ]; then
        echo "✅ Service is running (PID: $PID)"
        ps -p $PID -o pid,ppid,cmd,etime
    else
        echo "❌ Service is not running"
    fi
fi

echo ""
echo "------------------------------------------"

# Check health endpoint
echo "Health Check:"
HEALTH=$(curl -s http://localhost:8000/health 2>&1)
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    echo "✅ Health check passed"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null | head -15
else
    echo "⚠️  Health check failed"
    echo "$HEALTH"
fi

echo ""
echo "------------------------------------------"

# Check logs
if [ -f gpu_backend_service.log ]; then
    echo "Recent logs (last 5 lines):"
    tail -5 gpu_backend_service.log
else
    echo "No log file found"
fi

echo ""
echo "=========================================="
