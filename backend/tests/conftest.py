import pytest
from sqlalchemy.orm import clear_mappers
from app.core.database_config import DatabaseConfig
from app.models import UploadedFile, ParsedContent
from app.models.user import User

@pytest.fixture(scope="session")
def db_config():
    """Create a test database configuration."""
    config = DatabaseConfig(env="test")
    clear_mappers()
    config.init_db()
    yield config
    config.drop_db()

@pytest.fixture(scope="session")
def engine(db_config):
    """Get the test database engine."""
    return db_config.engine

@pytest.fixture(scope="session")
def SessionLocal(db_config):
    """Get the test session factory."""
    return db_config.SessionLocal

@pytest.fixture
def db(SessionLocal):
    """Create a test database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db):
    """Create a test client with a test database session."""
    from app.main import app
    from app.core.database import get_db
    
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear() 