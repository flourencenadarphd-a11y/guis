# 🚀 GitHub Setup - Complete Guide

## ✅ Your GitHub Repository Details

**Repository URL**: `https://github.com/flourencenadarphd-a11y/guis.git`
**Branch**: `main`
**Username**: `flourencenadarphd-a11y`

---

## 📋 Step-by-Step GitHub Setup

### Step 1: Fix Dependencies First

The current `requirements.txt` has Python 3.12 compatibility issues. Let's fix it:

```bash
# Use the updated requirements
py -m pip install -r requirements_py312.txt

# OR install manually (recommended)
install_dependencies.bat
```

### Step 2: Initialize Git (if not done)

```bash
cd C:\guis
git init
```

### Step 3: Create/Update .gitignore

Make sure `.gitignore` includes:
```
*.db
*.sqlite
*.pkl
__pycache__/
*.pyc
venv/
.env
*.log
```

### Step 4: Add All Files

```bash
git add .
```

### Step 5: Commit

```bash
git commit -m "Initial commit: GUIS application with Python 3.12 compatibility"
```

### Step 6: Connect to Your GitHub Repository

```bash
git remote add origin https://github.com/flourencenadarphd-a11y/guis.git
```

If you already added it, update:
```bash
git remote set-url origin https://github.com/flourencenadarphd-a11y/guis.git
```

### Step 7: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

---

## 🔧 Fixing the Dependency Issue

### Option 1: Use Updated Requirements (Recommended)

```bash
# Install using Python 3.12 compatible versions
py -m pip install -r requirements_py312.txt
```

### Option 2: Install Manually

```bash
# Core packages
py -m pip install fastapi uvicorn[standard] sqlalchemy requests beautifulsoup4 lxml deep-translator langdetect pydantic python-multipart streamlit pandas

# ML packages (install separately)
py -m pip install "numpy>=1.26.0"
py -m pip install "scikit-learn>=1.3.2"
py -m pip install "sentence-transformers>=2.2.2"
```

### Option 3: Use the Batch Script

```bash
install_dependencies.bat
```

---

## 📝 Update requirements.txt for GitHub

Before pushing, update `requirements.txt` to be Python 3.12 compatible:

```bash
# Copy the Python 3.12 compatible version
copy requirements_py312.txt requirements.txt
```

Or manually update `requirements.txt` to use `>=` instead of `==` for versions.

---

## ✅ Complete GitHub Push Commands

```bash
# Navigate to project
cd C:\guis

# Fix dependencies first
py -m pip install -r requirements_py312.txt

# Initialize git (if needed)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: GUIS with Python 3.12 support"

# Add remote (your repository)
git remote add origin https://github.com/flourencenadarphd-a11y/guis.git

# Set branch
git branch -M main

# Push
git push -u origin main
```

---

## 🚀 Deploy to Streamlit Cloud

After pushing to GitHub:

1. **Go to**: https://share.streamlit.io
2. **Sign in** with GitHub
3. **Click**: "New app"
4. **Fill in**:
   - **Repository**: `flourencenadarphd-a11y/guis`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py` ⭐
   - **App URL**: `guis` (or your choice)
5. **Click**: "Deploy"

**Your link**: `https://guis.streamlit.app`

---

## 🔍 Verify Your Repository

After pushing, check:
- https://github.com/flourencenadarphd-a11y/guis

You should see:
- ✅ `streamlit_app.py`
- ✅ `backend/` folder
- ✅ `data/gotouniversity.csv`
- ✅ `requirements.txt` (updated)
- ✅ `README.md`

---

## ⚠️ Important Notes

1. **Python Version**: Streamlit Cloud uses Python 3.11 by default, but our requirements work with both 3.11 and 3.12
2. **Dependencies**: The updated requirements use `>=` instead of `==` for better compatibility
3. **ML Packages**: May take longer to install on Streamlit Cloud (this is normal)
4. **Database**: SQLite works fine on Streamlit Cloud

---

## 🎯 Quick Checklist

Before pushing:
- [ ] Dependencies installed successfully
- [ ] `streamlit_app.py` works locally
- [ ] `requirements.txt` is updated (Python 3.12 compatible)
- [ ] `.gitignore` excludes sensitive files
- [ ] All files are in the repository

After pushing:
- [ ] Repository is visible on GitHub
- [ ] All files are present
- [ ] Streamlit Cloud can deploy

---

## 📞 If You Get Errors

### "Permission denied"
- Check GitHub authentication
- Use: `git config --global user.name "Your Name"`
- Use: `git config --global user.email "your.email@example.com"`

### "Repository not found"
- Check repository name: `flourencenadarphd-a11y/guis`
- Verify you have access
- Check if repository exists on GitHub

### "Dependencies fail on Streamlit Cloud"
- Ensure `requirements.txt` uses `>=` not `==`
- Check Python version compatibility
- Some packages may need time to install

---

**Ready? Follow the steps above to push to GitHub! 🚀**

