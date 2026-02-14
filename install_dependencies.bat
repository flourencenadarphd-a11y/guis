@echo off
echo ========================================
echo GUIS Dependency Installation
echo Python 3.12 Compatible
echo ========================================
echo.

echo [1/3] Upgrading pip...
py -m pip install --upgrade pip
echo.

echo [2/3] Installing core dependencies (without ML packages first)...
py -m pip install fastapi uvicorn[standard] sqlalchemy requests beautifulsoup4 lxml deep-translator langdetect pydantic python-multipart streamlit pandas
if errorlevel 1 (
    echo ERROR: Failed to install core dependencies
    pause
    exit /b 1
)
echo ✅ Core dependencies installed
echo.

echo [3/3] Installing ML dependencies (this may take a few minutes)...
py -m pip install numpy>=1.26.0
py -m pip install scikit-learn>=1.3.2
py -m pip install sentence-transformers>=2.2.2
if errorlevel 1 (
    echo WARNING: Some ML dependencies failed. System will work but ML features may be limited.
)
echo.

echo ========================================
echo ✅ Installation Complete!
echo ========================================
echo.
echo To test: streamlit run streamlit_app.py
echo.
pause

