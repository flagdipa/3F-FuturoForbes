
import os
import sys
import asyncio
import logging
import io

# Add project root to sys.path
sys.path.append(os.path.abspath('.'))

# Set logging to see what PaddleOCR is doing
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ia_ocr.paddle_engine")
logger.setLevel(logging.DEBUG)

async def test_ocr_execution():
    try:
        from backend.plugins.ia_ocr.services import ocr_service
        from PIL import Image
        
        # Create a dummy white image
        img = Image.new('RGB', (200, 100), color=(255, 255, 255))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        file_content = img_byte_arr.getvalue()
        print("Iniciando procesamiento de imagen de prueba...")
        
        ocr_service._ensure_init()

        if hasattr(ocr_service, '_paddle_engine'):
             pe = ocr_service._paddle_engine
             if pe:
                 print(f"DEBUG: Paddle Engine Initialized: {pe._initialized}")
                 print(f"DEBUG: Paddle Engine Available: {pe._available}")
        
        result = await ocr_service.process_image(file_content, "image/png")
        
        print("\n--- Resultado del OCR ---")
        import json
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución del OCR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ocr_execution())
