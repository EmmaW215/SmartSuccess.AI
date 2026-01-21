#!/bin/bash
# Test GPU Backend Server

echo "=========================================="
echo "Testing GPU Backend Server"
echo "=========================================="
echo ""

# Test 1: Basic Health Check
echo "1. Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    echo "✅ Health check passed"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool
else
    echo "❌ Health check failed"
    echo "$HEALTH_RESPONSE"
    exit 1
fi

echo ""
echo "------------------------------------------"

# Test 2: GPU Status
echo "2. Checking GPU status..."
if echo "$HEALTH_RESPONSE" | grep -q '"gpu_available":true'; then
    echo "✅ GPU is available"
else
    echo "⚠️  GPU is not available"
fi

echo ""
echo "------------------------------------------"

# Test 3: GPU Status
echo "3. Testing /health/gpu/status endpoint..."
GPU_RESPONSE=$(curl -s http://localhost:8000/health/gpu/status)
if echo "$GPU_RESPONSE" | grep -q '"available"'; then
    echo "✅ GPU status check passed"
    echo "$GPU_RESPONSE" | python3 -m json.tool
else
    echo "⚠️  GPU status check"
    echo "$GPU_RESPONSE"
fi

echo ""
echo "------------------------------------------"

# Test 4: API Documentation
echo "4. Checking API documentation..."
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ "$DOCS_STATUS" = "200" ]; then
    echo "✅ API docs available at http://localhost:8000/docs"
else
    echo "⚠️  API docs not accessible (status: $DOCS_STATUS)"
fi

echo ""
echo "=========================================="
echo "✅ All tests completed!"
echo "=========================================="
echo ""
echo "Server is running at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "ReDoc: http://localhost:8000/redoc"
