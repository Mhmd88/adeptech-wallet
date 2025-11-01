# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

Base = declarative_base()

def init_engine_session(database_url: str):
    # SQLite in-memory (tests): single shared connection
    if database_url.startswith("sqlite:///:memory:"):
        engine = create_engine(
            database_url,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # Works for sqlite files and Postgres URLs like:
        # postgresql+psycopg2://user:pass@host:5432/dbname
        engine = create_engine(database_url, future=True)

    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    return engine, SessionLocal
