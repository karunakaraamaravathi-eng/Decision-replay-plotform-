@echo off
title Expert Decision Replay Platform - Docker Launcher
color 0B

echo ===============================================================================
echo       EXPERT DECISION REPLAY PLATFORM - DOCKER PRODUCTION DEPLOYMENT
echo ===============================================================================
echo.

where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not detected in your PATH.
    echo Please make sure Docker Desktop is installed, running, and accessible.
    echo Download: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo [*] Building and launching containers with Docker Compose...
docker compose up --build -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Docker containers.
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo   SERVICES ARE RUNNING VIA DOCKER:
echo ===============================================================================
echo   - Frontend UI:        http://localhost:5173 (or http://localhost)
echo   - Backend API:        http://localhost:8000
echo   - Swagger API Docs:   http://localhost:8000/docs
echo   - PostgreSQL DB:      localhost:5432
echo ===============================================================================
echo.
echo To view container logs:   docker compose logs -f
echo To stop containers:       docker compose down
echo.
pause
