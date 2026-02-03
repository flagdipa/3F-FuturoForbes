import google.generativeai as genai
import os
from .config import settings

class IAService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    async def procesar_ticket(self, file_content: bytes, mime_type: str):
        if not self.model:
            return {"error": "GEMINI_API_KEY no configurada"}

        prompt = """
        Analiza esta imagen de un ticket o recibo de gasto.
        Extrae la siguiente información en formato JSON:
        {
            "monto": float,
            "beneficiario": string,
            "fecha": string (ISO 8601),
            "categoria_sugerida": string,
            "notas": string
        }
        Si no puedes encontrar un dato, deja el campo como null.
        Solo responde con el objeto JSON.
        """

        try:
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": mime_type,
                    "data": file_content
                }
            ])
            # Intentar limpiar la respuesta si tiene markdown
            text = response.text.replace('```json', '').replace('```', '').strip()
            return text
        except Exception as e:
            return {"error": str(e)}

ia_service = IAService()
