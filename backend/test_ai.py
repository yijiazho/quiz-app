import os
import requests
import json
import time
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def wait_for_server(url: str, max_retries: int = 5, delay: int = 2) -> bool:
    """Wait for the server to be ready."""
    for i in range(max_retries):
        try:
            print(f"Attempting to connect to {url}...")
            response = requests.get(url)
            if response.status_code == 200:
                print("Server is ready!")
                return True
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            if i < max_retries - 1:
                print(f"Server not ready, retrying in {delay} seconds...")
                time.sleep(delay)
            continue
    return False

def test_generate_quiz():
    """Test the quiz generation endpoint."""
    print("Testing AI endpoints...")
    
    # Use localhost for client connection
    host = "127.0.0.1"
    port = "8001"
    server_url = f"http://{host}:{port}"
    
    print(f"Server URL: {server_url}")
    
    # Check if server is running
    if not wait_for_server(f"{server_url}/health"):
        print("Error: Server is not running. Please start the server first.")
        sys.exit(1)
    
    # Test data
    payload = {
        "content": "Python is a high-level programming language known for its simplicity and readability.",
        "num_questions": 2,
        "question_type": "multiple_choice",
        "difficulty": "medium"
    }
    
    try:
        # Make request
        url = f"{server_url}/api/ai/generate-quiz"
        print(f"Making request to: {url}")
        response = requests.post(url, json=payload, timeout=30)
        
        # Print response
        print("\nResponse:")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_generate_quiz() 