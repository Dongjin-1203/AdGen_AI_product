# backend/app/db/base.py
"""
Database configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from config import settings

logger = logging.getLogger(__name__)

# DATABASE_URL 읽기
DATABASE_URL = settings.DATABASE_URL

logger.info(f"🔧 DATABASE_URL: {DATABASE_URL[:50] if DATABASE_URL else 'Not set'}...")

# PostgreSQL 연결
if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    logger.info("🐘 Using PostgreSQL")
    
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,  # 연결 체크
    )
else:
    logger.warning("⚠️ DATABASE_URL not set, using default SQLite")
    engine = create_engine(
        "sqlite:///./adgen.db",
        connect_args={"check_same_thread": False},
        echo=False
    )

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

logger.info("✅ Database configuration loaded")