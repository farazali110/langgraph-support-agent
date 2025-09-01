import requests
import json
import sys
import time

def test_api():
    """Test the Support Agent API with a sample ticket."""
    print("="*50)
    print("SUPPORT AGENT API TEST")
    print("="*50)
    print("Testing Support Agent API...")

    url = "http://localhost:8000/resolve_ticket"
    payload = {
        "ticket_id": "12345",
        "subject": "Billing Question",
        "description": "How much does the premium plan cost per month?"
    }

    try:
        print(f"Sending request to {url}...")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success! Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Connection error: The server is not running or cannot be reached.")
        print("Please make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"Request failed: {str(e)}")
    
    print("="*50)

if __name__ == "__main__":
    test_api()
