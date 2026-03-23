from abc import ABC, abstractmethod

class IAProviderPlugin(ABC):
    """
    Contrato base para plugins que proveen servicios de Inteligencia Artificial.
    Cualquier plugin que desee ofrecer capacidades de OCR, Forecasting o Insights
    debe implementar esta interfaz.
    """
    
    @abstractmethod
    def is_configured(self) -> bool:
        """
        Debe devolver True si el plugin tiene todas las credenciales y configuración
        necesaria para operar (ej: API Key cargada).
        """
        ...
    
    @abstractmethod
    async def analyze_receipt(self, image_bytes: bytes, mime_type: str) -> dict:
        """
        Debe procesar los bytes de una imagen y devolver un diccionario con la 
        información estructurada del ticket. 
        
        El formato de retorno esperado es:
        {
            "fecha": "YYYY-MM-DD",
            "establecimiento": "Nombre del Comercio",
            "monto_total": "123.45",
            "moneda": "ARS",
            "items": [], # opcional
            "engine": "nombre-del-plugin",
            "confidence": 0.95
        }
        """
        ...
