# 🔧 Fix: "Code not connected to GitHub repository"

## ❌ The Problem

**Error Message:**
```
Unable to deploy
The app's code is not connected to a remote GitHub repository.
```

**What this means:**
- Streamlit Cloud can't find your code on GitHub
- Your code is only on your local computer
- You need to push it to GitHub first

---

## ✅ The Solution (3 Steps)

### Step 1: Push Your Code to GitHub

You need to push your code from your computer to GitHub.

**Option A: Use the Batch Script (Easiest)**
```bash
cd C:\guis
PUSH_TO_GITHUB.bat
```

**Option B: Manual Commands**
```bash
cd C:\guis

# Check if git is initialized
git status

# If not initialized, initialize it
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit: GUIS application"

# Add your GitHub repository
git remote add origin https://github.com/flourencenadarphd-a11y/guis.git

# Set branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

---

### Step 2: Verify Code is on GitHub

1. **Open your browser**
2. **Go to**: https://github.com/flourencenadarphd-a11y/guis
3. **Check that you see:**
   - ✅ `streamlit_app.py` file
   - ✅ `backend/` folder
   - ✅ `data/` folder
   - ✅ `requirements.txt`
   - ✅ Other files

**If you see "404 Not Found":**
- The repository doesn't exist yet
- Go to Step 3 first, then come back to Step 1

---

### Step 3: Create GitHub Repository (If It Doesn't Exist)

**If the repository doesn't exist:**

1. **Go to**: https://github.com/new
2. **Fill in:**
   - **Repository name**: `guis`
   - **Description**: "Global University Intelligence System"
   - **Visibility**: Public (recommended for free Streamlit Cloud)
   - **DO NOT** check "Initialize with README"
   - **DO NOT** add .gitignore or license
3. **Click**: "Create repository"
4. **Then go back to Step 1** to push your code

---

## 🔍 Troubleshooting

### Problem: "Repository not found" when pushing

**Solution:**
1. Make sure repository exists on GitHub (Step 3)
2. Check repository name: `flourencenadarphd-a11y/guis`
3. Verify you have access to the repository

### Problem: "Authentication failed"

**Solution:**
1. GitHub no longer accepts passwords
2. Use a **Personal Access Token** instead:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Name: "GUIS Deployment"
   - Select scope: `repo` (check all repo permissions)
   - Click "Generate token"
   - **Copy the token** (you won't see it again!)
   - When Git asks for password, paste the token instead

### Problem: "Nothing to commit"

**Solution:**
```bash
# Check what files are tracked
git status

# If files show as "untracked", add them
git add .

# Then commit
git commit -m "Initial commit: GUIS application"
```

### Problem: "Remote already exists"

**Solution:**
```bash
# Remove existing remote
git remote remove origin

# Add correct remote
git remote add origin https://github.com/flourencenadarphd-a11y/guis.git

# Or update existing remote
git remote set-url origin https://github.com/flourencenadarphd-a11y/guis.git
```

---

## 📋 Complete Checklist

Before deploying to Streamlit Cloud:

- [ ] Git is installed (`git --version` works)
- [ ] Git is configured (name and email set)
- [ ] GitHub repository exists (`https://github.com/flourencenadarphd-a11y/guis`)
- [ ] Code is pushed to GitHub (you can see files on GitHub)
- [ ] `streamlit_app.py` is in the repository
- [ ] `requirements.txt` is in the repository
- [ ] `backend/` folder is in the repository

---

## 🚀 After Pushing to GitHub

Once your code is on GitHub:

1. **Go back to Streamlit Cloud**: https://share.streamlit.io
2. **Click "New app"** again
3. **Select your repository**: `flourencenadarphd-a11y/guis`
4. **Main file**: `streamlit_app.py`
5. **Click "Deploy"**

**Now it should work!** ✅

---

## 💡 Quick Fix Command

Run this to check and fix everything:

```bash
cd C:\guis

# Check git status
git status

# If not initialized
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: GUIS"

# Set remote (update if exists)
git remote remove origin 2>nul
git remote add origin https://github.com/flourencenadarphd-a11y/guis.git

# Push
git branch -M main
git push -u origin main
```

---

## 🎯 Summary

**The Problem**: Your code is only on your computer, not on GitHub.

**The Solution**: Push your code to GitHub first, then deploy.

**Quick Fix**: Run `PUSH_TO_GITHUB.bat` or use the commands above.

**After pushing**: Go back to Streamlit Cloud and deploy again.

---

**Once your code is on GitHub, Streamlit Cloud will be able to deploy it! 🚀**

