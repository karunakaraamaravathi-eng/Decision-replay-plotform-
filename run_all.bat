@echo off
title Expert Decision Replay Platform Launcher
color 0A

echo ===============================================================================
echo            EXPERT DECISION REPLAY PLATFORM (MILESTONE 1, 2 & 3)
echo ===============================================================================
echo.
echo  [1/3] Verifying Python and Node environments...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH. Please install Python 3.10+
    pause
    exit /b 1
)

echo  [2/3] Launching FastAPI Backend Server on http://localhost:8000 ...
start "Backend API (FastAPI :8000)" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 2 /nobreak >nul

echo  [3/3] Launching React Vite Frontend Server on http://localhost:5173 ...
start "Frontend UI (React Vite :5173)" cmd /k "cd /d "%~dp0frontend" && call npm.cmd run dev"
timeout /t 3 /nobreak >nul

echo.
echo ===============================================================================
echo   PLATFORM IS NOW RUNNING LIVE IN YOUR BROWSER!
echo ===============================================================================
echo   - Web Application:       http://localhost:5173
echo   - Interactive CLI:       http://localhost:5173/terminal
echo   - Reports Center:        http://localhost:5173/reports
echo   - Swagger API Docs:      http://localhost:8000/docs
echo.
echo   DEMO CREDENTIALS:
echo   - Manager:               manager@company.com  / Password123!
echo   - Administrator:         admin@company.com    / Password123!
echo   - Reviewer:              reviewer@company.com / Password123!
echo   - Employee:              employee@company.com / Password123!
echo.
echo   CLI MANAGEMENT IN TERMINAL:
echo   - Run 'python cli.py status' to inspect platform metrics
echo   - Run 'python cli.py decisions list' to list decisions
echo   - Run 'python cli.py audit tail' to view audit log trail
echo ===============================================================================
echo.
echo Opening default web browser to http://localhost:5173 ...
start http://localhost:5173

pause
