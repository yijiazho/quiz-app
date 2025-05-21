"""Database module that exports commonly used database components."""
from .database_config import db_config

# Export commonly used components
engine = db_config.engine
SessionLocal = db_config.SessionLocal
Base = db_config.Base
get_db = db_config.get_db 