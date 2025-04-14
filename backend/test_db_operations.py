import requests
import os
import time
import sys
from datetime import datetime
import random
import string

"""
Comprehensive test for database operations with uploaded files:
1. Upload a file to the database
2. List all files in the database
3. Get metadata for a specific file
4. Download a file from the database
5. Delete a file from the database
"""

# Base URL for the API
BASE_URL = "http://localhost:8000/api/upload"

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_colored(text, color):
    """Print colored text in the terminal"""
    print(f"{color}{text}{RESET}")

def generate_test_file(filename, size_kb=10):
    """Generate a test file with random content of specified size"""
    # Create random content
    random_content = ''.join(random.choices(string.ascii_letters + string.digits, k=size_kb * 1024))
    
    # Write to file
    with open(filename, 'w') as f:
        f.write(random_content)
    
    return filename

def test_upload_file(filepath, title=None, description=None):
    """Test uploading a file to the database"""
    print_colored(f"\nTesting file upload: {filepath}", BLUE)
    
    # Determine content type based on file extension
    content_type = "application/octet-stream"  # Default content type
    if filepath.endswith(".txt"):
        content_type = "text/plain"
    elif filepath.endswith(".json"):
        content_type = "application/json"
    elif filepath.endswith(".pdf"):
        content_type = "application/pdf"
    elif filepath.endswith(".docx") or filepath.endswith(".doc"):
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    # Open the file
    file_obj = open(filepath, 'rb')
    
    # Prepare the file and data
    files = {
        'file': (os.path.basename(filepath), file_obj, content_type)
    }
    data = {}
    if title:
        data['title'] = title
    if description:
        data['description'] = description
        
    try:
        # Send the request
        response = requests.post(f"{BASE_URL}/", files=files, data=data)
        
        # Check response
        if response.status_code == 201:
            print_colored("✓ File upload successful", GREEN)
            print(f"Response: {response.json()}")
            return response.json()
        else:
            print_colored(f"✗ File upload failed with status code: {response.status_code}", RED)
            print(f"Error: {response.text}")
            return None
    finally:
        # Close the file
        file_obj.close()

def test_list_files():
    """Test listing all files in the database"""
    print_colored("\nTesting file listing", BLUE)
    
    # Send the request
    response = requests.get(f"{BASE_URL}/files")
    
    # Check response
    if response.status_code == 200:
        files = response.json()
        print_colored(f"✓ Retrieved {files['total']} files", GREEN)
        for i, file in enumerate(files['files']):
            print(f"{i+1}. {file['filename']} (ID: {file['file_id']})")
        return files
    else:
        print_colored(f"✗ File listing failed with status code: {response.status_code}", RED)
        print(f"Error: {response.text}")
        return None

def test_get_file_metadata(file_id):
    """Test getting metadata for a specific file"""
    print_colored(f"\nTesting metadata retrieval for file ID: {file_id}", BLUE)
    
    # Send the request
    response = requests.get(f"{BASE_URL}/files/{file_id}")
    
    # Check response
    if response.status_code == 200:
        metadata = response.json()
        print_colored("✓ File metadata retrieved successfully", GREEN)
        print(f"Filename: {metadata['filename']}")
        print(f"Size: {metadata['file_size']} bytes")
        print(f"Content Type: {metadata['content_type']}")
        print(f"Upload Time: {metadata['upload_time']}")
        return metadata
    else:
        print_colored(f"✗ Metadata retrieval failed with status code: {response.status_code}", RED)
        print(f"Error: {response.text}")
        return None

def test_download_file(file_id, filename):
    """Test downloading a file from the database"""
    print_colored(f"\nTesting file download for file ID: {file_id}", BLUE)
    
    # Send the request
    response = requests.get(f"{BASE_URL}/files/{file_id}/download")
    
    # Check response
    if response.status_code == 200:
        # Save the downloaded file
        download_path = f"downloaded_{filename}"
        with open(download_path, 'wb') as f:
            f.write(response.content)
            
        print_colored(f"✓ File downloaded successfully to {download_path}", GREEN)
        print(f"Content size: {len(response.content)} bytes")
        
        # Verify the file exists
        if os.path.exists(download_path):
            print_colored(f"✓ Downloaded file exists on disk", GREEN)
            return download_path
        else:
            print_colored("✗ Downloaded file not found on disk", RED)
            return None
    else:
        print_colored(f"✗ File download failed with status code: {response.status_code}", RED)
        print(f"Error: {response.text}")
        return None

