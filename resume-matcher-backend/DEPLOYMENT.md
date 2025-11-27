# SmartSuccess.AI Backend Deployment Guide

## Render Deployment

### Prerequisites
- GitHub account with repository access
- Render account (https://render.com)
- Stripe account (for payments)
- Firebase project (for user management)
- OpenAI/xAI API keys

### Setup Steps

1. **Create New Web Service on Render**
   - Connect your GitHub repository
   - Root Directory: `resume-matcher-backend`

2. **Configure Build Settings**
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**
   Set the following in Render dashboard:
   ```
   PYTHON_VERSION=3.9.0
   OPENAI_API_KEY=your_openai_api_key
   XAI_API_KEY=your_xai_api_key
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

4. **Secret Files**
   - Upload your `serviceAccountKey.json` (Firebase Admin SDK key) as a "Secret File" in Render.
   - Filename on Render: `serviceAccountKey.json`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

### Health Check
- Endpoint: `GET /health`
- Expected Response: `{"status": "ok"}`

### API Endpoints
- `POST /api/compare` - Resume comparison
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/user/status` - User status
- `GET /api/user/can-generate` - Check generation limits
- `POST /api/create-checkout-session` - Stripe checkout
- `POST /api/stripe-webhook` - Stripe webhook

## Local Development

1. **Setup Environment**
   - Place `serviceAccountKey.json` in the `resume-matcher-backend` folder.
   - Create a `.env` file with the variables listed above.

2. **Run Server**
   ```bash
   cd resume-matcher-backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

## Troubleshooting

### CORS Issues
Ensure frontend domain is in `ALLOWED_ORIGINS` environment variable.

### API Key Issues
Verify API keys are correctly set in environment variables.

### Firebase/Stripe Errors
Check if `serviceAccountKey.json` is present and Stripe keys are valid.
