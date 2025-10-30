import os, tempfile, pytest
from app.db import init_engine_session
from app.models import Base

@pytest.fixture()
def session():
    engine, SessionLocal = init_engine_session("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as s:
        yield s