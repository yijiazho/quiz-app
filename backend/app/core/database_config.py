from typing import Optional, Generator, Any
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
from dotenv import load_dotenv
from app.core.database import Base  # <-- Use shared Base

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabaseError(Exception):
    """Base exception for database-related errors."""
    pass

class DatabaseConfig:
    """Database configuration class that handles environment-specific settings."""
    
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        # self.Base = declarative_base()  # REMOVE THIS
        
        if test_mode:
            # Use file-based SQLite for testing to ensure all connections share the same DB
            self.SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
            self.engine = create_engine(
                self.SQLALCHEMY_DATABASE_URL,
                connect_args={"check_same_thread": False}
            )
        else:
            # Use file-based SQLite for production
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            os.makedirs(db_path, exist_ok=True)
            self.SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(db_path, 'quiz.db')}"
            self.engine = create_engine(
                self.SQLALCHEMY_DATABASE_URL,
                connect_args={"check_same_thread": False}
            )
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_db(self) -> Generator[Session, None, None]:
        """Get a database session."""
        db = self.SessionLocal()
        try:
            yield db
        except SQLAlchemyError as e:
            logger.error(f"Database session error: {str(e)}")
            db.rollback()
            raise DatabaseError(f"Database session error: {str(e)}")
        finally:
            db.close()
    
    def init_db(self) -> None:
        """Initialize the database by creating all tables."""
        try:
            # Create all tables defined in models
            Base.metadata.create_all(bind=self.engine)
            
            # Verify tables exist
            with self.engine.connect() as conn:
                tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
                table_names = [table[0] for table in tables]
                logger.info(f"Created tables: {table_names}")
            
            logger.info("Database initialized successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise DatabaseError(f"Failed to initialize database: {str(e)}")
    
    def drop_db(self) -> None:
        """Drop all tables from the database."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop database: {str(e)}")
            raise DatabaseError(f"Failed to drop database: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test the database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def get_db_info(self) -> dict[str, Any]:
        """Get database information."""
        try:
            with self.engine.connect() as conn:
                # Get database version
                if self.SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
                    version = "SQLite"
                    # Get table count for SQLite
                    table_count = conn.execute(text(
                        "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                    )).scalar()
                else:
                    version = conn.execute(text("SELECT version()"))
                    # Get table count for PostgreSQL
                    table_count = conn.execute(text(
                        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
                    )).scalar()
                
                return {
                    "version": version,
                    "table_count": table_count,
                    "initialized": True,
                    "environment": "production" if not self.test_mode else "test"
                }
        except SQLAlchemyError as e:
            logger.error(f"Failed to get database info: {str(e)}")
            raise DatabaseError(f"Failed to get database info: {str(e)}")

# Create a singleton instance
config = DatabaseConfig()

# Export commonly used items
engine = config.engine
get_db = config.get_db

# Remove the following line to avoid creating a second engine instance
# db_config = DatabaseConfig() 