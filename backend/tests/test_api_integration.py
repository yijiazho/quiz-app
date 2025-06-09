import requests
import json
import logging
from datetime import datetime, UTC
import uuid
from app.models.file import UploadedFile
from app.core.database_config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_endpoint():
    """Test the files API endpoint and response handling."""
    logger.info("=== Starting API Integration Test ===")
    
    # Test 1: Check API URL and response
    api_url = "http://localhost:8000/api/files/"
    logger.info(f"Testing API endpoint: {api_url}")
    
    try:
        response = requests.get(api_url)
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            logger.error(f"API request failed with status {response.status_code}")
            return False
            
        data = response.json()
        logger.info(f"Response data: {json.dumps(data, indent=2)}")
        
        # Verify response structure
        if "total" not in data or "files" not in data:
            logger.error("Response missing required fields")
            return False
            
        # Test 2: Add a test file and verify it appears in the response
        db = config.SessionLocal()
        try:
            # Create test file
            test_file = UploadedFile(
                file_id=str(uuid.uuid4()),
                filename="test_integration.pdf",
                content_type="application/pdf",
                file_size=1024,
                file_content=b"test content",
                upload_time=datetime.now(UTC),
                title="Test Integration File",
                description="File created for API integration test"
            )
            
            db.add(test_file)
            db.commit()
            logger.info("Added test file to database")
            
            # Verify file appears in API response
            response = requests.get(api_url)
            data = response.json()
            
            test_file_data = next(
                (f for f in data["files"] if f["file_id"] == test_file.file_id),
                None
            )
            
            if not test_file_data:
                logger.error("Test file not found in API response")
                return False
                
            logger.info("Test file found in API response")
            logger.info("=== API Integration Test Completed Successfully ===")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api_endpoint()
    exit(0 if success else 1) 