from typing import Dict, Any, List
from backend.plugins.base import BasePlugin
from backend.core.ia_service import ia_service

class IaOcrPlugin(BasePlugin):
    nombre_tecnico = "ia_ocr"
    nombre_display = "IA OCR Vision"
    version = "1.0.2"
    autor = "3F Core"
    descripcion = "Extracción inteligente de datos de facturas y tickets mediante Computer Vision."
    hooks = ["vault_file_upload", "transaction_created"]

    async def initialize(self):
        self.logger.info("IA OCR Plugin inicializado")

    async def shutdown(self):
        self.logger.info("IA OCR Plugin desactivado")

    async def on_vault_file_upload(self, file_content: bytes, mime_type: str, **kwargs):
        """Hook disparado cuando se sube un archivo al vault"""
        self.logger.info("IA OCR: Procesando nuevo archivo en vault")
        return await ia_service.procesar_ticket(file_content, mime_type)

    async def on_transaction_created(self, transaction_id: int, **kwargs):
        """Hook disparado al crear una transacción (para sugerir datos si hay adjunto)"""
        pass
