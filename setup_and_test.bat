@echo off
echo ========================================
echo GUIS Setup and Test Script
echo ========================================
echo.

echo [1/4] Installing dependencies...
py -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

echo [2/4] Testing imports...
py -c "import fastapi, streamlit, sqlalchemy, requests, pandas; print('✅ All core modules imported successfully')"
if errorlevel 1 (
    echo ERROR: Import test failed
    pause
    exit /b 1
)
echo.

echo [3/4] Testing backend initialization...
cd backend
py -c "from database import Database; db = Database(); print('✅ Database initialized'); print('✅ Backend modules working')"
if errorlevel 1 (
    echo ERROR: Backend test failed
    cd ..
    pause
    exit /b 1
)
cd ..
echo.

echo [4/4] Testing standalone app...
py -c "import sys; sys.path.insert(0, 'backend'); from database import Database; print('✅ Standalone app imports working')"
if errorlevel 1 (
    echo ERROR: Standalone app test failed
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✅ ALL TESTS PASSED!
echo ========================================
echo.
echo To start the app:
echo   1. Backend: cd backend ^&^& py main.py
echo   2. Frontend: cd frontend ^&^& streamlit run app.py
echo   3. Standalone: streamlit run streamlit_app.py
echo.
pause

