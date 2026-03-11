"""
Modelos de datos para el plugin CriptoYa Multi-País
Tablas independientes para almacenar datos de cotizaciones de criptomonedas
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON, DECIMAL
from decimal import Decimal


class CriptoYaConfig(SQLModel, table=True):
    """
    Configuración del plugin CriptoYa por usuario
    """
    __tablename__ = "criptoya_config"
    
    id_config: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="users.id", index=True)
    
    # Países habilitados para monitoreo
    paises_habilitados: List[str] = Field(default=[], sa_column=Column(JSON))
    
    # Criptomonedas a monitorear
    coins_monitoreadas: List[str] = Field(default=["BTC", "ETH", "USDT"], sa_column=Column(JSON))
    
    # Exchanges preferidos por país
    exchanges_preferidos: dict = Field(default={}, sa_column=Column(JSON))
    
    # Configuración de actualización
    auto_update: bool = Field(default=True)
    update_interval_minutes: int = Field(default=5)  # Mínimo 1 minuto (límite API: 120 req/min)
    
    # Volumen de referencia para cotizaciones
    volumen_default: Decimal = Field(default=Decimal("0.1"), max_digits=20, decimal_places=8)
    
    # Notificaciones
    notificar_cambio_significativo: bool = Field(default=False)
    umbral_cambio_porcentaje: Decimal = Field(default=Decimal("5.0"), max_digits=5, decimal_places=2)
    
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)
    activo: bool = Field(default=True)


class CriptoYaPais(SQLModel, table=True):
    """
    Catálogo de países soportados por CriptoYa
    """
    __tablename__ = "criptoya_paises"
    
    id_pais: Optional[int] = Field(default=None, primary_key=True)
    codigo_iso: str = Field(unique=True, index=True, max_length=3)  # AR, BR, CL, etc.
    nombre: str = Field(max_length=100)
    nombre_display: str = Field(max_length=100)
    moneda_local: str = Field(max_length=3)  # ARS, BRL, CLP, etc.
    
    # Configuración específica del país
    api_endpoint: str = Field(default="https://criptoya.com/api")
    
    # Flags de disponibilidad
    disponible: bool = Field(default=True)
    requiere_volumen: bool = Field(default=True)
    
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    exchanges: List["CriptoYaExchange"] = Relationship(back_populates="pais")
    rates: List["CriptoYaRate"] = Relationship(back_populates="pais")


class CriptoYaExchange(SQLModel, table=True):
    """
    Exchanges/casas de cambio disponibles por país
    """
    __tablename__ = "criptoya_exchanges"
    
    id_exchange: Optional[int] = Field(default=None, primary_key=True)
    id_pais: int = Field(foreign_key="criptoya_paises.id_pais", index=True)
    
    # Identificación del exchange
    slug: str = Field(max_length=50, index=True)  # cryptomkt, lemoncash, etc.
    nombre: str = Field(max_length=100)
    nombre_display: Optional[str] = Field(default=None, max_length=100)
    
    # Tipo de exchange
    tipo: str = Field(default="exchange", max_length=20)  # exchange, p2p, banco, etc.
    
    # URLs y contacto
    web_url: Optional[str] = Field(default=None, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=255)
    
    # Estado
    activo: bool = Field(default=True)
    requiere_verificacion: bool = Field(default=False)
    
    # Metadatos
    metodos_pago: List[str] = Field(default=[], sa_column=Column(JSON))
    criptos_soportadas: List[str] = Field(default=[], sa_column=Column(JSON))
    
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    pais: Optional["CriptoYaPais"] = Relationship(back_populates="exchanges")
    rates: List["CriptoYaRate"] = Relationship(back_populates="exchange")
    fees: List["CriptoYaFee"] = Relationship(back_populates="exchange")


class CriptoYaCoin(SQLModel, table=True):
    """
    Criptomonedas disponibles en CriptoYa
    """
    __tablename__ = "criptoya_coins"
    
    id_coin: Optional[int] = Field(default=None, primary_key=True)
    
    # Identificación
    symbol: str = Field(unique=True, index=True, max_length=10)  # BTC, ETH, USDT
    nombre: str = Field(max_length=100)
    nombre_completo: Optional[str] = Field(default=None, max_length=100)
    
    # Tipo
    tipo: str = Field(default="crypto", max_length=20)  # crypto, stablecoin, token
    
    # Información adicional
    red_principal: Optional[str] = Field(default=None, max_length=50)
    decimals: int = Field(default=8)
    
    # Estado
    activo: bool = Field(default=True)
    popular: bool = Field(default=False)
    
    # Metadatos
    redes_disponibles: List[str] = Field(default=[], sa_column=Column(JSON))
    
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    rates: List["CriptoYaRate"] = Relationship(back_populates="coin")
    fees: List["CriptoYaFee"] = Relationship(back_populates="coin")


class CriptoYaRate(SQLModel, table=True):
    """
    Tasas de cambio históricas obtenidas de CriptoYa
    """
    __tablename__ = "criptoya_rates"
    
    id_rate: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    id_pais: int = Field(foreign_key="criptoya_paises.id_pais", index=True)
    id_exchange: int = Field(foreign_key="criptoya_exchanges.id_exchange", index=True)
    id_coin: int = Field(foreign_key="criptoya_coins.id_coin", index=True)
    
    # Moneda fiat
    fiat: str = Field(max_length=3, index=True)  # ARS, BRL, CLP, etc.
    
    # Precios
    ask: Decimal = Field(max_digits=30, decimal_places=8)  # Precio de venta
    total_ask: Decimal = Field(max_digits=30, decimal_places=8)  # Total con comisiones
    bid: Decimal = Field(max_digits=30, decimal_places=8)  # Precio de compra
    total_bid: Decimal = Field(max_digits=30, decimal_places=8)  # Total con comisiones
    
    # Volumen de la cotización
    volumen: Decimal = Field(max_digits=20, decimal_places=8)
    
    # Spread
    spread: Decimal = Field(max_digits=10, decimal_places=4)  # Diferencia ask-bid
    spread_porcentaje: Decimal = Field(max_digits=6, decimal_places=2)
    
    # Timestamp de la cotización (de la API)
    timestamp_api: int  # Unix timestamp
    
    # Timestamp de registro
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    pais: Optional["CriptoYaPais"] = Relationship(back_populates="rates")
    exchange: Optional["CriptoYaExchange"] = Relationship(back_populates="rates")
    coin: Optional["CriptoYaCoin"] = Relationship(back_populates="rates")


class CriptoYaFee(SQLModel, table=True):
    """
    Comisiones de retiro por exchange y criptomoneda
    """
    __tablename__ = "criptoya_fees"
    
    id_fee: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    id_exchange: int = Field(foreign_key="criptoya_exchanges.id_exchange", index=True)
    id_coin: int = Field(foreign_key="criptoya_coins.id_coin", index=True)
    
    # Red de retiro
    red: str = Field(max_length=50, index=True)  # ERC20, BEP20, TRC20, etc.
    
    # Comisión
    comision: Decimal = Field(max_digits=20, decimal_places=8)
    comision_fiat: Optional[Decimal] = Field(default=None, max_digits=20, decimal_places=2)
    
    # Información adicional
    tiempo_confirmacion: Optional[str] = Field(default=None, max_length=50)
    requiere_memo: bool = Field(default=False)
    
    # Estado
    activo: bool = Field(default=True)
    
    # Timestamp
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    exchange: Optional["CriptoYaExchange"] = Relationship(back_populates="fees")
    coin: Optional["CriptoYaCoin"] = Relationship(back_populates="fees")


class CriptoYaAlerta(SQLModel, table=True):
    """
    Alertas de precio configuradas por usuario
    """
    __tablename__ = "criptoya_alertas"
    
    id_alerta: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="users.id", index=True)
    
    # Configuración de la alerta
    id_coin: int = Field(foreign_key="criptoya_coins.id_coin")
    id_pais: int = Field(foreign_key="criptoya_paises.id_pais")
    fiat: str = Field(max_length=3)
    
    # Tipo de alerta
    tipo: str = Field(max_length=20)  # mayor_que, menor_que, cambio_porcentaje
    
    # Valor objetivo
    valor_objetivo: Decimal = Field(max_digits=30, decimal_places=8)
    porcentaje_objetivo: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=2)
    
    # Estado
    activa: bool = Field(default=True)
    disparada: bool = Field(default=False)
    disparada_el: Optional[datetime] = Field(default=None)
    
    # Notificaciones
    notificar_email: bool = Field(default=True)
    notificar_telegram: bool = Field(default=False)
    
    # Referencia al precio base (para alertas de porcentaje)
    precio_base: Optional[Decimal] = Field(default=None, max_digits=30, decimal_places=8)
    
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    expira_el: Optional[datetime] = Field(default=None)


class CriptoYaFavorito(SQLModel, table=True):
    """
    Pares de trading favoritos del usuario
    """
    __tablename__ = "criptoya_favoritos"
    
    id_favorito: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="users.id", index=True)
    
    # Par favorito
    id_coin: int = Field(foreign_key="criptoya_coins.id_coin")
    id_pais: int = Field(foreign_key="criptoya_paises.id_pais")
    fiat: str = Field(max_length=3)
    id_exchange_preferido: Optional[int] = Field(default=None, foreign_key="criptoya_exchanges.id_exchange")
    
    # Orden en la UI
    orden: int = Field(default=0)
    
    creado_el: datetime = Field(default_factory=datetime.utcnow)
