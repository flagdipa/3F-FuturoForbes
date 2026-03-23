"""
IA OCR Services — Extracción de datos de tickets y facturas con Google Gemini.
Incluye fallback a PyTesseract cuando la API no está disponible.
"""
import json
import base64
import logging
import re
from typing import Optional
from decimal import Decimal, InvalidOperation
from datetime import datetime, date

logger = logging.getLogger("ia_ocr.services")

import os
from ...config import settings


class OcrResult:
    """Resultado estructurado del OCR."""

    def __init__(self, raw: dict):
        self.raw = raw
        self.fecha: Optional[str] = raw.get("fecha")
        self.hora: Optional[str] = raw.get("hora")
        self.establecimiento: Optional[str] = raw.get("establecimiento")
        self.moneda: Optional[str] = raw.get("moneda") or "ARS"
        self.metodo_pago: Optional[str] = raw.get("metodo_pago")
        self.categoria_sugerida: Optional[str] = raw.get("categoria_sugerida") or "Otro"
        self.notas: Optional[str] = raw.get("notas")
        self.items: list = raw.get("items") or []

        # Parsear monto con tolerancia
        raw_monto = raw.get("monto_total")
        self.monto_total: Optional[Decimal] = self._safe_decimal(raw_monto)

    @staticmethod
    def _safe_decimal(value) -> Optional[Decimal]:
        if value is None:
            return None
        try:
            # Limpiar strings con símbolos de moneda o separadores
            if isinstance(value, str):
                value = re.sub(r"[^\d.,\-]", "", value)
                value = value.replace(",", ".")
            return Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return None

    def to_transaction_prefill(self) -> dict:
        """Convierte el resultado en un payload de pre-llenado para el formulario de transacción."""
        return {
            "fecha_transaccion": self.fecha or date.today().isoformat(),
            "descripcion": self.establecimiento or "",
            "monto_transaccion": str(self.monto_total) if self.monto_total else "",
            "metodo_pago": self.metodo_pago,
            "notas": self.notas or "",
            "categoria_sugerida": self.categoria_sugerida,
            "moneda": self.moneda,
            "splits_sugeridos": self._build_splits(),
        }

    def _build_splits(self) -> list:
        """Construye splits sugeridos a partir de los ítems del ticket."""
        if not self.items or len(self.items) <= 1:
            return []
        splits = []
        for item in self.items:
            subtotal = self._safe_decimal(item.get("subtotal")) or self._safe_decimal(
                item.get("precio_unitario")
            )
            if subtotal:
                splits.append(
                    {
                        "descripcion": item.get("descripcion", ""),
                        "monto": str(subtotal),
                        "cantidad": item.get("cantidad", 1),
                    }
                )
        return splits

    def to_dict(self) -> dict:
        return {
            "fecha": self.fecha,
            "hora": self.hora,
            "establecimiento": self.establecimiento,
            "monto_total": str(self.monto_total) if self.monto_total else None,
            "moneda": self.moneda,
            "metodo_pago": self.metodo_pago,
            "categoria_sugerida": self.categoria_sugerida,
            "notas": self.notas,
            "items": self.items,
            "transaction_prefill": self.to_transaction_prefill(),
        }


