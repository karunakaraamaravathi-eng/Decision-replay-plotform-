# Expert Decision Replay Platform - PowerShell Launcher
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host "           EXPERT DECISION REPLAY PLATFORM (MILESTONE 1, 2 & 3)" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Green

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "`n[1/3] Starting Backend FastAPI Server..." -ForegroundColor Yellow
Start-Process cmd.exe -ArgumentList "/k cd /d `"$scriptDir\backend`" && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 2

Write-Host "[2/3] Starting Frontend React Vite Server..." -ForegroundColor Yellow
Start-Process cmd.exe -ArgumentList "/k cd /d `"$scriptDir\frontend`" && call npm.cmd run dev"

Start-Sleep -Seconds 3

Write-Host "`n[3/3] Platform is active!" -ForegroundColor Green
Write-Host " - Web UI:          http://localhost:5173" -ForegroundColor White
Write-Host " - Terminal CLI:    http://localhost:5173/terminal" -ForegroundColor White
Write-Host " - Reports:         http://localhost:5173/reports" -ForegroundColor White
Write-Host " - API Swagger:     http://localhost:8000/docs" -ForegroundColor White

Write-Host "`nDemo Accounts: (Password for all is 'Password123!')" -ForegroundColor Magenta
Write-Host " - manager@company.com"
Write-Host " - admin@company.com"
Write-Host " - reviewer@company.com"
Write-Host " - employee@company.com"

Start-Process "http://localhost:5173"
