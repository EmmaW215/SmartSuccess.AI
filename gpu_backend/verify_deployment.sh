#!/bin/bash
# Verify SmartSuccess.AI GPU Backend Deployment

echo "=========================================="
echo "Verifying Deployment"
echo "=========================================="
echo ""

# Step 1: Check service status
echo "1. Checking systemd service status..."
if systemctl is-active --quiet smartsuccess-gpu.service 2>/dev/null; then
    echo "✅ Service is running"
    sudo systemctl status smartsuccess-gpu.service --no-pager -l | head -15
else
    echo "⚠️  Service status check (may need sudo)"
    echo "   Run: sudo systemctl status smartsuccess-gpu"
fi

echo ""
echo "------------------------------------------"

# Step 2: Check if server is responding
echo "2. Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/health 2>&1)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Health check passed (HTTP $HTTP_CODE)"
    echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
    
    # Check GPU status
    if echo "$RESPONSE_BODY" | grep -q '"gpu_available":true'; then
        echo ""
        echo "✅ GPU is available and working"
    else
        echo ""
        echo "⚠️  GPU not available"
    fi
else
    echo "❌ Health check failed (HTTP $HTTP_CODE)"
    echo "Response: $RESPONSE_BODY"
fi

echo ""
echo "------------------------------------------"

# Step 3: Check service logs
echo "3. Recent service logs (last 10 lines)..."
if command -v journalctl >/dev/null 2>&1; then
    sudo journalctl -u smartsuccess-gpu.service -n 10 --no-pager 2>/dev/null || echo "   (Requires sudo to view logs)"
else
    echo "   journalctl not available, checking application log..."
    if [ -f "gpu_backend.log" ]; then
        tail -10 gpu_backend.log
    else
        echo "   No log file found"
    fi
fi

echo ""
echo "------------------------------------------"

# Step 4: Check API documentation
echo "4. Checking API documentation..."
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>&1)
if [ "$DOCS_STATUS" = "200" ]; then
    echo "✅ API docs accessible at http://localhost:8000/docs"
else
    echo "⚠️  API docs not accessible (HTTP $DOCS_STATUS)"
fi

echo ""
echo "------------------------------------------"

# Step 5: Check process
echo "5. Checking uvicorn process..."
if pgrep -f "uvicorn main:app" > /dev/null; then
    echo "✅ Uvicorn process is running"
    ps aux | grep "uvicorn main:app" | grep -v grep | head -2
else
    echo "⚠️  No uvicorn process found"
fi

echo ""
echo "=========================================="
echo "Verification Complete!"
echo "=========================================="
echo ""
echo "Service endpoints:"
echo "  Health:     http://localhost:8000/health"
echo "  API Docs:   http://localhost:8000/docs"
echo "  Root:       http://localhost:8000/"
echo ""
echo "Useful commands:"
echo "  View logs:  sudo journalctl -u smartsuccess-gpu -f"
echo "  Restart:    sudo systemctl restart smartsuccess-gpu"
echo "  Status:     sudo systemctl status smartsuccess-gpu"
