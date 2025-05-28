from app.core.database import Base, engine
from app.models.user import User
from app.models.file import UploadedFile
from app.core.migrations import migration_manager

def init_db():
    """Initialize the database with migrations"""
    # Apply all migrations
    migration_manager.apply_migrations()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!") 