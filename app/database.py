from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
<<<<<<< HEAD
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
=======
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/api_fortress_db",
)

engine = create_engine(DATABASE_URL)
>>>>>>> 36b22f616c006a8fae6fd7833e030d6d32b07ede
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
