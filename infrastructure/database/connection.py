from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    database_url: str = "postgresql://postgres:postgres@localhost:5432/event_ticketing"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    All database models must inherit from this class.
    """
    pass


engine = create_engine(
    settings.database_url,
    echo=settings.debug,   # Log SQL queries when debug=True
    pool_pre_ping=True,    # Verify connection before using from pool
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    Dependency function for FastAPI.
    Yields a database session and ensures it is closed after use.
    Usage in FastAPI: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables defined in ORM models."""
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Drop all tables — use with caution, for testing only."""
    Base.metadata.drop_all(bind=engine)