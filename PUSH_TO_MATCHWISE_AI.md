# Push to matchwise-ai Repository Guide

## ✅ Current Status

- ✅ Git remote updated to: `https://github.com/EmmaW215/matchwise-ai.git`
- ✅ All changes committed (commit: f6fc121)
- ⚠️ Ready to push (requires authentication)

## 🔐 Authentication Required

To push to GitHub, you need to authenticate. Choose one method:

### Method 1: Personal Access Token (Recommended)

1. **Create a Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: "SmartSuccess.AI Push"
   - Select scopes: `repo` (full control of private repositories)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again!)

2. **Push using token:**
   ```bash
   cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI
   git push -u origin main
   ```
   - When prompted for username: Enter `EmmaW215`
   - When prompted for password: **Paste your Personal Access Token** (not your GitHub password)

### Method 2: SSH Key (Alternative)

1. **Check if SSH key exists:**
   ```bash
   ls -la ~/.ssh/id_rsa.pub
   ```

2. **If no SSH key, generate one:**
   ```bash
   ssh-keygen -t ed25519 -C "emma.w215@users.noreply.github.com"
   # Press Enter to accept default location
   # Press Enter twice for no passphrase (or set one)
   ```

3. **Add SSH key to GitHub:**
   ```bash
   cat ~/.ssh/id_rsa.pub
   # Copy the output
   ```
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste the key and save

4. **Update remote to use SSH:**
   ```bash
   cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI
   git remote set-url origin git@github.com:EmmaW215/matchwise-ai.git
   git push -u origin main
   ```

## 📤 Push Command

Once authenticated, run:
```bash
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI
git push -u origin main
```

## 🔍 Verify Push

After pushing, verify at:
https://github.com/EmmaW215/matchwise-ai

## 📝 What Will Be Pushed

- All committed changes including:
  - TypeScript fixes for Web Speech API
  - GPU backend scripts
  - Interview page updates
  - All project files from SmartSuccess.AI
