#!/usr/bin/env bash
# Expert Decision Replay Platform - Docker Deployment Script
set -e

echo "==============================================================================="
echo "      EXPERT DECISION REPLAY PLATFORM - DOCKER DEPLOYMENT"
echo "==============================================================================="

if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed or not available in PATH."
    echo "Please install Docker and Docker Compose before running this script."
    exit 1
fi

echo "[*] Building and starting containers in detached mode..."
docker compose up --build -d

echo ""
echo "==============================================================================="
echo "  PLATFORM IS RUNNING IN DOCKER:"
echo "==============================================================================="
echo "  - Frontend UI:      http://localhost:5173 (or http://localhost)"
echo "  - Backend API:      http://localhost:8000"
echo "  - Swagger Docs:     http://localhost:8000/docs"
echo "  - PostgreSQL:       localhost:5432"
echo "==============================================================================="
echo ""
echo "Log command:  docker compose logs -f"
echo "Stop command: docker compose down"
