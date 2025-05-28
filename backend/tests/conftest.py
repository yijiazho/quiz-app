import pytest
from app.core.database_config import config, Base
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.migrations import run_migrations
import logging
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def test_db():
    """Create a test database session."""
    # Create all tables
    Base.metadata.create_all(bind=config.engine)
    
    # Create a new session
    connection = config.engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        # Drop all tables
        Base.metadata.drop_all(bind=config.engine)

@pytest.fixture
def client(test_db):
    """Create a test client with a test database session."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass  # Don't close the session here, it's managed by the test_db fixture
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def db(test_db):
    """Create a fresh database for each test."""
    # Clear the tables
    test_db.execute(text("DELETE FROM parsed_contents"))
    test_db.execute(text("DELETE FROM uploaded_files"))
    test_db.commit()
    
    try:
        yield test_db
    finally:
        # Clear the tables after the test
        test_db.execute(text("DELETE FROM parsed_contents"))
        test_db.execute(text("DELETE FROM uploaded_files"))
        test_db.commit() 