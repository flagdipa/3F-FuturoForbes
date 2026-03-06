import logging
import json
from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("ia_engine")

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class IAEngine:
    """
    Motor de Inteligencia Artificial para 3F (Futuro Forbes).
    Integra Gemini 1.5 Flash (OCR/Vision) y Gemini 1.5 Pro (Forecasting).
    Soporta fallbacks heurísticos estructurados si la API no está disponible.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.is_active = False
        
        if self.api_key and HAS_GENAI:
            try:
                genai.configure(api_key=self.api_key)
                self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
                self.pro_model = genai.GenerativeModel('gemini-1.5-pro')
                self.is_active = True
                logger.info("IA Engine (Gemini) activado correctamente.")
            except Exception as e:
                logger.error(f"Error configurando Gemini: {e}")
        else:
            logger.warning("IA Engine funcionando en modo OFFLINE (Mock/Heurístico).")

    async def analyze_receipt(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analiza un ticket/factura extrayendo sus datos estructurados mediante OCR.
        """
        if not self.is_active:
            # Fallback simulado
            await __import__('asyncio').sleep(2)
            return {
                "store_name": "STARBUCKS INC",
                "date": datetime.now().date().isoformat(),
                "total": Decimal("4500.50"),
                "currency": "ARS",
                "items": [
                    {"description": "Cafe Latte Grande", "quantity": 1, "unit_price": "2500.00"},
                    {"description": "Croissant", "quantity": 1, "unit_price": "2000.50"}
                ],
                "confidence": 0.85
            }
            
        try:
            prompt = """
            Eres un analizador de tickets de compra experto. Analiza la imagen y extrae 
            los siguientes datos en formato JSON estricto (no incluyas markdown, SOLO JSON válido):
            {
               "store_name": "Nombre del comercio",
               "date": "YYYY-MM-DD",
               "total": "El total pagado en formato decimal",
               "currency": "Moneda deducida (ARS, USD, EUR, etc)",
               "items": [
                 { "description": "Detalle item", "quantity": 1, "unit_price": "100.00" }
               ]
            }
            """
            
            # TODO: Convertir bytes a formato legible por Gemini (base64 o PIL image)
            # contents = [ prompt, {"mime_type": "image/jpeg", "data": image_bytes} ]
            # response = self.vision_model.generate_content(contents)
            # result = json.loads(response.text)
            # return result
            
            return {"error": "Implementación de OCR pendiente de parseo de imagen."}
            
        except Exception as e:
            logger.error(f"Error en OCR: {e}")
            raise Exception("No se pudo procesar el ticket.")

    async def forecast_cashflow(self, user_transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predice el flujo de caja para los próximos meses en base al historial.
        """
        if not self.is_active or not user_transactions:
            return {
                "predicted_income": [950000, 950000, 950000],
                "predicted_expenses": [420000, 435000, 410000],
                "anomalies_detected": ["Gasto de Supermercado anormalmente alto en quincena actual"],
                "recommendations": ["Sugerimos retrasar la compra de 'Tecnología' al próximo mes."]
            }
            
        prompt = f"""
        Actúa como un analista financiero. Aquí tienes un historial de transacciones (JSON).
        Predice los ingresos y gastos de los próximos 3 meses, detecta anomalías y danos 2 recomendaciones.
        Devuelve el resultado estructurado en JSON.
        Datos: {json.dumps(user_transactions[:50])} # Limitamos para no exceder tokens
        """
        try:
            response = self.pro_model.generate_content(prompt)
            # En producción, usar strict parsing.
            import re
            json_str = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
            if json_str:
                return json.loads(json_str.group(1))
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error en Forecasting: {e}")
            raise

    async def generate_insights(self, user_id: int) -> List[Dict[str, str]]:
        """
        Genera pequeñas píldoras de conocimiento (Insights) a mostrar en el dashboard.
        """
        return [
            {"type": "achievement", "title": "Ahorro Sostenido", "desc": "Tus gastos en transporte se redujeron 15% este mes."},
            {"type": "warning", "title": "Alerta de Presupuesto", "desc": "Estás a 10% de exceder el presupuesto de 'Salidas' y falta 1 semana para fin de mes."}
        ]
