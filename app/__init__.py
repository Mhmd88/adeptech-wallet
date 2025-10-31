from flask import Flask
from app.db import init_engine_session
from app.models import Base

# Global session factory 
engine = None
SessionLocal = None


def create_app(testing: bool = False) -> Flask:
    """Flask app factory pattern"""
    global engine, SessionLocal

    app = Flask(__name__)


    if testing:
        # in-memory DB for pytest
        database_url = "sqlite:///:memory:"
    else:
        # prefer env var DATABASE_URL, fallback to local dev.db
        import os
        database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")

    engine, SessionLocal = init_engine_session(database_url)

    # Create tables 
    Base.metadata.create_all(bind=engine)

    # -------------------------
    # Blueprint registration (will add soon)
    # -------------------------
    from app.routes import register_blueprints
    register_blueprints(app)

    # -------------------------
    # Simple health check route
    # -------------------------
    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app
