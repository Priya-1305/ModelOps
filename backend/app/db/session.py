import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.config import settings
from backend.app.db.base import Base

db_url = os.environ.get("DATABASE_URL", settings.DATABASE_URL)

# Configure engine with pool settings appropriate for SQLite vs PostgreSQL
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
    echo=settings.DB_ECHO,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and safely closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in database if they don't exist."""
    # Ensure all models are imported so metadata is populated
    import backend.app.db.models  # noqa
    Base.metadata.create_all(bind=engine)
