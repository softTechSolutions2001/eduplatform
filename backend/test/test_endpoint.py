#!/usr/bin/env python
import requests
import json

def test_featured_endpoint():
    """Test the featured endpoint that was causing 500 errors"""
    try:
        url = "http://localhost:8000/api/featured/"
        print(f"Testing: {url}")

        response = requests.get(url, headers={"Accept": "application/json"})

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("SUCCESS: Endpoint is working!")
            try:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
        else:
            print(f"ERROR: Status {response.status_code}")
            print(f"Response Text: {response.text}")

        return response.status_code == 200

    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Is Django running on localhost:8000?")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False

if __name__ == '__main__':
    print("=== TESTING FEATURED ENDPOINT ===")
    success = test_featured_endpoint()
    print(f"\n=== RESULT: {'PASS' if success else 'FAIL'} ===")
