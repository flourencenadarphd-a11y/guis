# 🚀 GUIS Deployment Guide

## 📋 Single Working Streamlit App

**File:** `streamlit_app.py` (in project root)

This is a **standalone Streamlit app** that combines backend and frontend functionality in one file for easy deployment.

### Quick Start (Local)

```bash
cd C:\guis
streamlit run streamlit_app.py
```

Opens at: `http://localhost:8501`

---

## 🌐 Deployment to Streamlit Cloud

### Step 1: Prepare GitHub Repository

#### Required GitHub Details:

1. **Repository Name**: `guis` (or your preferred name)
2. **Repository Visibility**: Public (for free Streamlit Cloud) or Private
3. **Branch**: `main` or `master`

#### Files to Include:

```
guis/
├── streamlit_app.py          # ⭐ Main app file
├── backend/                  # Backend modules
│   ├── database.py
│   ├── scraper.py
│   ├── translator.py
│   ├── language_detector.py
│   ├── ml_classifier.py
│   ├── metadata_checker.py
│   ├── gotouni_checker.py
│   └── ai_query.py
├── data/
│   └── gotouniversity.csv
├── requirements.txt          # ⭐ Dependencies
├── README.md
└── .gitignore
```

#### Files to Exclude (in .gitignore):

```
*.db
*.pkl
__pycache__/
*.pyc
venv/
.env
```

### Step 2: Create GitHub Repository

1. **Go to GitHub**: https://github.com/new
2. **Repository name**: `guis` (or your choice)
3. **Description**: "Global University Intelligence System"
4. **Visibility**: Public (recommended for free hosting)
5. **Initialize**: Don't add README, .gitignore, or license (we have them)
6. **Click**: "Create repository"

### Step 3: Push Code to GitHub

```bash
# Initialize git (if not already)
cd C:\guis
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: GUIS application"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/guis.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: https://share.streamlit.io
2. **Sign in** with GitHub account
3. **Click**: "New app"
4. **Fill in**:
   - **Repository**: Select `YOUR_USERNAME/guis`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py` ⭐
   - **App URL**: `guis` (or your choice)
5. **Advanced settings** (optional):
   - **Python version**: 3.11
   - **Environment variables** (if needed):
     - `GEMINI_API_KEY` (for AI features)
     - `OPENAI_API_KEY` (for AI features)
6. **Click**: "Deploy"

### Step 5: Wait for Deployment

- First deployment takes 2-5 minutes
- Streamlit will install dependencies
- Watch the logs for any errors
- Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

## 🔧 Alternative: Deploy Backend + Frontend Separately

### Option A: Streamlit Cloud (Frontend) + Railway (Backend)

#### Frontend (Streamlit Cloud):
- Use `frontend/app.py`
- Set API URL to backend URL in sidebar

#### Backend (Railway):
1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select repository
4. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables if needed
6. Get backend URL
7. Update frontend API URL

### Option B: Render (Both)

#### Backend:
1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repository
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy

#### Frontend:
1. New → Web Service
2. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0`
3. Add environment variable: `API_BASE_URL` = backend URL
4. Deploy

---

## 📝 Required GitHub Information

### For Streamlit Cloud Deployment:

1. **GitHub Username**: Your GitHub username
2. **Repository Name**: `guis` (or your choice)
3. **Branch**: `main`
4. **Main File**: `streamlit_app.py`
5. **Python Version**: 3.11 (recommended)

### Repository Structure:

```
guis/
├── streamlit_app.py          # Main app (for standalone)
├── frontend/
│   └── app.py                # Frontend (for separate deployment)
├── backend/
│   └── main.py               # Backend API (for separate deployment)
├── data/
│   └── gotouniversity.csv
├── requirements.txt
├── README.md
├── .gitignore
└── Procfile                  # For Heroku/Railway
```

---

## 🔑 Environment Variables (Optional)

If using AI features, add these in Streamlit Cloud:

1. Go to app settings
2. Click "Secrets"
3. Add:
   ```
   GEMINI_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```

---

## ✅ Testing Before Deployment

### Local Test:

```bash
# Test standalone app
streamlit run streamlit_app.py

# Test backend (if separate)
cd backend
python main.py

# Test frontend (if separate)
cd frontend
streamlit run app.py
```

### Verify:

1. ✅ App loads without errors
2. ✅ Can fetch universities
3. ✅ Can search programs
4. ✅ Database creates successfully
5. ✅ All dependencies install

---

## 🐛 Common Deployment Issues

### Issue: "Module not found"

**Solution**: Ensure all backend modules are in `backend/` folder and `streamlit_app.py` imports them correctly.

### Issue: "Database error"

**Solution**: SQLite works on Streamlit Cloud, but ensure file paths are relative.

### Issue: "Timeout during scraping"

**Solution**: This is normal. Scraping can take time. Consider adding progress indicators.

### Issue: "Dependencies fail to install"

**Solution**: Check `requirements.txt` for version conflicts. Some packages may need specific versions.

---

## 🎯 Recommended Deployment Strategy

### For Quick Demo:
- **Use**: `streamlit_app.py` on Streamlit Cloud
- **Pros**: Simple, one-click deploy
- **Cons**: Limited resources, slower for heavy scraping

### For Production:
- **Backend**: Railway/Render (FastAPI)
- **Frontend**: Streamlit Cloud (Streamlit)
- **Database**: PostgreSQL (instead of SQLite)
- **Pros**: Scalable, faster, more reliable
- **Cons**: More complex setup

---

## 📞 Deployment Checklist

Before deploying:

- [ ] All code pushed to GitHub
- [ ] `requirements.txt` is complete
- [ ] `streamlit_app.py` works locally
- [ ] Database paths are relative
- [ ] No hardcoded paths
- [ ] Environment variables set (if needed)
- [ ] `.gitignore` excludes sensitive files
- [ ] README.md is updated

---

## 🎉 Your Working Link

After deployment, your app will be available at:

**Streamlit Cloud**: `https://YOUR_APP_NAME.streamlit.app`

Replace `YOUR_APP_NAME` with the name you chose during deployment.

---

## 📚 Additional Resources

- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs

---

**Ready to deploy? Follow the steps above and your GUIS app will be live! 🚀**