class OcrService:
    """Servicio de OCR. Usa PaddleOCR como motor primario, Gemini como backup, y PyTesseract como fallback."""

    def __init__(self):
        self._paddle_engine = None
        self._tesseract_available = False
        self._initialized = False

    def _ensure_init(self):
        if self._initialized:
            return
        self._initialized = True

        # 1. Intentar inicializar PaddleOCR (prioridad local pesado)
        try:
            from backend.plugins.ia_ocr.paddle_engine import PaddleOcrEngine
            self._paddle_engine = PaddleOcrEngine()
            self._paddle_engine._ensure_init()
        except Exception as e:
            logger.info(f"ℹ️ PaddleOcrEngine no disponible: {e}")

        # 2. Intentar inicializar Tesseract (motor local ligero)
        try:
            import pytesseract
            
            # Configurar el comando de Tesseract desde settings
            tess_cmd = settings.TESSERACT_CMD
            if os.path.exists(tess_cmd):
                pytesseract.pytesseract.tesseract_cmd = tess_cmd
                self._tesseract_available = True
                logger.info(f"✅ PyTesseract configurado en: {tess_cmd}")
            else:
                # Intentar si está en el PATH
                try:
                    import subprocess
                    subprocess.run(["tesseract", "--version"], capture_output=True, check=True)
                    self._tesseract_available = True
                    logger.info("✅ PyTesseract detectado en el PATH")
                except:
                    logger.warning(f"⚠️ Tesseract no encontrado en {tess_cmd} ni en PATH")
        except ImportError:
            logger.warning("⚠️ pytesseract no instalado")

    async def process_image(
        self, file_content: bytes, mime_type: str
    ) -> dict:
        """
        Procesa una imagen de ticket/factura y extrae datos financieros.

        Args:
            file_content: Bytes del archivo de imagen o PDF.
            mime_type: Tipo MIME del archivo.

        Returns:
            Diccionario con datos extraídos, prefill de transacción y confianza.
        """
        self._ensure_init()

        engine_used = "none"
        raw_result = {}

        # ── 1. PaddleOCR (motor prioritario local) ───────────────────────────
        if self._paddle_engine and getattr(self._paddle_engine, '_available', False):
            try:
                raw_result = await self._paddle_engine.process(file_content, mime_type)
                engine_used = "paddleocr"
            except Exception as e:
                logger.error(f"PaddleOCR falló: {e}. Intentando fallback Tesseract.")

        # ── 2. Tesseract (motor local ligero) ─────────────────────────────
        if not raw_result and self._tesseract_available:
            try:
                raw_result = await self._process_with_tesseract(file_content, mime_type)
                engine_used = "tesseract"
            except Exception as e:
                logger.error(f"Tesseract falló: {e}")

        if not raw_result:
            return {
                "error": "Ningún motor de OCR disponible. Configure TESSERACT_CMD o instale PaddleOCR.",
                "engine": "none",
            }

        ocr = OcrResult(raw_result)
        result = ocr.to_dict()
        result["engine"] = engine_used
        result["confidence"] = self._estimate_confidence(ocr)
        return result

    async def _process_with_tesseract(self, file_content: bytes, mime_type: str) -> dict:
        """Fallback con PyTesseract: extracción básica sin estructura."""
        import pytesseract
        from PIL import Image
        import io

        image = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(image, lang="spa+eng")
        
        # Limpiar texto
        clean_lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Extracción básica por regex
        monto = self._extract_amount_from_text(text)
        fecha = self._extract_date_from_text(text)
        
        # Heurística para establecimiento: primera línea alfanumérica
        establecimiento = None
        for line in clean_lines:
            if re.search(r'[A-Za-z0-9]', line) and len(line) > 3:
                # Evitar líneas que parezcan solo números (posible CUIT o fecha)
                if not re.match(r'^[\d\s\-\/:]+$', line):
                    establecimiento = line
                    break

        return {
            "fecha": fecha,
            "establecimiento": establecimiento,
            "monto_total": monto,
            "moneda": "ARS",
            "categoria_sugerida": "Otro",
            "notas": f"Procesado con Tesseract local.",
            "items": [],
        }

    @staticmethod
    def _extract_amount_from_text(text: str) -> Optional[str]:
        """Extrae el monto más probable del texto crudo (Heurística LATAM)."""
        # 1. Buscar palabras clave primero
        keywords = ["total", "importe", "pagar", "final", "total a pagar", "monto"]
        lines = text.split('\n')
        
        for kw in keywords:
            for line in lines:
                if kw in line.lower():
                    # Buscar patrones de moneda/número en esa línea
                    match = re.search(r"([\d\.\,]{2,})", line)
                    if match:
                        val = match.group(1).replace(".", "").replace(",", ".")
                        try:
                            if float(val) > 0:
                                return val
                        except: pass

        # 2. Si no hay keywords, buscar el número decimal más alto (típico en tickets)
        # Excluyendo números sospechosos de ser CUIT (ej: 30-12345678-9) o teléfonos
        potential_amounts = []
        # Buscamos algo que parezca un decimal (XX.XX o XX,XX)
        matches = re.findall(r"(\d+[\.\,]\d{2})(?!\d)", text)
        for m in matches:
            val = m.replace(".", "").replace(",", ".")
            try:
                potential_amounts.append(float(val))
            except: pass
            
        if potential_amounts:
            return str(max(potential_amounts))
            
        return None

    @staticmethod
    def _extract_date_from_text(text: str) -> Optional[str]:
        """Extrae la fecha del texto crudo."""
        patterns = [
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{2}-\d{2}-\d{4})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                raw = match.group(1)
                # Normalizar a YYYY-MM-DD
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                    try:
                        return datetime.strptime(raw, fmt).date().isoformat()
                    except ValueError:
                        continue
        return None

    @staticmethod
    def _estimate_confidence(ocr: OcrResult) -> float:
        """Estima la confianza del resultado basado en campos presentes."""
        score = 0.0
        if ocr.monto_total:
            score += 0.4
        if ocr.establecimiento:
            score += 0.2
        if ocr.fecha:
            score += 0.2
        if ocr.categoria_sugerida and ocr.categoria_sugerida != "Otro":
            score += 0.1
        if ocr.items:
            score += 0.1
        return round(score, 2)


# Instancia global del servicio
ocr_service = OcrService()
