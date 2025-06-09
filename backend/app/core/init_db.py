"""Initialize the database and run migrations."""
import logging
from .database_config import config, engine
from .migrations import run_migrations
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database and run migrations."""
    try:
        # Create tables
        config.init_db()
        
        # Run migrations
        with Session(engine) as db:
            run_migrations(db)
            
        logger.info("Database initialized and migrations applied successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database() 