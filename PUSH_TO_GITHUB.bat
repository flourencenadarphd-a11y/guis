@echo off
echo ========================================
echo Push GUIS to GitHub
echo ========================================
echo.

echo Your GitHub Repository:
echo https://github.com/flourencenadarphd-a11y/guis.git
echo.

echo [1/5] Checking git status...
git status
if errorlevel 1 (
    echo Initializing git...
    git init
)
echo.

echo [2/5] Adding all files...
git add .
echo ✅ Files added
echo.

echo [3/5] Committing changes...
git commit -m "Initial commit: GUIS application with Python 3.12 compatibility"
if errorlevel 1 (
    echo WARNING: Nothing to commit or commit failed
)
echo.

echo [4/5] Setting remote...
git remote remove origin 2>nul
git remote add origin https://github.com/flourencenadarphd-a11y/guis.git
echo ✅ Remote set
echo.

echo [5/5] Pushing to GitHub...
git branch -M main
git push -u origin main
if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Possible reasons:
    echo 1. Repository doesn't exist on GitHub - create it first
    echo 2. Authentication needed - use: git config --global user.name "Your Name"
    echo 3. Need to authenticate - GitHub may prompt for credentials
    echo.
    echo To create repository:
    echo 1. Go to: https://github.com/new
    echo 2. Name: guis
    echo 3. Click "Create repository"
    echo 4. Then run this script again
    echo.
) else (
    echo.
    echo ========================================
    echo ✅ SUCCESS! Pushed to GitHub!
    echo ========================================
    echo.
    echo Your repository:
    echo https://github.com/flourencenadarphd-a11y/guis
    echo.
    echo Next step: Deploy to Streamlit Cloud
    echo 1. Go to: https://share.streamlit.io
    echo 2. Sign in with GitHub
    echo 3. New app → Select: flourencenadarphd-a11y/guis
    echo 4. Main file: streamlit_app.py
    echo 5. Deploy!
    echo.
)
echo.
pause

