@echo off
echo ===================================================
echo   Expert Decision Replay Platform - Backend Setup
echo ===================================================
echo.

echo [1/3] Checking Python installation...
python --version
if errorlevel 1 (
    echo [ERROR] Python is not found in PATH. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

echo.
echo [2/3] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [3/3] Initializing and Seeding Database...
call reset_db.bat

echo.
echo ===================================================
echo [SUCCESS] Backend and FastAPI Setup Completed!
echo To run the server, execute: run_backend.bat
echo Or run: python run.py
echo ===================================================
pause
