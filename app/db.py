from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass

def init_engine_session(database_url: str = "sqlite:///dev.db"):
    engine = create_engine(database_url, future=True)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    return engine, SessionLocal
