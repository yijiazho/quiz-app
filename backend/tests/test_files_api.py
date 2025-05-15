import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from app.main import app
from app.models.parsed_content import ParsedContent
from app.core.database import get_db, engine, Base
from unittest.mock import patch, MagicMock
from app.models.file import UploadedFile
from sqlalchemy import text

@pytest.fixture(scope="session")
def test_db():
    """Create a test database session."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        # Drop all tables
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
    return TestClient(app)

# Test data
TEST_PARSED_CONTENT = {
    "content_id": "test-content-1",
    "file_id": "test-file-1",
    "content_type": "application/pdf",
    "parsed_text": "This is a test document content",
    "content_metadata": {
        "file_size": 1024,
        "encoding": "utf-8"
    },
    "parse_time": datetime.now(UTC),
    "last_updated": datetime.now(UTC)
}

TEST_UPLOADED_FILE = {
    "filename": "test.pdf",
    "content_type": "application/pdf",
    "file_size": 1024,
    "file_content": b"test content",
    "upload_time": datetime.now(UTC)
}

@pytest.fixture
def setup_test_data(test_db):
    """Set up test data in the database."""
    # Clear the tables
    test_db.execute(text("DELETE FROM parsed_contents"))
    test_db.execute(text("DELETE FROM uploaded_files"))
    test_db.commit()
    
    # Create test uploaded file
    test_file = UploadedFile(
        filename=TEST_UPLOADED_FILE["filename"],
        content_type=TEST_UPLOADED_FILE["content_type"],
        file_size=TEST_UPLOADED_FILE["file_size"],
        file_content=TEST_UPLOADED_FILE["file_content"],
        upload_time=TEST_UPLOADED_FILE["upload_time"]
    )
    test_db.add(test_file)
    test_db.commit()
    test_db.refresh(test_file)
    
    # Create test parsed content
    test_content = ParsedContent(
        content_id=TEST_PARSED_CONTENT["content_id"],
        file_id=test_file.file_id,
        content_type=TEST_PARSED_CONTENT["content_type"],
        parsed_text=TEST_PARSED_CONTENT["parsed_text"],
        content_metadata=TEST_PARSED_CONTENT["content_metadata"],
        parse_time=TEST_PARSED_CONTENT["parse_time"],
        last_updated=TEST_PARSED_CONTENT["last_updated"]
    )
    test_db.add(test_content)
    test_db.commit()
    test_db.refresh(test_content)
    
    return test_content

def test_list_files_empty(client, test_db):
    """Test listing files when database is empty."""
    # Clear the tables
    test_db.execute(text("DELETE FROM parsed_contents"))
    test_db.execute(text("DELETE FROM uploaded_files"))
    test_db.commit()
    
    response = client.get("/api/files")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["files"]) == 0

def test_list_files_with_data(client, setup_test_data):
    """Test listing files with data in the database."""
    response = client.get("/api/files")
    assert response.status_code == 200
    data = response.json()
    
    assert "total" in data
    assert "files" in data
    assert data["total"] > 0
    assert len(data["files"]) > 0
    
    first_file = data["files"][0]
    assert first_file["id"] == TEST_PARSED_CONTENT["content_id"]
    assert first_file["file_id"] == setup_test_data.file_id
    assert first_file["type"] == TEST_PARSED_CONTENT["content_type"]
    assert first_file["text"] == TEST_PARSED_CONTENT["parsed_text"]
    assert first_file["metadata"] == TEST_PARSED_CONTENT["content_metadata"]
    assert "parsed_at" in first_file
    assert "updated_at" in first_file
    assert first_file["filename"] == TEST_UPLOADED_FILE["filename"]

def test_list_files_database_error(client):
    """Test handling of database errors."""
    from app.core.database import get_db
    # Patch the db.query method to raise an exception
    def override_get_db():
        db = next(get_db())
        original_query = db.query
        def raise_query(*args, **kwargs):
            raise Exception("Database error")
        db.query = raise_query
        try:
            yield db
        finally:
            db.query = original_query
    app = client.app
    app.dependency_overrides[get_db] = override_get_db
    response = client.get("/api/files")
    assert response.status_code == 500
    assert response.json()["detail"].startswith("Error listing files:")
    app.dependency_overrides = {}

def test_upload_file(client, test_db):
    """Test file upload endpoint."""
    with patch('app.services.file_service.FileService.save_file_to_db') as mock_save:
        mock_save.return_value = UploadedFile(
            file_id="test-file-1",
            filename="test.pdf",
            content_type="application/pdf",
            file_size=1024,
            file_content=b"test content",
            upload_time=datetime.now(UTC)
        )

        response = client.post(
            "/api/upload",
            files={"file": ("test.pdf", b"test content", "application/pdf")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] == "test-file-1"
        assert data["filename"] == "test.pdf"
        assert "parsed" in data

def test_get_file(client, setup_test_data):
    """Test get file endpoint."""
    test_content = setup_test_data
    
    response = client.get(f"/api/files/{test_content.file_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_id"] == test_content.file_id
    assert data["filename"] == TEST_UPLOADED_FILE["filename"]
    assert data["content_type"] == TEST_UPLOADED_FILE["content_type"]
    assert data["file_size"] == TEST_UPLOADED_FILE["file_size"]

def test_get_file_not_found(client):
    """Test get file endpoint with non-existent file."""
    response = client.get("/api/files/non-existent-id")
    assert response.status_code == 404

def test_get_file_content(client, setup_test_data):
    """Test get file content endpoint."""
    test_content = setup_test_data
    
    response = client.get(f"/api/files/{test_content.file_id}/content")
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_id"] == test_content.file_id
    assert data["content_type"] == test_content.content_type
    assert data["parsed_text"] == test_content.parsed_text
    assert data["content_metadata"] == test_content.content_metadata

def test_get_file_content_not_found(client):
    """Test get file content endpoint with non-existent file."""
    response = client.get("/api/files/non-existent-id/content")
    assert response.status_code == 404

def test_delete_file(client, setup_test_data):
    """Test delete file endpoint."""
    test_content = setup_test_data
    
    response = client.delete(f"/api/files/{test_content.file_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "File deleted successfully"
    
    # Verify file is deleted
    response = client.get(f"/api/files/{test_content.file_id}")
    assert response.status_code == 404

def test_delete_file_not_found(client):
    """Test delete file endpoint with non-existent file."""
    response = client.delete("/api/files/non-existent-id")
    assert response.status_code == 404 