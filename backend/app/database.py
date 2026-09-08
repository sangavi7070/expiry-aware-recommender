"""Database connection and initialization module for ExpiryAware."""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database path in the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "expiry_aware.db"
DATABASE_URL = f"sqlite:///{DB_FILE.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency to yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(seed_if_empty: bool = True):
    """Initialize database tables and automatically seed data if empty."""
    from . import models
    from .seed_data import populate_database

    Base.metadata.create_all(bind=engine)

    if seed_if_empty:
        db = SessionLocal()
        try:
            batch_count = db.query(models.InventoryBatch).count()
            if batch_count == 0:
                populate_database(db)
        finally:
            db.close()
