@echo off
echo ========================================
echo Automated Streamlit Cloud Deployment
echo ========================================
echo.
echo This script will:
echo 1. Set up GitHub (if needed)
echo 2. Push your code to GitHub
echo 3. Give you the Streamlit Cloud link
echo.
echo Press any key to continue...
pause
echo.

REM Step 1: Check if git is initialized
echo [1/6] Checking Git setup...
if not exist .git (
    echo Initializing Git repository...
    git init
    echo ✅ Git initialized
) else (
    echo ✅ Git already initialized
)
echo.

REM Step 2: Configure Git (if not configured)
echo [2/6] Configuring Git...
git config user.name >nul 2>&1
if errorlevel 1 (
    echo Git user name not set. Please enter your name:
    set /p GIT_NAME="Your name: "
    git config --global user.name "%GIT_NAME%"
)
git config user.email >nul 2>&1
if errorlevel 1 (
    echo Git email not set. Please enter your email:
    set /p GIT_EMAIL="Your email: "
    git config --global user.email "%GIT_EMAIL%"
)
echo ✅ Git configured
echo.

REM Step 3: Add all files
echo [3/6] Adding files to Git...
git add .
echo ✅ Files added
echo.

REM Step 4: Commit
echo [4/6] Committing changes...
git commit -m "Deploy to Streamlit Cloud - GUIS Application" >nul 2>&1
if errorlevel 1 (
    echo ℹ️  No new changes to commit (files already committed)
) else (
    echo ✅ Changes committed
)
echo.

REM Step 5: Set up remote
echo [5/6] Setting up GitHub remote...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/flourencenadarphd-a11y/guis.git
echo ✅ Remote configured
echo.

REM Step 6: Push to GitHub
echo [6/6] Pushing to GitHub...
echo.
echo ⚠️  IMPORTANT: You need a Personal Access Token!
echo.
echo If you don't have one:
echo 1. Go to: https://github.com/settings/tokens
echo 2. Click "Generate new token (classic)"
echo 3. Name: "GUIS Deployment"
echo 4. Select scope: repo (check all)
echo 5. Generate and copy the token
echo.
echo When prompted:
echo   Username: flourencenadarphd-a11y
echo   Password: [Paste your Personal Access Token]
echo.
pause

git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo ❌ Push Failed - Authentication Issue
    echo ========================================
    echo.
    echo Common fixes:
    echo 1. Make sure you used Personal Access Token (not password)
    echo 2. Check repository exists: https://github.com/flourencenadarphd-a11y/guis
    echo 3. If repository doesn't exist, create it first:
    echo    - Go to: https://github.com/new
    echo    - Name: guis
    echo    - Click "Create repository"
    echo    - Then run this script again
    echo.
    echo For detailed help, see: FIX_AUTHENTICATION.md
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo ✅ SUCCESS! Code pushed to GitHub!
    echo ========================================
    echo.
    echo Your repository:
    echo https://github.com/flourencenadarphd-a11y/guis
    echo.
    echo ========================================
    echo 🚀 NEXT: Deploy to Streamlit Cloud
    echo ========================================
    echo.
    echo Follow these steps:
    echo.
    echo 1. Go to: https://share.streamlit.io
    echo 2. Sign in with GitHub
    echo 3. Click "New app"
    echo 4. Fill in:
    echo    - Repository: flourencenadarphd-a11y/guis
    echo    - Branch: main
    echo    - Main file path: streamlit_app.py ⭐
    echo    - App URL: guis (or your choice)
    echo 5. Click "Deploy"
    echo.
    echo Your app will be live at:
    echo https://guis.streamlit.app
    echo.
    echo ========================================
    echo.
    pause
)

