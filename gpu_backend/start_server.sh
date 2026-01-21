#!/bin/bash
# Start GPU Backend Server

cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend

# Activate conda environment
source /home/jovyan/miniconda3/etc/profile.d/conda.sh
conda activate gpu_backend

# Start uvicorn server
echo "Starting GPU Backend server..."
echo "Server will be available at: http://0.0.0.0:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
