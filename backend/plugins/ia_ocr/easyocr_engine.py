"""
EasyOCR Engine Wrapper para el plugin IA OCR.
Reemplaza a PaddleOCR en caso de problemas de entorno bajo Python 3.13.
"""
import logging
import re
import asyncio
from typing import Optional
from datetime import datetime

logger = logging.getLogger("ia_ocr.easyocr_engine")

class EasyOcrEngine:
    def __init__(self):
        self._reader = None
        self._available = False
        self._initialized = False

    def _ensure_init(self):
        if self._initialized:
            return
        self._initialized = True
        
        try:
            import easyocr
            # Inicializamos en español e inglés, y le decimos que no use GPU si no hay torch+cuda
            self._reader = easyocr.Reader(['es', 'en'], gpu=False)
            self._available = True
            logger.info("✅ EasyOCR inicializado correctamente")
        except ImportError:
            logger.info("ℹ️ EasyOCR no disponible. Instalar con: pip install easyocr")
        except Exception as e:
            logger.error(f"❌ Error al inicializar EasyOCR: {e}")

    async def process(self, file_content: bytes, mime_type: str) -> dict:
        """
        Runs EasyOCR on the given image bytes and parses it to a structured format.
        """
        self._ensure_init()
        if not self._available:
            raise Exception("EasyOCR no está disponible")
            
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self._run_ocr_sync, file_content)
        
        return self._parse_text_to_structured(result)
        
    def _run_ocr_sync(self, file_content: bytes) -> str:
        """Synchronous wrapper for EasyOCR."""
        try:
            # EasyOCR can directly read from bytes
            # result is a list of tuples: (bbox, text, prob)
            result = self._reader.readtext(file_content)
            
            extracted_text_lines = []
            for item in result:
                text = item[1]
                extracted_text_lines.append(text)
            
            return "\n".join(extracted_text_lines)
            
        except Exception as e:
            import traceback
            logger.error(f"Error procesando imagen con EasyOCR: {e}\n{traceback.format_exc()}")
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
            "notas": f"Procesado vía EasyOCR local.",
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
        # Very simple heuristic: try to find a float price at the end of a line
        for line in lines:
            if any(k in line.lower() for k in ignore_keywords):
                continue
            
            match = re.search(r"^(.*?)\s+[\$]?\s*([\d.,]+)$", line)
            if match:
                name = match.group(1).strip()
                price = match.group(2).replace(",", ".")
                
                # Minimum filters
                if len(name) > 3 and not re.match(r"^\d+$", name):
                    items.append({"nombre": name, "precio": price})
                    
        return items
