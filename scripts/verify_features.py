import requests
import os

BASE_URL = "http://localhost:8000/api"

def test_flow():
    print("--- 3F Feature Verification ---")
    
    # 1. Login (Emergency Bypass)
    print("Logging in...")
    login_data = {"email": "fer@forbes.com", "password": "password"}
    res = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if res.status_code != 200:
        print(f"Login failed: {res.status_code} {res.text}")
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Login successful")

    # 2. Get Cuentas/Categorias for data
    cuentas = requests.get(f"{BASE_URL}/cuentas/", headers=headers).json()["data"]
    categorias = requests.get(f"{BASE_URL}/categorias/", headers=headers).json()["data"]
    beneficiarios = requests.get(f"{BASE_URL}/beneficiarios/", headers=headers).json()["data"]
    
    if not cuentas or not categorias or not beneficiarios:
        print("Missing base data (cuentas/categorias/beneficiarios)")
        return
        
    id_cuenta = cuentas[0]["id_cuenta"]
    id_ben = beneficiarios[0]["id_beneficiario"]
    
    # 3. Create Split Transaction
    print("Creating split transaction...")
    tx_data = {
        "id_cuenta": id_cuenta,
        "id_beneficiario": id_ben,
        "monto_transaccion": 1500.0,
        "codigo_transaccion": "Withdrawal",
        "notas": "TEST_VERIFICATION_SPLIT",
        "es_dividida": True,
        "divisiones": [
            {"id_categoria": categorias[0]["id_categoria"], "monto_division": 1000.0, "notas": "Split 1"},
            {"id_categoria": categorias[1]["id_categoria"] if len(categorias) > 1 else categorias[0]["id_categoria"], "monto_division": 500.0, "notas": "Split 2"}
        ]
    }
    res = requests.post(f"{BASE_URL}/transacciones/", json=tx_data, headers=headers)
    if res.status_code != 200:
        print(f"Failed to create split tx: {res.text}")
        return
    tx = res.json()
    tx_id = tx["id_transaccion"]
    print(f"✓ Split transaction created ID: {tx_id}")

    # 4. Upload Attachment
    print("Uploading attachment...")
    with open("test_receipt.txt", "w") as f:
        f.write("Receipt Data Test Content")
        
    files = {'file': ('test_receipt.txt', open('test_receipt.txt', 'rb'), 'text/plain')}
    data = {'tipo_referencia': 'Transaccion', 'id_referencia': tx_id, 'descripcion': 'Comprobante de test'}
    res = requests.post(f"{BASE_URL}/attachments/", files=files, data=data, headers=headers)
    if res.status_code != 201:
        print(f"Failed to upload attachment: {res.text}")
    else:
        print("✓ Attachment uploaded")
        adj_id = res.json()["id_adjunto"]
        
        # 5. List Attachments
        res = requests.get(f"{BASE_URL}/attachments/Transaccion/{tx_id}", headers=headers)
        if len(res.json()) > 0:
            print(f"✓ Found {len(res.json())} attachments for TX")
        else:
            print("✗ No attachments found")

    # Cleanup (Optional)
    # print("Cleaning up test TX...")
    # requests.delete(f"{BASE_URL}/transacciones/{tx_id}", headers=headers)
    # os.remove("test_receipt.txt")
    print("--- End of Verification ---")

if __name__ == "__main__":
    test_flow()
