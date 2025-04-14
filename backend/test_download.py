import requests
import json
import os

# Get the file ID from the previously uploaded file
list_url = "http://localhost:8000/api/upload/files"
list_response = requests.get(list_url)
list_data = list_response.json()

if not list_data['files']:
    print("No files found in the database.")
    exit(1)

# Get the first file ID
file_id = list_data['files'][0]['file_id']
filename = list_data['files'][0]['filename']
content_type = list_data['files'][0]['content_type']

print(f"Downloading file: {filename} (ID: {file_id}, Type: {content_type})")

# Construct the download URL
download_url = f"http://localhost:8000/api/upload/files/{file_id}/download"

# Make the GET request to download the file
response = requests.get(download_url)

# Check if the download was successful
if response.status_code == 200:
    # Save the downloaded file with a different name
    downloaded_filename = f"downloaded_{filename}"
    with open(downloaded_filename, 'wb') as f:
        f.write(response.content)
    
    print(f"File downloaded successfully as: {downloaded_filename}")
    
    # Compare file sizes
    original_size = list_data['files'][0]['file_size']
    downloaded_size = os.path.getsize(downloaded_filename)
    
    print(f"Original file size: {original_size} bytes")
    print(f"Downloaded file size: {downloaded_size} bytes")
    print(f"Files match: {original_size == downloaded_size}")
    
    # Print the content of the downloaded file (if it's a text file)
    if content_type == 'text/plain':
        with open(downloaded_filename, 'r') as f:
            content = f.read()
        print("\nFile content:")
        print(content)
else:
    print(f"Error downloading file: {response.status_code}")
    print(response.text) 