
try:
    from paddleocr import PaddleOCR
    print("Intentando inicializar PaddleOCR...")
    # Disable MKLDNN and other things that might trigger the PIR bug
    ocr = PaddleOCR(use_angle_cls=True, lang='es', enable_mkldnn=False, use_tensorrt=False)
    print("✅ Inicialización exitosa")
    
    import io
    from PIL import Image
    # Create a dummy white image
    img = Image.new('RGB', (200, 100), color=(255, 255, 255))
    img.save('dummy.png', format='PNG')
    
    print("Realizando OCR sobre dummy.png...")
    result = ocr.ocr('dummy.png')
    print("OK:", result)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
