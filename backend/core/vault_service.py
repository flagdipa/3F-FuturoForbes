import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class VaultService:
    def __init__(self, upload_dir: str = "uploads/attachments"):
        self.upload_dir = Path(upload_dir)
        self.ensure_dir()

    def ensure_dir(self):
        if not self.upload_dir.exists():
            self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, file) -> str:
        """
        Saves an uploaded file to the vault with a timestamped name.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"VAULT_{timestamp}_{file.filename}"
        file_path = self.upload_dir / filename
        
        import shutil
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File {filename} saved directly to vault.")
        return filename

    def get_all_files(self) -> List[Dict]:
        """
        Scans the attachments directory and returns a list of file metadata.
        """
        files = []
        try:
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "extension": file_path.suffix.lower(),
                        "path": str(file_path)
                    })
            # Sort by creation date descending
            files.sort(key=lambda x: x["created_at"], reverse=True)
            return files
        except Exception as e:
            logger.error(f"Error indexing vault files: {e}")
            return []

    def delete_file(self, filename: str) -> bool:
        """
        Deletes a file from the vault.
        """
        file_path = self.upload_dir / filename
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                logger.info(f"File {filename} deleted from vault.")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False

    async def extract_text(self, filename: str) -> Optional[str]:
        """
        Uses pytesseract to extract text from images in the vault.
        Checks if 'ia_ocr' plugin is active.
        """
        # Phase 6.4: Plugin Integration
        from .database import engine
        from ..models.models_plugins import Plugin
        from sqlmodel import Session, select
        
        with Session(engine) as session:
            statement = select(Plugin).where(Plugin.nombre_tecnico == "ia_ocr")
            plugin = session.exec(statement).first()
            
            if not plugin or not plugin.activo:
                return "Módulo IA OCR deshabilitado. Active el módulo en la sección de Módulos."
            
            config = plugin.configuracion or {}
            confidence_threshold = config.get("confidence_threshold", 0.5)
            # Provider placeholder (for future Google GenAI implementation)
            provider = config.get("provider", "pytesseract")

        file_path = self.upload_dir / filename
        if not file_path.exists():
            return None
            
        try:
            from PIL import Image
            import pytesseract
            
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                img = Image.open(file_path)
                # In a real scenario, we would use the provider and confidence_threshold here.
                # For now, we remain with pytesseract as the local engine.
                text = pytesseract.image_to_string(img)
                return text.strip() if text else "No se detectó texto legible."
            
            elif file_path.suffix.lower() == '.pdf':
                return "Soporte para PDF requiere poppler-utils. Por ahora, extrae texto de imágenes."
            
            return "Formato de archivo no compatible para OCR."
            
        except ImportError:
            return "Error: pytesseract o Pillow no están instalados en el servidor."
        except Exception as e:
            logger.error(f"Error in OCR for {filename}: {e}")
            return f"Error procesando OCR: {str(e)}"

vault_service = VaultService()
