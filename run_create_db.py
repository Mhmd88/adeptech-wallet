from app.db import init_engine_session
from app.models import Base  # <-- Base is in app.models, not app.db

# point to your local sqlite dev DB or postgres
database_url = "sqlite:///dev.db"

engine, SessionLocal = init_engine_session(database_url)

# create all tables
Base.metadata.create_all(bind=engine)

print("✅ Database tables initialized successfully.")
