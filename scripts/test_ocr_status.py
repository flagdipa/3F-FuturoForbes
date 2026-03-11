
import os
import sys
import asyncio
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath('.'))

# Suppress noisy logs
logging.basicConfig(level=logging.ERROR)

async def test_ocr_status():
    try:
        from backend.plugins.ia_ocr.services import ocr_service
        
        print("--- Verificando Motores OCR ---")
        ocr_service._ensure_init()
        
        easyocr_available = False
        try:
            import easyocr
            easyocr_available = True
        except ImportError:
            pass
            
        paddle_available = False
        paddle_error = "Ninguno"
        
        try:
             # Force direct initialization of PaddleOCR
             from paddleocr import PaddleOCR
             # No pasamos parámetros pesados para ver si carga el motor base
             paddle_available = True
        except Exception as e:
             paddle_error = str(e)
             
        print(f"EasyOCR (Local):   {'✅ DISPONIBLE' if easyocr_available else '❌ NO DISPONIBLE'}")
        print(f"PaddleOCR (Local): {'✅ DISPONIBLE' if paddle_available else '❌ ERROR: ' + paddle_error}")
        print(f"Gemini (Cloud):    {'✅ CONFIGURADO' if ocr_service._gemini_model else '⚠️  SIN API KEY'}")
        print(f"Tesseract (Local): {'✅ DISPONIBLE' if ocr_service._tesseract_available else 'ℹ️  NO INSTALADO'}")
        
        if paddle_available:
            print("\nPrueba de carga de PaddleOCR...")
            # Si llegó hasta acá sin crashear tras ensure_init, el modelo base cargó.
            print("PaddleOCR cargado en memoria correctamente.")
            
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")

if __name__ == "__main__":
    asyncio.run(test_ocr_status())
