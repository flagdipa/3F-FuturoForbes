import requests
import sys
import time

BASE_URL = "http://localhost:8000"

def check_endpoint(method, endpoint, expected_status=200):
    url = f"{BASE_URL}{endpoint}"
    try:
        start_time = time.time()
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url)
        duration = (time.time() - start_time) * 1000
        
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - {response.status_code} ({duration:.2f}ms)")
            return True
        else:
            print(f"❌ {method} {endpoint} - Expected {expected_status}, got {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection Refused (Is server running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

def main():
    print("🏥 Starting 3F System Health Check...")
    
    all_passed = True
    
    # 1. Public / Basic Endpoints
    all_passed &= check_endpoint("GET", "/api/estado")
    all_passed &= check_endpoint("GET", "/") # Front
    all_passed &= check_endpoint("GET", "/login") # Front
    
    # 2. Auth Check (Mock login to get token for protected routes)
    # We'll skip complex auth flow for this simple script and focus on public availability
    # or endpoints that return 401 (which means they are up and protecting data)
    
    print("\n🔐 Security Check (Expect 401 for protected routes):")
    all_passed &= check_endpoint("GET", "/api/resumen/", expected_status=401)
    all_passed &= check_endpoint("GET", "/api/reportes/mensual", expected_status=401)
    all_passed &= check_endpoint("GET", "/api/plugins", expected_status=401)

    if all_passed:
        print("\n✨ ALL SYSTEMS OPERATIONAL ✨")
        sys.exit(0)
    else:
        print("\n⚠️ SOME CHECKS FAILED ⚠️")
        sys.exit(1)

if __name__ == "__main__":
    main()
