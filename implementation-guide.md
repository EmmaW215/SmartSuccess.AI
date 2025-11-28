# SmartSuccess.AI - Implementation Guide

## Summary of Changes

| Task | Files to Update | Status |
|------|-----------------|--------|
| 1. Rename to SmartSuccess.AI | `layout.tsx`, `page.tsx` | ✅ Ready |
| 2. Fix Visitor Counter | `SimpleVisitorCounter.tsx`, `main.py` (backend) | ✅ Ready |
| 3. Add Demo Page | New file: `demo/page.tsx` | ✅ Ready |

---

## Step-by-Step Implementation

### Step 1: Update the Backend (Render)

Add the visitor counter endpoints to your **`resume-matcher-backend/main.py`**:

```python
# Add these imports at the TOP of main.py (if not already present)
import json
from pathlib import Path
from datetime import datetime

# Add this AFTER your existing imports, BEFORE app = FastAPI()
# Visitor counter storage
VISITOR_COUNT_FILE = Path("visitor_count.json")

def get_visitor_count() -> int:
    """Get current visitor count from file"""
    try:
        if VISITOR_COUNT_FILE.exists():
            with open(VISITOR_COUNT_FILE, 'r') as f:
                data = json.load(f)
                return data.get('count', 0)
    except Exception as e:
        print(f"Error reading visitor count: {e}")
    return 0

def save_visitor_count(count: int):
    """Save visitor count to file"""
    try:
        with open(VISITOR_COUNT_FILE, 'w') as f:
            json.dump({'count': count, 'updated_at': datetime.now().isoformat()}, f)
    except Exception as e:
        print(f"Error saving visitor count: {e}")

# Initialize count if file doesn't exist
if not VISITOR_COUNT_FILE.exists():
    save_visitor_count(100)  # Start with a base number

# Add these NEW ENDPOINTS after your existing endpoints

@app.get("/api/visitor/count")
async def get_visitor_count_endpoint():
    """Get current visitor count"""
    count = get_visitor_count()
    return JSONResponse(content={"count": count})

@app.post("/api/visitor/increment")
async def increment_visitor_count():
    """Increment and return visitor count"""
    current_count = get_visitor_count()
    new_count = current_count + 1
    save_visitor_count(new_count)
    return JSONResponse(content={"count": new_count})
```

**Deploy to Render** after making these changes.

---

### Step 2: Update Frontend Files

#### File 1: `resume-matcher-frontend/src/app/layout.tsx`

**Replace the entire file with:**

```tsx
import { Inter, Roboto_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], weight: ['400', '700'] });
const robotoMono = Roboto_Mono({ subsets: ['latin'], weight: ['400'] });

export const metadata = {
  title: 'SmartSuccess.AI - AI-Powered Career Success Platform',
  description: 'AI-powered resume optimization, job matching analysis, and mock interview preparation to accelerate your career success.',
  keywords: 'AI resume, job matching, mock interview, career success, resume optimization',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.className}>
      <body>
        <main className={robotoMono.className}>{children}</main>
      </body>
    </html>
  );
}
```

---

#### File 2: `resume-matcher-frontend/src/app/components/SimpleVisitorCounter.tsx`

**Replace the entire file** with the code from the **"SmartSuccess.AI - Frontend Updates"** artifact (File 2).

---

#### File 3: `resume-matcher-frontend/src/app/page.tsx`

**Replace the entire file** with the code from the **"SmartSuccess.AI - Updated page.tsx"** artifact.

---

#### File 4: Create NEW file `resume-matcher-frontend/src/app/demo/page.tsx`

1. Create folder: `resume-matcher-frontend/src/app/demo/`
2. Create file: `page.tsx` inside that folder
3. Copy the entire code from the **"SmartSuccess.AI - Demo Page"** artifact

---

### Step 3: Test Locally

```bash
# In resume-matcher-frontend directory
npm run dev

# Test these pages:
# http://localhost:3000          - Main page with new branding
# http://localhost:3000/demo     - Demo page
```

---

### Step 4: Deploy to Vercel

```bash
# Commit and push changes
git add .
git commit -m "Rebrand to SmartSuccess.AI, fix visitor counter, add demo page"
git push origin main

# Vercel will auto-deploy
```

---

## Visual Changes Summary

### Before → After

| Element | Before | After |
|---------|--------|-------|
| **Title** | MatchWise | SmartSuccess.AI |
| **Subtitle** | Tailor Your Resume... | Same, but with gradient styling |
| **Description** | Resume Comparison Platform | AI-Powered Career Success Platform |
| **Demo Button** | None | Purple gradient button → /demo |
| **Visitor Counter** | localStorage (broken) | Backend API (persistent) |
| **Footer** | © MatchWise | © SmartSuccess.AI |
| **Coming Soon** | None | Mock Interview button (disabled) |

---

## Folder Structure After Changes

```
resume-matcher-frontend/
└── src/
    └── app/
        ├── layout.tsx              ← UPDATED
        ├── page.tsx                ← UPDATED
        ├── globals.css             (unchanged)
        ├── components/
        │   └── SimpleVisitorCounter.tsx  ← UPDATED
        ├── demo/                   ← NEW FOLDER
        │   └── page.tsx            ← NEW FILE
        └── api/
            └── visitor-count/      (can delete - no longer needed)
```

---

## Troubleshooting

### Visitor Counter Still Shows "..."
- Check if backend is deployed with new endpoints
- Test endpoint directly: `curl https://your-backend.onrender.com/api/visitor/count`
- Check browser console for errors

### Demo Page Not Found (404)
- Make sure you created the folder `demo/` inside `src/app/`
- Make sure the file is named exactly `page.tsx`
- Restart dev server: `npm run dev`

### Styling Issues
- Clear browser cache
- Delete `.next` folder and rebuild: `rm -rf .next && npm run build`

---

## Next Steps (After These Changes)

Once these 3 items are complete, we can proceed with:
1. **Week 2**: RAG Layer implementation
2. **Week 3**: Voice Interview Agent
3. **Week 4**: Integration & Polish

Ready to proceed? 🚀
