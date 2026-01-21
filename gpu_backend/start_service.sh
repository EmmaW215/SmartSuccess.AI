#!/bin/bash
# Start SmartSuccess.AI GPU Backend Service (without systemd)

cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend

# Check if already running
if [ -f gpu_backend.pid ]; then
    PID=$(cat gpu_backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Service is already running (PID: $PID)"
        exit 1
    else
        rm gpu_backend.pid
    fi
fi

# Activate conda environment
source /home/jovyan/miniconda3/etc/profile.d/conda.sh
conda activate gpu_backend

# Start service in background
echo "Starting SmartSuccess.AI GPU Backend..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &
PID=$!

# Save PID
echo $PID > gpu_backend.pid

echo "✅ Service started with PID: $PID"
echo "   Logs: gpu_backend_service.log"
echo "   PID file: gpu_backend.pid"
echo ""
echo "Check status: ./status_service.sh"
echo "Stop service: ./stop_service.sh"
