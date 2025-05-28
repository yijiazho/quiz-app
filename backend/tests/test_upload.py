import sys
import os
import importlib.util
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import io
from datetime import datetime, UTC
from typing import Optional
import uuid

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.core.database_config import Base, engine, get_db
from app.models.file import UploadedFile
from app.models.parsed_content import ParsedContent
from app.main import app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture
def client(db: Session):
    """Create a test client with the test database"""
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    # Drop and recreate all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()

def test_upload_pdf_file(client: TestClient, db: Session):
    """Test uploading a PDF file"""
    # Create a test PDF file
    test_file = io.BytesIO(b"%PDF-1.4\n%Test PDF content")
    test_file.name = "test.pdf"
    
    # Upload the file
    response = client.post(
        "/api/upload",
        files={"file": ("test.pdf", test_file, "application/pdf")}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.pdf"
    
    # Verify file was saved in database
    file = db.query(UploadedFile).filter(UploadedFile.filename == "test.pdf").first()
    assert file is not None
    assert file.content_type == "application/pdf"

def test_upload_text_file(client: TestClient, db: Session):
    """Test uploading a text file"""
    # Create a test text file
    test_file = io.BytesIO(b"Test text content")
    test_file.name = "test.txt"
    
    # Upload the file
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.txt"
    
    # Verify file was saved in database
    file = db.query(UploadedFile).filter(UploadedFile.filename == "test.txt").first()
    assert file is not None
    assert file.content_type == "text/plain"

def test_upload_invalid_file_type(client: TestClient, db: Session):
    """Test uploading an invalid file type"""
    # Create a test file with invalid type
    test_file = io.BytesIO(b"Invalid file content")
    test_file.name = "test.invalid"
    
    # Try to upload the file
    response = client.post(
        "/api/upload",
        files={"file": ("test.invalid", test_file, "application/invalid")}
    )
    
    # Check response
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_list_files(client: TestClient, db: Session):
    """Test listing uploaded files"""
    # Upload two test files
    for i in range(2):
        test_file = io.BytesIO(f"Test content {i}".encode())
        test_file.name = f"test{i}.txt"
        client.post(
            "/api/upload",
            files={"file": (f"test{i}.txt", test_file, "text/plain")}
        )
    
    # List files
    response = client.get("/api/upload")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_file_metadata(client: TestClient, db: Session):
    """Test getting file metadata"""
    # Upload a test file
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test.txt"
    upload_response = client.post(
        "/api/upload",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    file_id = upload_response.json()["file_id"]
    
    # Get metadata
    response = client.get(f"/api/upload/{file_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["content_type"] == "text/plain"

def test_download_file(client: TestClient, db: Session):
    """Test downloading a file"""
    # Upload a test file
    test_content = b"Test content"
    test_file = io.BytesIO(test_content)
    test_file.name = "test.txt"
    upload_response = client.post(
        "/api/upload",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    file_id = upload_response.json()["file_id"]
    
    # Download file
    response = client.get(f"/api/upload/{file_id}/download")
    assert response.status_code == 200
    assert response.content == test_content

def test_delete_file(client: TestClient, db: Session):
    """Test deleting a file"""
    # Upload a test file
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test.txt"
    upload_response = client.post(
        "/api/upload",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    file_id = upload_response.json()["file_id"]
    
    # Delete file
    response = client.delete(f"/api/upload/{file_id}")
    assert response.status_code == 200
    
    # Verify file was deleted
    file = db.query(UploadedFile).filter(UploadedFile.file_id == file_id).first()
    assert file is None

def test_upload_empty_file(client: TestClient, db: Session):
    """Test uploading an empty file"""
    # Create an empty file
    test_file = io.BytesIO(b"")
    test_file.name = "empty.txt"
    
    # Upload the file
    response = client.post(
        "/api/upload",
        files={"file": ("empty.txt", test_file, "text/plain")}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "empty.txt"
    
    # Verify file was saved in database
    file = db.query(UploadedFile).filter(UploadedFile.filename == "empty.txt").first()
    assert file is not None
    assert file.file_size == 0

def test_upload_large_file(client: TestClient, db: Session):
    """Test uploading a large file"""
    # Create a large file (1MB)
    large_content = b"0" * (1024 * 1024)  # 1MB of zeros
    test_file = io.BytesIO(large_content)
    test_file.name = "large.txt"
    
    # Upload the file
    response = client.post(
        "/api/upload",
        files={"file": ("large.txt", test_file, "text/plain")}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "large.txt"
    
    # Verify file was saved in database
    file = db.query(UploadedFile).filter(UploadedFile.filename == "large.txt").first()
    assert file is not None
    assert file.file_size == len(large_content)

def test_upload_with_metadata(client: TestClient, db: Session):
    """Test uploading a file with metadata"""
    # Create a test file
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test.txt"
    
    # Upload the file with metadata
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", test_file, "text/plain")},
        data={
            "title": "Test Document",
            "description": "This is a test document"
        }
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.txt"
    assert data["title"] == "Test Document"
    assert data["description"] == "This is a test document"
    
    # Close and reopen the session to see the latest committed data
    db.close()
    new_session = Session(bind=engine)
    file = new_session.query(UploadedFile).filter(UploadedFile.filename == "test.txt").first()
    assert file is not None
    assert file.title == "Test Document"
    assert file.description == "This is a test document"
    new_session.close()

def test_update_file_metadata(client: TestClient, db: Session):
    """Test updating file metadata"""
    # Upload a test file
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test.txt"
    upload_response = client.post(
        "/api/upload",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    file_id = upload_response.json()["file_id"]
    
    # Update metadata
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description"
    }
    response = client.patch(f"/api/upload/{file_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    
    # Verify in database
    file = db.query(UploadedFile).filter(UploadedFile.file_id == file_id).first()
    assert file.title == "Updated Title"
    assert file.description == "Updated Description"

def test_list_files_with_pagination(client: TestClient, db: Session):
    """Test listing files with pagination"""
    # Upload multiple test files
    for i in range(5):
        test_file = io.BytesIO(f"Test content {i}".encode())
        test_file.name = f"test{i}.txt"
        client.post(
            "/api/upload",
            files={"file": (f"test{i}.txt", test_file, "text/plain")}
        )

    # Test first page (limit=2)
    response = client.get("/api/upload/files?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["files"]) == 2
    assert data["total"] == 5

    # Test second page (skip=2, limit=2)
    response = client.get("/api/upload/files?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["files"]) == 2
    assert data["total"] == 5

    # Test last page (skip=4, limit=2)
    response = client.get("/api/upload/files?skip=4&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["files"]) == 1
    assert data["total"] == 5

def test_get_nonexistent_file(client: TestClient, db: Session):
    """Test getting a nonexistent file"""
    response = client.get("/api/files/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_delete_nonexistent_file(client: TestClient, db: Session):
    """Test deleting a nonexistent file"""
    response = client.delete("/api/files/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_upload_file_with_invalid_metadata(client: TestClient, db: Session):
    """Test uploading a file with invalid metadata"""
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test.txt"
    
    # Try to upload with invalid metadata (title too long)
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", test_file, "text/plain")},
        data={"title": "x" * 1001}  # Assuming 1000 is max length
    )
    assert response.status_code == 422  # Validation error
    assert "title" in response.json()["detail"].lower()

def test_upload_file_with_special_characters(client: TestClient, db: Session):
    """Test uploading a file with special characters in filename"""
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test!@#$%^&*().txt"
    
    response = client.post(
        "/api/upload",
        files={"file": (test_file.name, test_file, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == test_file.name

def test_upload_file_with_unicode_filename(client: TestClient, db: Session):
    """Test uploading a file with Unicode characters in filename"""
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test_测试_ファイル.txt"
    
    response = client.post(
        "/api/upload",
        files={"file": (test_file.name, test_file, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == test_file.name

def test_upload_file_without_content_type(client: TestClient, db: Session):
    """Test uploading a file without content type"""
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test.txt"
    
    response = client.post(
        "/api/upload",
        files={"file": (test_file.name, test_file, "")}  # Empty content type
    )
    assert response.status_code == 400
    assert "invalid file type" in response.json()["detail"].lower()

def test_upload_file_with_invalid_content_type(client: TestClient, db: Session):
    """Test uploading a file with invalid content type"""
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test.txt"
    
    response = client.post(
        "/api/upload",
        files={"file": (test_file.name, test_file, "invalid/type")}
    )
    assert response.status_code == 400
    assert "invalid file type" in response.json()["detail"].lower() 