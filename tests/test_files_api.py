import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, UTC
import io
import uuid

from app.core.database_config import Base, get_db, engine
from app.models.file import UploadedFile
from app.models.parsed_content import ParsedContent
from app.main import app

@pytest.fixture
def client(test_db):
    """Create a test client with the test database"""
    def override_get_db():
        yield test_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

def test_list_files_empty(client: TestClient, db: Session):
    """Test listing files when database is empty"""
    response = client.get("/api/files")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["files"]) == 0

def test_list_files_with_data(client: TestClient, db: Session):
    """Test listing files with data in the database"""
    # Create test files
    file1 = UploadedFile(
        file_id=str(uuid.uuid4()),
        filename="test1.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_content=b"test content 1",
        upload_time=datetime.now(UTC),
        title="Test File 1",
        description="First test file"
    )
    
    file2 = UploadedFile(
        file_id=str(uuid.uuid4()),
        filename="test2.txt",
        content_type="text/plain",
        file_size=512,
        file_content=b"test content 2",
        upload_time=datetime.now(UTC),
        title="Test File 2",
        description="Second test file"
    )
    
    # Add parsed content to first file
    parsed_content = ParsedContent(
        id=str(uuid.uuid4()),
        content_id=str(uuid.uuid4()),
        file_id=file1.file_id,
        content_type="text/plain",
        parsed_text="Parsed content",
        parse_time=datetime.now(UTC)
    )
    
    db.add_all([file1, file2, parsed_content])
    db.commit()
    
    # Test the endpoint
    response = client.get("/api/files")
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert data["total"] == 2
    assert len(data["files"]) == 2
    
    # Check first file (with parsed content)
    file1_data = next(f for f in data["files"] if f["file_id"] == file1.file_id)
    assert file1_data["filename"] == "test1.pdf"
    assert file1_data["content_type"] == "application/pdf"
    assert file1_data["file_size"] == 1024
    assert file1_data["title"] == "Test File 1"
    assert file1_data["description"] == "First test file"
    assert file1_data["is_parsed"] is True
    assert file1_data["parsed_contents_count"] == 1
    
    # Check second file (without parsed content)
    file2_data = next(f for f in data["files"] if f["file_id"] == file2.file_id)
    assert file2_data["filename"] == "test2.txt"
    assert file2_data["content_type"] == "text/plain"
    assert file2_data["file_size"] == 512
    assert file2_data["title"] == "Test File 2"
    assert file2_data["description"] == "Second test file"
    assert file2_data["is_parsed"] is False
    assert file2_data["parsed_contents_count"] == 0

def test_list_files_database_error(client: TestClient, db: Session):
    """Test handling of database errors"""
    # Force a database error by closing the session
    db.close()
    
    response = client.get("/api/files")
    assert response.status_code == 500
    assert "Error listing files" in response.json()["detail"] 