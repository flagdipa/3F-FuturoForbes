"""
PaddleOCR Engine Wrapper para el plugin IA OCR.
Carga el modelo de forma perezosa (lazy-load) para no impactar el inicio del sistema.
Extrae texto crudo y usa expresiones regulares (heredadas de Tesseract) para encontrar
información financiera.
"""
import logging
import re
import io
import asyncio
from typing import Optional
from datetime import datetime

logger = logging.getLogger("ia_ocr.paddle_engine")

class PaddleOcrEngine:
    def __init__(self):
        self._ocr = None
        self._available = False
        self._initialized = False

    def _ensure_init(self):
        if self._initialized:
            return
        self._initialized = True
        
        try:
            # Requires paddleocr to be installed
            from paddleocr import PaddleOCR
            
            # Initialize with Spanish by default, using CPU (use_gpu=False makes it safer for most environments)
            # You can change use_gpu=True if CUDA is configured correctly.
            self._ocr = PaddleOCR(use_angle_cls=True, lang='es', use_gpu=False, show_log=False)
            self._available = True
            logger.info("✅ PaddleOCR inicializado correctamente")
        except ImportError:
            logger.info("ℹ️ PaddleOCR no disponible. Instalar con: pip install paddlepaddle paddleocr")
        except Exception as e:
            logger.error(f"❌ Error al inicializar PaddleOCR: {e}")

    async def process(self, file_content: bytes, mime_type: str) -> dict:
        """
        Runs PaddleOCR on the given image bytes and parses it to a structured format.
        """
        self._ensure_init()
        if not self._available:
            raise Exception("PaddleOCR no está disponible")
            
        # We need to run it in a thread pool since paddleocr is synchronous and CPU-bound
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self._run_ocr_sync, file_content)
        
        return self._parse_text_to_structured(result)
        
    def _run_ocr_sync(self, file_content: bytes) -> str:
        """Synchronous wrapper for PaddleOCR."""
        try:
            import numpy as np
            import cv2
            from PIL import Image
            
            # Convert bytes to cv2 image
            image = Image.open(io.BytesIO(file_content))
            image = image.convert('RGB')
            img_array = np.array(image)
            # Convert RGB to BGR for cv2
            img_array = img_array[:, :, ::-1]

            # Perform OCR
            result = self._ocr.ocr(img_array, cls=True)
            
            # result is a list of lists.
            # Example structure: [[[[x,y],[x,y],[x,y],[x,y]], ('text', confidence)], ...]
            extracted_text_lines = []
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    extracted_text_lines.append(text)
            
            return "\n".join(extracted_text_lines)
            
        except Exception as e:
            logger.error(f"Error procesando imagen con PaddleOCR: {e}")
            raise e

    def _parse_text_to_structured(self, text: str) -> dict:
        """
        Intenta parsear el texto de la misma forma que el fallback de Tesseract.
        """
        monto = self._extract_amount_from_text(text)
        fecha = self._extract_date_from_text(text)
        
        # Heurística simple para "establecimiento": suele ser una de las primeras líneas en tickets
        establecimiento = None
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # Tomar la primera línea que no sea un CUIT ni fecha
            for line in lines[:3]:
                if not re.search(r'\d{2}-\d{8}-\d|\d{2}/\d{2}/\d{4}', line):
                    establecimiento = line
                    break

        return {
            "fecha": fecha,
            "establecimiento": establecimiento,
            "monto_total": monto,
            "moneda": "ARS",
            "categoria_sugerida": "Otro", # Default
            "notas": f"Procesado vía PaddleOCR local. Extracto:\n{text[:150]}...",
            "items": [],
        }

    @staticmethod
    def _extract_amount_from_text(text: str) -> Optional[str]:
        # Same regex patterns from the Tesseract fallback
        patterns = [
            r"total[:\s]+\$?\s*([\d.,]+)",
            r"importe[:\s]+\$?\s*([\d.,]+)",
            r"a pagar[:\s]+\$?\s*([\d.,]+)",
            r"\$\s*([\d.,]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).replace(",", ".")
        return None

    @staticmethod
    def _extract_date_from_text(text: str) -> Optional[str]:
        patterns = [
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{2}-\d{2}-\d{4})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                raw = match.group(1)
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                    try:
                        return datetime.strptime(raw, fmt).date().isoformat()
                    except ValueError:
                        continue
        return None
