import requests
import os

def test_upload_endpoint():
    """
    Test the upload endpoint with a sample file.
    """
    # Create a sample test file
    test_file_path = "test_document.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test document for the QuizForge API.")
    
    try:
        # Test file upload
        url = "http://localhost:8000/api/upload"
        files = {"file": ("test_document.txt", open(test_file_path, "rb"), "text/plain")}
        
        print(f"Making POST request to {url}...")
        response = requests.post(url, files=files)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Test passed!")
        else:
            print("❌ Test failed!")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        # Clean up the test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_upload_endpoint() 