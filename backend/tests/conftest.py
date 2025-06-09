import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.database import Base
from app.main import app
from app.core.database_config import get_db
import logging

logger = logging.getLogger(__name__)

# Use file-based SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_DB_PATH = "./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db_file():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    yield
    # Do not remove at teardown to avoid PermissionError

@pytest.fixture(scope="function")
def test_db():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Create a test client with a test database session."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass  # Don't close the session here, it's managed by the test_db fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

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