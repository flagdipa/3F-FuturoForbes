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
        Intenta parsear el texto identificando fechas, montos e ítems mediante heurísticas.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        monto = self._extract_amount_from_text(lines)
        fecha = self._extract_date_from_text(text)
        
        establecimiento = self._extract_establecimiento(lines)
        categoria_sugerida = self._guess_category(establecimiento)
        items = self._extract_items(lines)

        return {
            "fecha": fecha,
            "establecimiento": establecimiento,
            "monto_total": monto,
            "moneda": "ARS",
            "categoria_sugerida": categoria_sugerida,
            "notas": f"Procesado vía PaddleOCR local.",
            "items": items,
        }

    @staticmethod
    def _extract_establecimiento(lines: list) -> Optional[str]:
        # Known headers or generic text to ignore in the first lines
        ignore_patterns = [
            r'(?i)factura', r'(?i)ticket', r'(?i)consumidor final', 
            r'\d{2}-\d{8}-\d', r'\d{2}/\d{2}/\d{4}', r'(?i)cuit', r'(?i)iva'
        ]
        for line in lines[:7]:
            if len(line) < 3:
                continue
            is_valid = True
            for pat in ignore_patterns:
                if re.search(pat, line):
                    is_valid = False
                    break
            if is_valid:
                return line
        return None

    @staticmethod
    def _guess_category(establecimiento: Optional[str]) -> str:
        if not establecimiento:
            return "Otro"
        est_lower = establecimiento.lower()
        if any(x in est_lower for x in ['coto', 'carrefour', 'jumbo', 'dia', 'disco', 'vea', 'supermercado', 'almacen', 'kiosco', 'maxiconsumo', 'hiper']):
            return "Alimentación"
        if any(x in est_lower for x in ['ypf', 'shell', 'axion', 'puma', 'gulf', 'estacion de servicio']):
            return "Transporte"
        if any(x in est_lower for x in ['farmacity', 'farmacia', 'hospital', 'clinica']):
            return "Salud"
        if any(x in est_lower for x in ['edesur', 'edenor', 'metrogas', 'aysa', 'telecentro', 'personal', 'movistar', 'claro', 'fibertel']):
            return "Servicios"
        if any(x in est_lower for x in ['mcdonalds', 'burger king', 'starbucks', 'cafe', 'bar', 'restaurant', 'restaurante', 'pizzeria', 'mostaza']):
            return "Entretenimiento"
        return "Otro"

    @staticmethod
    def _extract_amount_from_text(lines: list) -> Optional[str]:
        # Iterate backwards to find the Total, which is usually at the bottom
        patterns = [
            r"(?i)total[:\s]+\$?\s*([\d.,]+)",
            r"(?i)importe[:\s]+\$?\s*([\d.,]+)",
            r"(?i)a pagar[:\s]+\$?\s*([\d.,]+)",
        ]
        
        # Primero buscar patrones explícitos
        for line in reversed(lines):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1).replace(",", ".")
                    
        # Fallback: el último número grande de la factura precedido por un $
        for line in reversed(lines):
            match = re.search(r"\$\s*([\d.,]+)", line)
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

    @staticmethod
    def _extract_items(lines: list) -> list:
        items = []
        ignore_keywords = [
            'total', 'subtotal', 'vuelto', 'su pago', 'descuento', 
            'tarjeta', 'efectivo', 'cambio', 'iva ', 'pago', 'importe', 'cuit'
        ]
        
        # Regex to catch line with text and a price at the end "Leche 1L  1500.00"
        # Permite formato "1.500,00" o "1500.00"
        item_pattern = re.compile(r'^(.*?)\s+\$?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))\s*$')
        
        for line in lines:
            if any(k in line.lower() for k in ignore_keywords):
                continue
                
            match = item_pattern.match(line)
            if match:
                desc = match.group(1).strip()
                if len(desc) > 3 and not re.match(r'^[\d\W]+$', desc): # No es solo números y simbolos
                    precio_str = match.group(2).replace(',', '.')
                    items.append({
                        "descripcion": desc[:50], # Limitar longitud de descripción
                        "cantidad": 1,
                        "precio_unitario": precio_str,
                        "subtotal": precio_str
                    })
        return items
