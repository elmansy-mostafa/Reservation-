# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models_base import Base  # Import Base from the new models_base module

DATABASE_URL = "sqlite:///./test.db"  # Adjust this path if necessary.

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()