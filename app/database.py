import os
import sys

# Ensure workspace root is in sys.path when running standalone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Create engine for SQLite / PostgreSQL
engine = sqlalchemy.create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to provide database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  DATABASE MODULE: ENGINE & SESSION CHECK")
    print("=" * 60)
    print(f"[*] Database URL: {settings.DATABASE_URL}")
    print(f"[*] Engine:       {engine}")
    print("[*] Testing session connection...")
    db = SessionLocal()
    try:
        print("[OK] Database session established successfully!")
    finally:
        db.close()
    print("=" * 60 + "\n")
