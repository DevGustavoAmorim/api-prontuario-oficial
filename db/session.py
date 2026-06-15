from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./pdf.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    """
    Cria uma sessão para cada requisição
    e fecha automaticamente ao final.
    """
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()