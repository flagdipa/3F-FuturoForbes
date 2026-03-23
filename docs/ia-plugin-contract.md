# IA Plugin Contract (Contrato de Proveedor de IA)

Este documento describe el estándar arquitectónico que deben cumplir los plugins que deseen proveer servicios de Inteligencia Artificial (LLM Cloud, OCR Cloud, etc.) al sistema 3F (Futuro Forbes).

## Arquitectura de Plugins

El sistema 3F utiliza una arquitectura de plugins para desacoplar el núcleo de la aplicación de los proveedores externos de servicios cognitivos. Esto permite:
1.  **Privacidad**: El usuario decide qué proveedores activar y cuándo.
2.  **Mantenibilidad**: Es posible actualizar o añadir nuevos proveedores (Gemini, OpenAI, Claude) sin tocar el código core.
3.  **Seguridad**: Las API Keys se mantienen dentro de la configuración del plugin respectivo, no en el core del sistema.

## Interfaz `IAProviderPlugin`

Todos los plugins que provean servicios de IA deben heredar de `backend.plugins.base_ia.IAProviderPlugin` y completar los métodos requeridos:

```python
from backend.plugins.base_ia import IAProviderPlugin

class MiPluginIA(IAProviderPlugin):
    def is_configured(self) -> bool:
        # Devuelve True solo si las API Keys necesarias están presentes
        return bool(os.environ.get("MY_API_KEY"))

    async def analyze_receipt(self, image_bytes: bytes, mime_type: str) -> dict:
        # Lógica para llamar al proveedor cloud (ej: Gemini, OpenAI)
        # y parsear el resultado a JSON estructurado.
        ...
```

## Formato de Respuesta Esperado

Para asegurar la compatibilidad con el frontend de 3F, el método `analyze_receipt` debe devolver invariablemente un diccionario con las siguientes claves:

| Clave | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `fecha` | `string` | Fecha del ticket en formato ISO (YYYY-MM-DD) | `"2024-03-22"` |
| `establecimiento` | `string` | Nombre del comercio o payee | `"Supermercado Coto"` |
| `monto_total` | `string` | Monto total como string (para evitar float precision errors) | `"4500.50"` |
| `moneda` | `string` | Código de moneda ISO 4217 | `"ARS"` |
| `engine` | `string` | Identificador del plugin/motor usado | `"gemini-cloud"` |
| `confidence` | `float` | Confianza estimada del resultado (0.0 a 1.0) | `0.95` |
| `items` | `list` | (Opcional) Desglose de ítems (splits sugeridos) | `[]` |

## Cómo Registrar el Plugin

1.  Crea la carpeta de tu plugin en `backend/plugins/mi_nombre/`.
2.  Implementa la lógica en un archivo `.py`.
3.  Asegúrate de que el plugin sea descubierto por el `Plugin Manager`.
4.  El sistema core (`backend/api/v1/ia.py`) en versiones futuras podrá detectar plugins que hereden de `IAProviderPlugin` para ofrecer una cadena de fallbacks dinámica.

## Ejemplo Mínimo (Referencia para Gemini)

```python
# Un ejemplo simplificado de cómo se vería un plugin real de Gemini
class GeminiOcrPlugin(IAProviderPlugin):
    async def analyze_receipt(self, image_bytes, mime_type):
        client = genai.Client(api_key=...)
        response = await client.generate_content(...) # Vision analysis
        data = json.loads(response.text)
        return {
            "fecha": data["date"],
            "establecimiento": data["payee"],
            "monto_total": str(data["amount"]),
            "moneda": "ARS",
            "engine": "gemini-plugin",
            "confidence": 0.9
        }
```
