@echo off
echo ========================================================
echo Initializing Git Repository for Expert Decision Replay
echo ========================================================

git init
git add .
git commit -m "Milestone 1 & 2 Completed: Decision Management, Alternative Matrix, Discussions, File Uploads, Version Tracking, Auth & RBAC"
git branch -M main

echo.
echo ========================================================
echo Git repository initialized locally!
echo Next step: Add your GitHub remote URL using:
echo   git remote add origin https://github.com/YOUR_USERNAME/expert-decision-replay-platform.git
echo   git push -u origin main
echo ========================================================
pause
