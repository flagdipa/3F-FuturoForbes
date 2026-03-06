"""
IA OCR Plugin — Extracción de datos de tickets/facturas con Gemini.
Pre-llena el formulario de transacción automáticamente.
"""
from backend.plugins.base import BasePlugin
from backend.plugins.ia_ocr.services import ocr_service


class IaOcrPlugin(BasePlugin):
    nombre_tecnico = "ia_ocr"
    nombre_display = "IA OCR — Escaneo de Tickets"
    version = "1.1.0"
    autor = "3F Core"
    descripcion = (
        "Extrae automáticamente datos financieros de imágenes de tickets y facturas "
        "usando Google Gemini 1.5 Flash. Pre-llena el formulario de transacción y "
        "sugiere splits por ítem si el ticket tiene detalle de productos."
    )
    hooks = ["vault_file_upload"]

    async def initialize(self):
        # Pre-inicializar el motor de OCR
        ocr_service._ensure_init()
        engine = "Gemini" if ocr_service._gemini_model else (
            "Tesseract" if ocr_service._tesseract_available else "ninguno"
        )
        self.logger.info(
            f"IA OCR Plugin inicializado. Motor disponible: {engine}"
        )

    async def shutdown(self):
        self.logger.info("IA OCR Plugin desactivado")

    async def on_vault_file_upload(self, file_content: bytes, mime_type: str, **kwargs):
        """
        Hook: procesa automáticamente imágenes subidas al Vault.
        Retorna los datos para pre-llenar el formulario de transacción.
        """
        if not mime_type.startswith("image/") and mime_type != "application/pdf":
            return None
        self.logger.info("IA OCR: Procesando archivo subido al Vault...")
        return await ocr_service.process_image(file_content, mime_type)

    async def process_file(self, file_content: bytes, mime_type: str) -> dict:
        """API pública del plugin: procesar imagen/PDF directamente."""
        return await ocr_service.process_image(file_content, mime_type)
