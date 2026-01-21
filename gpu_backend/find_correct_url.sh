#!/bin/bash
# Script to help find the correct GPU Backend URL

echo "=========================================="
echo "Finding Correct GPU Backend URL"
echo "=========================================="
echo ""

# Check if service is running
echo "1. Checking if GPU Backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ GPU Backend is running on port 8000"
    curl -s http://localhost:8000/health | python3 -m json.tool | head -10
else
    echo "❌ GPU Backend is not running"
    echo "   Start it with: ./start_service.sh"
    exit 1
fi

echo ""
echo "------------------------------------------"
echo "2. Current Service Information:"
echo "   - Service is running on: localhost:8000"
echo "   - Health endpoint: http://localhost:8000/health"
echo ""

echo "------------------------------------------"
echo "3. How to find the public URL:"
echo ""
echo "   Option A: Check Inference.ai Console"
echo "   - Go to your Inference.ai project"
echo "   - Open 'Overview' page"
echo "   - Look for 'HTTP Ports' section"
echo "   - Find port :8000 entry"
echo "   - Copy the URL (format: https://xxx-8000.cluster3.service-inference.ai)"
echo ""

echo "   Option B: Based on JupyterLab URL"
echo "   If your JupyterLab URL is:"
echo "   jupyter-labs-8888-1769018572503320273.cluster3.service-inference.ai"
echo ""
echo "   Try these formats for port 8000:"
echo "   - https://your-service-8000-1769018572503320273.cluster3.service-inference.ai"
echo "   - https://1769018572503320273-8000.cluster3.service-inference.ai"
echo "   - https://gpu-backend-8000-1769018572503320273.cluster3.service-inference.ai"
echo ""

echo "------------------------------------------"
echo "4. Test the URL:"
echo ""
echo "   Once you have a candidate URL, test it:"
echo "   curl https://your-candidate-url/health"
echo ""
echo "   Expected response:"
echo "   {\"status\":\"healthy\",\"gpu_available\":true,...}"
echo ""

echo "------------------------------------------"
echo "5. Vercel Configuration:"
echo ""
echo "   Environment Variable:"
echo "   Key: NEXT_PUBLIC_GPU_BACKEND_URL"
echo "   Value: https://your-service-8000-xxxxx.cluster3.service-inference.ai"
echo ""
echo "   Important:"
echo "   - Use HTTPS (not HTTP)"
echo "   - Port should be 8000 (not 8888)"
echo "   - No ?token= parameter"
echo "   - No trailing slash"
echo ""

echo "=========================================="
echo "Next Steps:"
echo "1. Check Inference.ai console for port 8000 URL"
echo "2. Test the URL with: curl https://url/health"
echo "3. Add to Vercel as NEXT_PUBLIC_GPU_BACKEND_URL"
echo "4. Redeploy Vercel application"
echo "=========================================="
