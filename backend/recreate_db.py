"""Recreate the database from scratch."""
import os
import logging
from sqlalchemy import text
from app.core.database_config import config, engine
from app.core.database import Base
from app.models import user, file, parsed_content  # Import all models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_database():
    """Recreate the database from scratch."""
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("Dropped all existing tables")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Created all tables")
        
        # Verify tables
        with engine.connect() as conn:
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
            table_names = [table[0] for table in tables]
            logger.info(f"Database tables: {table_names}")
        
        logger.info("Database recreated successfully")
    except Exception as e:
        logger.error(f"Failed to recreate database: {str(e)}")
        raise

if __name__ == "__main__":
    recreate_database() 