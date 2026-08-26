@echo off
echo ========================================================
echo Initializing Git Repository for Expert Decision Replay
echo ========================================================

git init
git add .
git commit -m "Milestone 1 (Week 1-2): Complete FastAPI backend, JWT Auth, Database Design, User Management & UI Wireframes"
git branch -M main

echo.
echo ========================================================
echo Git repository initialized locally!
echo Next step: Add your GitHub remote URL using:
echo   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo   git push -u origin main
echo ========================================================
pause
