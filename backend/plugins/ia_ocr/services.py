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

# ─── Prompt estructurado para Gemini ─────────────────────────────────────────
OCR_PROMPT = """Eres un asistente especializado en extraer datos financieros de tickets y facturas.
Analiza la imagen y extrae EXACTAMENTE la siguiente información en JSON válido.
No incluyas markdown, backticks ni texto adicional. Solo el JSON.

{
  "fecha": "YYYY-MM-DD o null",
  "hora": "HH:MM o null",
  "establecimiento": "nombre del negocio o null",
  "monto_total": número_decimal o null,
  "moneda": "ARS|USD|EUR|BRL|otro o null",
  "metodo_pago": "efectivo|tarjeta_debito|tarjeta_credito|transferencia|otro o null",
  "categoria_sugerida": "Alimentación|Transporte|Entretenimiento|Salud|Servicios|Hogar|Ropa|Educación|Otro",
  "notas": "descripción breve opcional o null",
  "items": [
    {
      "descripcion": "nombre del producto/servicio",
      "cantidad": número o null,
      "precio_unitario": número_decimal o null,
      "subtotal": número_decimal o null
    }
  ]
}

Reglas:
- Si no puedes leer un campo claramente, usa null.
- Nunca inventes datos.
- monto_total debe ser un número (sin símbolos de moneda).
- fecha en formato ISO 8601: YYYY-MM-DD.
- Si hay múltiples ítems, inclúyelos todos en el array items.
- Si no hay ítems detallados, devuelve items como array vacío [].
"""


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
        self._gemini_model = None
        self._tesseract_available = False
        self._initialized = False

    def _ensure_init(self):
        if self._initialized:
            return
        self._initialized = True

        # 1. Intentar inicializar PaddleOCR (prioridad local)
        try:
            from backend.plugins.ia_ocr.paddle_engine import PaddleOcrEngine
            self._paddle_engine = PaddleOcrEngine()
            self._paddle_engine._ensure_init()
        except ImportError:
            logger.info("ℹ️ PaddleOcrEngine no pudo ser importado")

        # 2. Intentar inicializar Gemini (cloud fallback)
        try:
            import os
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self._gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                logger.info("✅ Gemini 1.5 Flash disponible para OCR")
            else:
                logger.warning("⚠️  GEMINI_API_KEY no configurada — Gemini deshabilitado")
        except ImportError:
            logger.warning("⚠️  google-generativeai no instalado")

        # 3. Intentar inicializar Tesseract (último fallback)
        try:
            import pytesseract  # noqa: F401

            self._tesseract_available = True
            logger.info("✅ PyTesseract disponible como fallback de OCR")
        except ImportError:
            logger.info("ℹ️  PyTesseract no disponible (opcional)")

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
                logger.error(f"PaddleOCR falló: {e}. Intentando fallback Gemini.")

        # ── 2. Gemini (motor cloud) ──────────────────────────────────────────
        if not raw_result and self._gemini_model:
            try:
                raw_result = await self._process_with_gemini(file_content, mime_type)
                engine_used = "gemini-1.5-flash"
            except Exception as e:
                logger.error(f"Gemini falló: {e}. Intentando fallback Tesseract.")

        # ── 3. Tesseract (fallback local básico) ─────────────────────────────
        if not raw_result and self._tesseract_available:
            try:
                raw_result = await self._process_with_tesseract(file_content, mime_type)
                engine_used = "tesseract"
            except Exception as e:
                logger.error(f"Tesseract falló: {e}")

        if not raw_result:
            return {
                "error": "No hay motor de OCR disponible. Configura GEMINI_API_KEY.",
                "engine": "none",
            }

        ocr = OcrResult(raw_result)
        result = ocr.to_dict()
        result["engine"] = engine_used
        result["confidence"] = self._estimate_confidence(ocr)
        return result

    async def _process_with_gemini(self, file_content: bytes, mime_type: str) -> dict:
        """Procesar imagen con Google Gemini."""
        response = self._gemini_model.generate_content(
            [
                OCR_PROMPT,
                {"mime_type": mime_type, "data": file_content},
            ]
        )
        text = response.text.strip()
        # Limpiar posibles bloques de código markdown
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)

    async def _process_with_tesseract(self, file_content: bytes, mime_type: str) -> dict:
        """Fallback con PyTesseract: extracción básica sin estructura."""
        import pytesseract
        from PIL import Image
        import io

        image = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(image, lang="spa+eng")

        # Extracción básica por regex
        monto = self._extract_amount_from_text(text)
        fecha = self._extract_date_from_text(text)

        return {
            "fecha": fecha,
            "establecimiento": None,
            "monto_total": monto,
            "moneda": "ARS",
            "categoria_sugerida": "Otro",
            "notas": f"Texto extraído (Tesseract): {text[:200]}",
            "items": [],
        }

    @staticmethod
    def _extract_amount_from_text(text: str) -> Optional[str]:
        """Extrae el monto más probable del texto crudo."""
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
