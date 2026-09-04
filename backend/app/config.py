from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "decision_replay.db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "Expert Decision Replay Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database: Defaults to SQLite for immediate local dev, easily swappable with PostgreSQL
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"
    
    # JWT Security Configuration
    SECRET_KEY: str = "super-secret-jwt-token-key-change-this-in-production-389f4b7a"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
