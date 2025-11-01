from flask import Flask
from app.db import init_engine_session
from app.models import Base

engine = None
SessionLocal = None

def create_app(testing: bool = False, database_url: str | None = None) -> Flask:
    """Flask app factory pattern."""
    global engine, SessionLocal
    app = Flask(__name__)

    if database_url is None:
        import os
        if testing:
            # 👇 allow env override in tests, else in-memory
            database_url = os.getenv("DATABASE_URL", "sqlite:///:memory:")
        else:
            database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")

    engine, SessionLocal = init_engine_session(database_url)
    Base.metadata.create_all(bind=engine)

    from app.routes import register_blueprints
    register_blueprints(app)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app
