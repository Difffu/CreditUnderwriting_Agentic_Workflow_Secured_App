from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from ..config import settings
from ..utils.logger import logger
from contextlib import contextmanager


# Create database URL
DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    try:
        # Check if database exists, if not, create it
        if not database_exists(engine.url):
            create_database(engine.url)
            logger.info(f"Database {settings.POSTGRES_DB} created successfully.")
        else:
            logger.info(f"Database {settings.POSTGRES_DB} already exists.")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database or tables: {str(e)}")
        raise

# Database dependency for FastAPI
# @contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()