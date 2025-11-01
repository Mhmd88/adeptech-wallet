from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

def init_engine_session(database_url: str):
    if database_url.startswith("sqlite:///:memory:"):
        engine = create_engine(
            database_url,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,  # ✅ share one connection across sessions
        )
    else:
        engine = create_engine(database_url, future=True)

    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    return engine, SessionLocal
