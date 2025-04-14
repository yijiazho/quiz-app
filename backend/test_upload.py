import requests
import os

# URL of the API endpoint
url = "http://localhost:8000/api/upload/"

# File to upload
file_path = "test_upload.txt"

# Get the content type based on file extension
content_type = "text/plain"  # Default for .txt files

# Prepare the file for upload with content type
files = {
    'file': (os.path.basename(file_path), open(file_path, 'rb'), content_type)
}

# Additional form data
data = {
    'title': 'Test Upload',
    'description': 'Test file upload to database'
}

# Make the POST request
response = requests.post(url, files=files, data=data)

# Print the response
print(f"Status Code: {response.status_code}")
print("Response Content:")
print(response.json())

# If the upload was successful, test the metadata endpoint
if response.status_code == 201:
    file_id = response.json().get('file_id')
    print(f"\nFile ID: {file_id}")
    
    # Test file metadata endpoint
    metadata_url = f"http://localhost:8000/api/upload/files/{file_id}"
    metadata_response = requests.get(metadata_url)
    print("\nFile Metadata Response:")
    print(metadata_response.json())

# Test file listing endpoint
list_url = "http://localhost:8000/api/upload/files"
list_response = requests.get(list_url)
print("\nList Files Response:")
print(list_response.json())

# Close the file
files['file'][1].close() 