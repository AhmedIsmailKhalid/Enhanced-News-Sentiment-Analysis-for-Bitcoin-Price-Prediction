"""
Database connection and session management
"""
import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.shared.logging import get_logger

logger = get_logger(__name__)

# Load environment variables
load_dotenv('.env.dev')

# Get active database configuration
ACTIVE_DATABASE = os.getenv('ACTIVE_DATABASE')
DATABASE_URL = os.getenv('DATABASE_URL')
NEONDB_PRODUCTION_URL = os.getenv('NEONDB_PRODUCTION_URL')
NEONDB_BACKUP_URL = os.getenv('NEONDB_BACKUP_URL')

# Select database URL based on ACTIVE_DATABASE setting
if ACTIVE_DATABASE == 'neondb_production' and NEONDB_PRODUCTION_URL:
    ACTIVE_DB_URL = NEONDB_PRODUCTION_URL
    logger.info("Using NeonDB Production database")
elif ACTIVE_DATABASE == 'neondb_backup' and NEONDB_BACKUP_URL:
    ACTIVE_DB_URL = NEONDB_BACKUP_URL
    logger.info("Using NeonDB Backup database")
elif not ACTIVE_DATABASE:
    raise ValueError("ACTIVE_DATABASE environment variable must be set in .env.dev")
else:
    ACTIVE_DB_URL = DATABASE_URL
    logger.info("Using local PostgreSQL database")

# Create engine
engine = create_engine(
    ACTIVE_DB_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,
    max_overflow=10
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    
    Usage:
        from fastapi import Depends
        from src.shared.database import get_db
        
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # use db session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """Test database connection"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False