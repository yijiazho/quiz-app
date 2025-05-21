from typing import Optional, Generator, Any
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabaseError(Exception):
    """Base exception for database-related errors."""
    pass

class DatabaseConfig:
    """Database configuration class that handles environment-specific settings."""
    
    def __init__(self, env: str = "development"):
        self.env = env
        self._engine: Optional[Engine] = None
        self._SessionLocal: Optional[sessionmaker] = None
        self.Base = declarative_base()
        self._initialized = False
        
    @property
    def database_url(self) -> str:
        """Get the database URL based on the environment."""
        if self.env == "test":
            return "sqlite:///:memory:"
        return os.getenv("DATABASE_URL", "sqlite:///./quiz_app.db")
    
    @property
    def engine(self) -> Engine:
        """Get or create the database engine."""
        if self._engine is None:
            try:
                self._engine = create_engine(
                    self.database_url,
                    echo=self.env != "production",
                    connect_args={"check_same_thread": False} if self.database_url.startswith("sqlite") else {}
                )
            except Exception as e:
                logger.error(f"Failed to create database engine: {str(e)}")
                raise DatabaseError(f"Failed to create database engine: {str(e)}")
        return self._engine
    
    @property
    def SessionLocal(self) -> sessionmaker:
        """Get or create the session factory."""
        if self._SessionLocal is None:
            try:
                self._SessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self.engine
                )
            except Exception as e:
                logger.error(f"Failed to create session factory: {str(e)}")
                raise DatabaseError(f"Failed to create session factory: {str(e)}")
        return self._SessionLocal
    
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
        if not self._initialized:
            try:
                self.Base.metadata.create_all(bind=self.engine)
                self._initialized = True
                logger.info("Database initialized successfully")
            except SQLAlchemyError as e:
                logger.error(f"Failed to initialize database: {str(e)}")
                raise DatabaseError(f"Failed to initialize database: {str(e)}")
    
    def drop_db(self) -> None:
        """Drop all tables from the database."""
        try:
            self.Base.metadata.drop_all(bind=self.engine)
            self._initialized = False
            logger.info("Database dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop database: {str(e)}")
            raise DatabaseError(f"Failed to drop database: {str(e)}")
    
    def is_initialized(self) -> bool:
        """Check if the database has been initialized."""
        return self._initialized
    
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
                if self.database_url.startswith("sqlite"):
                    version = "SQLite"
                    # Get table count for SQLite
                    table_count = conn.execute(text(
                        "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                    )).scalar()
                else:
                    version = conn.execute(text("SELECT version()")).scalar()
                    # Get table count for PostgreSQL
                    table_count = conn.execute(text(
                        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
                    )).scalar()
                
                return {
                    "version": version,
                    "table_count": table_count,
                    "initialized": self._initialized,
                    "environment": self.env
                }
        except SQLAlchemyError as e:
            logger.error(f"Failed to get database info: {str(e)}")
            raise DatabaseError(f"Failed to get database info: {str(e)}")

# Create default database configuration
db_config = DatabaseConfig(env=os.getenv("ENVIRONMENT", "development")) 