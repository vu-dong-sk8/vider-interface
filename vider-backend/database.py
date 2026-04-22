"""
Database configuration — PostgreSQL (production) / SQLite (development fallback).

Priority:
  1. DATABASE_URL env var  →  used as-is
  2. No DATABASE_URL       →  falls back to local SQLite ``vider_dev.db``
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL (or any other DB the user configured)
    engine = create_engine(DATABASE_URL, echo=False)
else:
    # SQLite fallback for quick local testing
    _sqlite_path = os.path.join(os.path.dirname(__file__), "vider_dev.db")
    DATABASE_URL = f"sqlite:///{_sqlite_path}"
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},  # SQLite specific
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