def test_delete_file(file_id):
    """Test deleting a file from the database"""
    print_colored(f"\nTesting file deletion for file ID: {file_id}", BLUE)
    
    # Send the request
    response = requests.delete(f"{BASE_URL}/files/{file_id}")
    
    # Check response
    if response.status_code == 200:
        print_colored("✓ File deleted successfully", GREEN)
        print(f"Response: {response.json()}")
        return True
    else:
        print_colored(f"✗ File deletion failed with status code: {response.status_code}", RED)
        print(f"Error: {response.text}")
        return False
    
def verify_file_deleted(file_id):
    """Verify that a file has been deleted by trying to get its metadata"""
    print_colored(f"\nVerifying file deletion for file ID: {file_id}", BLUE)
    
    # Send the request
    response = requests.get(f"{BASE_URL}/files/{file_id}")
    
    # Check response
    if response.status_code == 404:
        print_colored("✓ File confirmed deleted (404 Not Found)", GREEN)
        return True
    else:
        print_colored(f"✗ File might still exist with status code: {response.status_code}", RED)
        print(f"Response: {response.text}")
        return False

def run_all_tests():
    """Run all database operation tests in sequence"""
    print_colored("STARTING DATABASE OPERATIONS TESTS", BLUE)
    
    # Generate test files of different types
    test_files = [
        {"path": "test_text.txt", "type": "text/plain", "title": "Test Text File", "description": "A sample text file for testing"},
        {"path": "test_json.json", "type": "application/json", "title": "Test JSON File", "description": "A sample JSON file for testing"}
    ]
    
    # Generate content for test files
    for test_file in test_files:
        with open(test_file["path"], "w") as f:
            if test_file["path"].endswith(".txt"):
                f.write("This is a test file for database operations.\nIt contains multiple lines of text.\nTesting read and write operations.")
            elif test_file["path"].endswith(".json"):
                f.write('{"test": true, "purpose": "database testing", "values": [1, 2, 3, 4, 5]}')
    
    # Track file IDs for each uploaded file
    file_ids = []
    
    # Step 1: Upload test files
    for test_file in test_files:
        result = test_upload_file(
            test_file["path"], 
            title=test_file["title"], 
            description=test_file["description"]
        )
        if result:
            file_ids.append(result["file_id"])
    
    if not file_ids:
        print_colored("No files were uploaded successfully. Stopping tests.", RED)
        return
    
    # Step 2: List all files
    files_list = test_list_files()
    
    # Step 3: Get metadata for each file
    for file_id in file_ids:
        metadata = test_get_file_metadata(file_id)
    
    # Step 4: Download each file
    downloaded_files = []
    for i, file_id in enumerate(file_ids):
        filename = test_files[i]["path"]
        download_path = test_download_file(file_id, filename)
        if download_path:
            downloaded_files.append(download_path)
    
    # Step 5: Delete the first file
    if file_ids:
        deleted = test_delete_file(file_ids[0])
        if deleted:
            verify_file_deleted(file_ids[0])
    
    # Final listing to verify changes
    print_colored("\nFinal file listing after operations:", BLUE)
    test_list_files()
    
    # Clean up - delete remaining files from database
    print_colored("\nCleaning up test files from database:", BLUE)
    for file_id in file_ids[1:]:
        test_delete_file(file_id)
    
    # Clean up local files
    print_colored("\nCleaning up local test files:", BLUE)
    for test_file in test_files:
        if os.path.exists(test_file["path"]):
            os.remove(test_file["path"])
            print(f"Removed {test_file['path']}")
    
    for downloaded_file in downloaded_files:
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)
            print(f"Removed {downloaded_file}")
    
    print_colored("\nALL TESTS COMPLETED", BLUE)

if __name__ == "__main__":
    # Check if the server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print_colored("The API server returned an unexpected status code. Make sure it's running correctly.", RED)
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print_colored("Could not connect to the API server. Make sure it's running at http://localhost:8000", RED)
        sys.exit(1)
        
    run_all_tests() 