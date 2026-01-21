#!/bin/bash
# Stop SmartSuccess.AI GPU Backend Service

cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend

if [ -f gpu_backend.pid ]; then
    PID=$(cat gpu_backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping service (PID: $PID)..."
        kill $PID
        sleep 2
        
        # Check if still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "Force killing..."
            kill -9 $PID
        fi
        
        rm gpu_backend.pid
        echo "✅ Service stopped"
    else
        echo "Service not running (stale PID file)"
        rm gpu_backend.pid
    fi
else
    # Try to find by process name
    PID=$(pgrep -f "uvicorn main:app")
    if [ -n "$PID" ]; then
        echo "Found running process (PID: $PID), stopping..."
        kill $PID
        echo "✅ Service stopped"
    else
        echo "Service not running"
    fi
fi
