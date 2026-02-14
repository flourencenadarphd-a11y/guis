@echo off
echo ========================================
echo Push GUIS to GitHub with Token
echo ========================================
echo.
echo IMPORTANT: You need a Personal Access Token!
echo.
echo If you don't have one:
echo 1. Go to: https://github.com/settings/tokens
echo 2. Generate new token (classic)
echo 3. Select 'repo' scope
echo 4. Copy the token
echo.
echo Press any key when ready...
pause
echo.

echo [1/4] Checking git status...
git status
echo.

echo [2/4] Adding all files...
git add .
echo ✅ Files added
echo.

echo [3/4] Committing changes...
git commit -m "Initial commit: GUIS application with Python 3.12 compatibility"
if errorlevel 1 (
    echo ℹ️  Nothing new to commit (files already committed)
)
echo.

echo [4/4] Pushing to GitHub...
echo.
echo When prompted for credentials:
echo   Username: flourencenadarphd-a11y
echo   Password: [Paste your Personal Access Token here]
echo.
echo ⚠️  Note: GitHub no longer accepts passwords!
echo    You MUST use a Personal Access Token.
echo.
pause

git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo ❌ Push Failed!
    echo ========================================
    echo.
    echo Common issues:
    echo 1. Wrong username - use: flourencenadarphd-a11y
    echo 2. Used password instead of token - use Personal Access Token
    echo 3. Repository doesn't exist - create it on GitHub first
    echo 4. No access to repository - check permissions
    echo.
    echo Get help: See FIX_AUTHENTICATION.md
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
    echo Next: Deploy to Streamlit Cloud
    echo 1. Go to: https://share.streamlit.io
    echo 2. New app → Select: flourencenadarphd-a11y/guis
    echo 3. Main file: streamlit_app.py
    echo 4. Deploy!
    echo.
)

pause

