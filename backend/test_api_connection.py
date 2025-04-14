import requests
import sys
import time

def test_api_connection(retries=3, delay=2):
    """
    Simple test to check if the backend API is accessible.
    Retries a few times to allow the server to start up.
    """
    url = "http://127.0.0.1:8000"
    
    for attempt in range(retries):
        try:
            print(f"Testing connection to backend API (attempt {attempt+1}/{retries})...")
            
            # First try the root endpoint
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ Backend API is accessible at {url}")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"⚠️ Backend API returned non-200 status code: {response.status_code}")
                
                # Try the health check endpoint
                health_response = requests.get(f"{url}/api/upload")
                if health_response.status_code in [200, 404, 405]:  # 404/405 is fine as long as the server responds
                    print(f"✅ Backend API is accessible (upload endpoint test)")
                    return True
                    
        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to {url} (attempt {attempt+1})")
            if attempt < retries - 1:
                print(f"Waiting {delay} seconds before retrying...")
                time.sleep(delay)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if attempt < retries - 1:
                print(f"Waiting {delay} seconds before retrying...")
                time.sleep(delay)
    
    print("❌ Failed to connect to backend API. Is the server running?")
    return False

if __name__ == "__main__":
    success = test_api_connection()
    if not success:
        sys.exit(1)  # Exit with error code 