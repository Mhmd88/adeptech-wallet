from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base  # <- from models package

def init_engine_session(database_url: str = "sqlite:///dev.db"):
    engine = create_engine(database_url, future=True)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    return engine, SessionLocal
