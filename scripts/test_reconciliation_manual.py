import requests
import os

url = "http://127.0.0.1:8000/api/reconciliation/preview"
file_path = "test_reconciliation.csv"
account_id = 1

try:
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'text/csv')}
        data = {'id_cuenta': account_id}
        print(f"Sending request to {url}...")
        response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON:")
            print(response.json())
        else:
            print("Error Response:")
            print(response.text)
except Exception as e:
    print(f"Error: {e}")
