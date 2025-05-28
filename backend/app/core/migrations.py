"""Database migration module for managing database schema changes."""
from typing import List, Optional, Dict, Callable
from sqlalchemy import text, func
from sqlalchemy.exc import SQLAlchemyError
import logging
from .database_config import config, DatabaseError
from sqlalchemy.orm import Session
from datetime import datetime

logger = logging.getLogger(__name__)

class Migration:
    """Represents a database migration."""
    def __init__(self, version: int, name: str, sql: str):
        self.version = version
        self.name = name
        self.sql = sql

class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self):
        self._migrations: Dict[int, Migration] = {}
        self._init_migrations()
    
    def _init_migrations(self):
        """Initialize the list of migrations."""
        # Migration 1: Create users table
        self._migrations[1] = Migration(
            1,
            "create_users_table",
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        # Migration 2: Create uploaded_files table
        self._migrations[2] = Migration(
            2,
            "create_uploaded_files_table",
            """
            CREATE TABLE IF NOT EXISTS uploaded_files (
                file_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_content BLOB NOT NULL,
                upload_time TIMESTAMP NOT NULL,
                last_accessed TIMESTAMP,
                title TEXT,
                description TEXT,
                user_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        
        # Migration 3: Create parsed_contents table
        self._migrations[3] = Migration(
            3,
            "create_parsed_contents_table",
            """
            CREATE TABLE IF NOT EXISTS parsed_contents (
                id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                file_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                parsed_text TEXT,
                content_metadata JSON,
                parse_time TIMESTAMP NOT NULL,
                last_updated TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES uploaded_files(file_id)
            )
            """
        )
        
        # Migration 4: Create quizzes table
        self._migrations[4] = Migration(
            4,
            "create_quizzes_table",
            """
            CREATE TABLE IF NOT EXISTS quizzes (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                user_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )

    def init_migrations_table(self, db: Session) -> None:
        """Initialize the migrations table if it doesn't exist."""
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to initialize migrations table: {str(e)}")
            raise

    def get_applied_migrations(self, db: Session) -> list[int]:
        """Get the list of applied migrations."""
        try:
            result = db.execute(text("SELECT version FROM migrations ORDER BY version")).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {str(e)}")
            raise

    def apply_migrations(self, db: Session) -> None:
        """Apply all pending migrations."""
        try:
            self.init_migrations_table(db)
            applied = set(self.get_applied_migrations(db))
            
            for version, migration in sorted(self._migrations.items()):
                if version not in applied:
                    try:
                        # Apply migration
                        db.execute(text(migration.sql))
                        # Record migration
                        db.execute(
                            text("INSERT INTO migrations (version, name) VALUES (:version, :name)"),
                            {"version": version, "name": migration.name}
                        )
                        db.commit()
                        logger.info(f"Applied migration {version}: {migration.name}")
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Failed to apply migration {version}: {str(e)}")
                        raise
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise RuntimeError(f"Database migration failed: {str(e)}")

# Create a singleton instance
migration_manager = MigrationManager()

def run_migrations(db: Session) -> None:
    """Run all pending migrations."""
    migration_manager.apply_migrations(db) 