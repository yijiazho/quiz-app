"""Database migration module for managing database schema changes."""
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging
from .database_config import db_config, DatabaseError

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
        self._migrations: List[Migration] = []
        self._initialized = False
    
    def add_migration(self, version: int, name: str, sql: str) -> None:
        """Add a new migration."""
        self._migrations.append(Migration(version, name, sql))
        # Sort migrations by version
        self._migrations.sort(key=lambda m: m.version)
    
    def init_migrations_table(self) -> None:
        """Initialize the migrations table if it doesn't exist."""
        if not self._initialized:
            try:
                with db_config.engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS migrations (
                            version INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    conn.commit()
                self._initialized = True
                logger.info("Migrations table initialized")
            except SQLAlchemyError as e:
                logger.error(f"Failed to initialize migrations table: {str(e)}")
                raise DatabaseError(f"Failed to initialize migrations table: {str(e)}")
    
    def get_applied_migrations(self) -> List[int]:
        """Get list of applied migration versions."""
        try:
            with db_config.engine.connect() as conn:
                result = conn.execute(text("SELECT version FROM migrations ORDER BY version"))
                return [row[0] for row in result]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get applied migrations: {str(e)}")
            raise DatabaseError(f"Failed to get applied migrations: {str(e)}")
    
    def apply_migrations(self) -> None:
        """Apply all pending migrations."""
        self.init_migrations_table()
        applied = set(self.get_applied_migrations())
        
        for migration in self._migrations:
            if migration.version not in applied:
                try:
                    with db_config.engine.connect() as conn:
                        # Start transaction
                        with conn.begin():
                            # Apply migration
                            conn.execute(text(migration.sql))
                            # Record migration
                            conn.execute(
                                text("INSERT INTO migrations (version, name) VALUES (:version, :name)"),
                                {"version": migration.version, "name": migration.name}
                            )
                    logger.info(f"Applied migration {migration.version}: {migration.name}")
                except SQLAlchemyError as e:
                    logger.error(f"Failed to apply migration {migration.version}: {str(e)}")
                    raise DatabaseError(f"Failed to apply migration {migration.version}: {str(e)}")
    
    def rollback_migration(self, version: int) -> None:
        """Rollback a specific migration."""
        try:
            with db_config.engine.connect() as conn:
                # Start transaction
                with conn.begin():
                    # Remove migration record
                    conn.execute(
                        text("DELETE FROM migrations WHERE version = :version"),
                        {"version": version}
                    )
            logger.info(f"Rolled back migration {version}")
        except SQLAlchemyError as e:
            logger.error(f"Failed to rollback migration {version}: {str(e)}")
            raise DatabaseError(f"Failed to rollback migration {version}: {str(e)}")

# Create migration manager instance
migration_manager = MigrationManager()

# Add initial migrations
migration_manager.add_migration(
    version=1,
    name="create_users_table",
    sql="""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL,
        full_name VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

migration_manager.add_migration(
    version=2,
    name="create_files_table",
    sql="""
    CREATE TABLE IF NOT EXISTS files (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        content_type VARCHAR(100) NOT NULL,
        file_size INTEGER NOT NULL,
        file_content BYTEA NOT NULL,
        title VARCHAR(255),
        description TEXT,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_accessed TIMESTAMP,
        user_id INTEGER REFERENCES users(id)
    )
    """
)

migration_manager.add_migration(
    version=3,
    name="create_parsed_contents_table",
    sql="""
    CREATE TABLE IF NOT EXISTS parsed_contents (
        id SERIAL PRIMARY KEY,
        file_id INTEGER REFERENCES files(id),
        parsed_text TEXT NOT NULL,
        content_type VARCHAR(100) NOT NULL,
        content_metadata JSONB,
        parse_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
) 