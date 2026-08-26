import os

class Settings:
    PROJECT_NAME: str = "Expert Decision Replay Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "expert_decision_replay_platform_secret_key_2026_infosys_milestone1")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./decision_replay.db")
    
    # Roles
    ROLE_EMPLOYEE: str = "Employee"
    ROLE_REVIEWER: str = "Reviewer"
    ROLE_MANAGER: str = "Manager"
    ROLE_ADMINISTRATOR: str = "Administrator"
    
    VALID_ROLES: list = ["Employee", "Reviewer", "Manager", "Administrator"]

settings = Settings()
