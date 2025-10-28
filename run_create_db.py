from app.db import init_engine_session, Base


if __name__ == "__main__":
 engine, _ = init_engine_session() # uses ./dev.db by default
 Base.metadata.create_all(bind=engine)
 print("✅ Database initialized: tables created in dev.db")