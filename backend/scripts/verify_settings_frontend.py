import sys
import os
import requests

# Assuming the backend is running at http://localhost:8000
BASE_URL = "http://localhost:8000/api"

def verify_settings_api():
    print("--- Verifying Settings API ---")
    
    # 1. Test GET /settings/ (List all)
    try:
        response = requests.get(f"{BASE_URL}/settings/")
        if response.status_code == 200:
            print(f"SUCCESS: GET /settings/ returned {len(response.json())} items.")
        else:
            print(f"FAIL: GET /settings/ failed with {response.status_code}: {response.text}")
            return
    except Exception as e:
        print(f"FAIL: Connection error: {e}")
        return

    # 2. Test PUT /settings/{key} (Update/Create)
    test_key = "TEST_CONFIG_KEY"
    test_val = "TestValue123"
    
    try:
        data = {"valor": test_val, "descripcion": "Test Description"}
        response = requests.put(f"{BASE_URL}/settings/{test_key}", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("clave") == test_key and result.get("valor") == test_val:
                print(f"SUCCESS: PUT /settings/{test_key} created/updated correctly.")
            else:
                print(f"FAIL: PUT /settings/{test_key} returned unexpected data: {result}")
        else:
            print(f"FAIL: PUT /settings/{test_key} failed with {response.status_code}: {response.text}")
    except Exception as e:
        print(f"FAIL: Connection error during PUT: {e}")

    # 3. Verify Update via GET
    try:
        response = requests.get(f"{BASE_URL}/settings/{test_key}")
        if response.status_code == 200:
            result = response.json()
            if result.get("valor") == test_val:
                print(f"SUCCESS: GET /settings/{test_key} retrieved updated value.")
            else:
                print(f"FAIL: GET /settings/{test_key} mismatch. Expected {test_val}, got {result.get('valor')}")
        else:
            print(f"FAIL: GET /settings/{test_key} failed with {response.status_code}")
    except Exception as e:
        print(f"FAIL: Connection error during verification GET: {e}")

    # 4. Clean up (Optional, DELETE if endpoint exists)
    try:
        response = requests.delete(f"{BASE_URL}/settings/{test_key}")
        if response.status_code == 204:
             print(f"SUCCESS: DELETE /settings/{test_key} cleaned up.")
        else:
             print(f"WARNING: DELETE /settings/{test_key} failed (maybe not implemented?): {response.status_code}")
    except Exception as e:
        print(f"WARNING: DELETE failed: {e}")

if __name__ == "__main__":
    verify_settings_api()
