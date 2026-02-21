from backend.core.database import Session, engine
from backend.models.models_plugins import Plugin
from sqlmodel import select

with Session(engine) as session:
    p = session.exec(select(Plugin).where(Plugin.nombre_tecnico == 'argentina_datos')).first()
    if p:
        p.configuracion = {
            'intervalo_actualizacion_minutos': 60,
            'apis_disponibles': {
                'cotizaciones_actuales': {'activa': True, 'endpoint': '/v1/cotizaciones', 'label': 'Cotizaciones actuales'},
                'dolar_blue': {'activa': True, 'endpoint': '/v1/cotizaciones/dolares/blue', 'label': 'Dólar Blue'},
                'dolar_oficial': {'activa': False, 'endpoint': '/v1/cotizaciones/dolares/oficial', 'label': 'Dólar Oficial'},
                'dolar_bolsa': {'activa': False, 'endpoint': '/v1/cotizaciones/dolares/bolsa', 'label': 'Dólar Bolsa / MEP'},
                'dolar_ccl': {'activa': False, 'endpoint': '/v1/cotizaciones/dolares/contadoconliqui', 'label': 'Dólar CCL'},
                'dolar_cripto': {'activa': False, 'endpoint': '/v1/cotizaciones/dolares/cripto', 'label': 'Dólar Cripto'},
                'dolar_mayorista': {'activa': False, 'endpoint': '/v1/cotizaciones/dolares/mayorista', 'label': 'Dólar Mayorista'},
                'dolar_tarjeta': {'activa': False, 'endpoint': '/v1/cotizaciones/dolares/tarjeta', 'label': 'Dólar Tarjeta'},
                'euro': {'activa': False, 'endpoint': '/v1/cotizaciones/eur', 'label': 'Euro'},
                'real': {'activa': False, 'endpoint': '/v1/cotizaciones/brl', 'label': 'Real Brasileño'},
                'inflacion': {'activa': True, 'endpoint': '/v1/finanzas/inflacion', 'label': 'Inflación mensual'},
                'plazo_fijo': {'activa': False, 'endpoint': '/v1/finanzas/tasas/plazoFijo', 'label': 'Tasas de Plazo Fijo'},
                'plazos_fijos_entidades': {'activa': False, 'endpoint': '/v1/finanzas/tasas/plazosFijos', 'label': 'Tasas por entidad'},
                'depositos_30_dias': {'activa': False, 'endpoint': '/v1/finanzas/tasas/depositos30Dias', 'label': 'Depósitos a 30 días'},
                'indice_uva': {'activa': False, 'endpoint': '/v1/finanzas/indices/uva', 'label': 'Índice UVA'},
                'fci': {'activa': False, 'endpoint': '/v1/finanzas/fci', 'label': 'Fondos Comunes'},
                'riesgo_pais': {'activa': False, 'endpoint': '/v1/finanzas/indices/riesgo-pais/ultimo', 'label': 'Riesgo País'},
                'criptopesos': {'activa': False, 'endpoint': '/v1/finanzas/criptopesos', 'label': 'Criptopesos'},
                'cuentas_remuneradas_usd': {'activa': False, 'endpoint': '/v1/finanzas/cuentas-remuneradas-usd', 'label': 'Cuentas Remun. USD'},
                'hipotecarios_uva': {'activa': False, 'endpoint': '/v1/finanzas/hipotecarios-uva', 'label': 'Hipotecarios UVA'},
                'creditos_hipotecarios': {'activa': False, 'endpoint': '/v1/finanzas/creditos', 'label': 'Créditos Hipotecarios'}
            }
        }
        session.add(p)
        session.commit()
        print("Configuración de argentina_datos actualizada.")
    else:
        print("Plugin argentina_datos no encontrado.")
