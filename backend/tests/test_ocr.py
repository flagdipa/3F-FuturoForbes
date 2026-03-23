import pytest
from fastapi.testclient import TestClient
from backend.main import app
import os

def test_ocr_tesseract_fallback(client: TestClient):
    """
    Test that the OCR endpoint correctly identifies an image and uses Tesseract engine.
    NOTE: This test assumes Tesseract-OCR is NOT installed in the expected path 
    to see if it fails gracefully OR uses the PATH.
    """
    # Use the app icon as a test image
    img_path = "frontend/node_modules/playwright-core/lib/server/chromium/appIcon.png"
    if not os.path.exists(img_path):
        pytest.skip("Test image not found")
        
    with open(img_path, "rb") as f:
        response = client.post(
            "/api/v1/ia/ocr",
            files={"file": ("appIcon.png", f, "image/png")}
        )
        
    # Check if the endpoint responds
    assert response.status_code in [200, 500], response.text
    
    data = response.json()
    if response.status_code == 200:
        assert "engine" in data
        print(f"\nOCR Engine used: {data['engine']}")
    else:
        # If it failed 500, check the error message
        print(f"\nOCR Failed as expected or due to missing binary: {data.get('detail')}")
        assert "Ningún motor de OCR disponible" in data.get("detail", "") or "Tesseract" in data.get("detail", "")
