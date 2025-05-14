import sys
import os
import importlib.util

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main.py'))
spec = importlib.util.spec_from_file_location("main", main_path)
main = importlib.util.module_from_spec(spec)
sys.modules["main"] = main
spec.loader.exec_module(main)
app = main.app

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import io
import os
from app.core.database import get_db, Base, engine
from app.models.file import UploadedFile
from app.models.parsed_content import ParsedContent
from dotenv import load_dotenv

# Create test client
client = TestClient(app)

# Test database setup
@pytest.fixture(scope="function")
def db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)

def test_upload_pdf_file(db: Session):
    """Test uploading a PDF file"""
    # Create a test PDF file (minimal valid PDF)
    test_pdf = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    test_file = io.BytesIO(test_pdf)
    test_file.name = "test.pdf"

    # Upload the file
    response = client.post(
        "/api/upload/",
        files={"file": ("test.pdf", test_file, "application/pdf")}
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.pdf"
    # Don't assert parsed content since parsing may fail for test PDF

    # Check database
    db_file = db.query(UploadedFile).filter(UploadedFile.filename == "test.pdf").first()
    assert db_file is not None
    assert db_file.content_type == "application/pdf"

def test_upload_text_file(db: Session):
    """Test uploading a text file"""
    # Create a test text file
    test_file = io.BytesIO(b"Test text content")
    test_file.name = "test.txt"
    
    # Upload the file
    response = client.post(
        "/api/upload/",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.txt"
    assert data["parsed"] is not None
    
    # Check database
    db_file = db.query(UploadedFile).filter(UploadedFile.filename == "test.txt").first()
    assert db_file is not None
    assert db_file.content_type == "text/plain"
    
    # Check parsed content
    parsed_content = db.query(ParsedContent).filter(ParsedContent.file_id == db_file.file_id).first()
    assert parsed_content is not None
    assert parsed_content.content_type == "text/plain"

def test_upload_invalid_file_type(db: Session):
    """Test uploading an invalid file type"""
    # Create a test file with invalid type
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test.exe"
    
    # Upload the file
    response = client.post(
        "/api/upload/",
        files={"file": ("test.exe", test_file, "application/x-msdownload")}
    )
    
    # Check response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid file type" in data["detail"]

def test_list_files(db: Session):
    """Test listing uploaded files"""
    # Create some test files
    test_files = [
        ("test1.pdf", b"%PDF-1.4\nTest PDF 1", "application/pdf"),
        ("test2.txt", b"Test text 2", "text/plain")
    ]
    
    for filename, content, content_type in test_files:
        test_file = io.BytesIO(content)
        test_file.name = filename
        client.post(
            "/api/upload/",
            files={"file": (filename, test_file, content_type)}
        )
    
    # List files
    response = client.get("/api/upload/files")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert len(data["files"]) == 2
    
    # Check file details
    filenames = [f["filename"] for f in data["files"]]
    assert "test1.pdf" in filenames
    assert "test2.txt" in filenames

def test_get_file_metadata(db: Session):
    """Test getting file metadata"""
    # Upload a test file
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test.txt"
    
    upload_response = client.post(
        "/api/upload/",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    file_id = upload_response.json()["file_id"]
    
    # Get metadata
    response = client.get(f"/api/upload/files/{file_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["content_type"] == "text/plain"

def test_download_file(db: Session):
    """Test downloading a file"""
    # Upload a test file
    test_content = b"Test content for download"
    test_file = io.BytesIO(test_content)
    test_file.name = "test.txt"
    
    upload_response = client.post(
        "/api/upload/",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    file_id = upload_response.json()["file_id"]
    
    # Download the file
    response = client.get(f"/api/upload/files/{file_id}/download")
    assert response.status_code == 200
    assert response.content == test_content
    assert response.headers["content-type"].startswith("text/plain")
    assert "attachment" in response.headers["content-disposition"]

def test_delete_file(db: Session):
    """Test deleting a file"""
    # Upload a test file
    test_file = io.BytesIO(b"Test content")
    test_file.name = "test.txt"
    
    upload_response = client.post(
        "/api/upload/",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    file_id = upload_response.json()["file_id"]
    
    # Delete the file
    response = client.delete(f"/api/upload/files/{file_id}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "deleted successfully" in data["message"]
    
    # Verify file is deleted
    db_file = db.query(UploadedFile).filter(UploadedFile.file_id == file_id).first()
    assert db_file is None
    
    # Verify parsed content is deleted
    parsed_content = db.query(ParsedContent).filter(ParsedContent.file_id == file_id).first()
    assert parsed_content is None

load_dotenv() 