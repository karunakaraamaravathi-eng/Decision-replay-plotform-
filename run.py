import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"[*] Starting {settings.PROJECT_NAME}...")
    print(f"[*] Access Web UI at: http://127.0.0.1:8000")
    print(f"[*] Access Swagger API Docs at: http://127.0.0.1:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
