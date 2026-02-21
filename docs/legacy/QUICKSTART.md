# FuturoForbes - Guía de Inicio Rápido

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
# Copiar template
cp .env.template .env

# Editar .env (opcional, funciona con SQLite por defecto)
```

### 3. Inicializar Base de Datos con Datos de Ejemplo

```bash
python init_data.py
```

Esto creará:
- ✅ 4 divisas (ARS, USD, EUR, BTC)
- ✅ 15 categorías (Comida, Transporte, Servicios, etc.)
- ✅ 10 beneficiarios
- ✅ 4 cuentas de ejemplo
- ✅ 4 transacciones de ejemplo

### 4. Iniciar Servidor

```bash
uvicorn main:app --reload
```

El servidor estará disponible en: **http://localhost:8000**

---

## 📚 Endpoints Disponibles

### Documentación
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### API Cuentas
- `GET /api/cuentas` - Listar todas las cuentas
- `POST /api/cuentas` - Crear nueva cuenta
- `GET /api/cuentas/{id}` - Obtener detalles de una cuenta
- `DELETE /api/cuentas/{id}` - Cerrar cuenta

### API Transacciones
- `GET /api/transacciones` - Listar transacciones
- `GET /api/transacciones?cuenta_id=1` - Filtrar por cuenta
- `POST /api/transacciones` - Crear transacción
- `GET /api/transacciones/{id}` - Obtener detalles
- `DELETE /api/transacciones/{id}` - Eliminar transacción

---

## 🧪 Probar la API

### Crear una cuenta nueva

```bash
curl -X POST "http://localhost:8000/api/cuentas/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_cuenta": "Mi Nueva Cuenta",
    "tipo_cuenta": "Ahorro",
    "id_divisa": 1,
    "saldo_inicial": 10000.0
  }'
```

### Listar todas las cuentas

```bash
curl http://localhost:8000/api/cuentas/
```

### Crear una transacción

```bash
curl -X POST "http://localhost:8000/api/transacciones/" \
  -H "Content-Type: application/json" \
  -d '{
    "id_cuenta": 1,
    "id_beneficiario": 1,
    "codigo_transaccion": "Withdrawal",
    "monto_transaccion": 500.0,
    "id_categoria": 1,
    "notas": "Compra de prueba"
  }'
```

### Listar transacciones

```bash
curl http://localhost:8000/api/transacciones/
```

---

## 📁 Estructura del Proyecto

```
backend/
├── api/                    # Endpoints de la API
│   ├── cuentas.py         # CRUD de cuentas
│   └── transacciones.py   # CRUD de transacciones
├── core/                   # Configuración
│   ├── config.py          # Settings
│   └── db.py              # Database
├── models/                 # Modelos SQLModel
│   └── finance.py         # Modelos principales
├── init_data.py           # Script de inicialización
├── main.py                # Aplicación FastAPI
└── requirements.txt       # Dependencias
```

---

## 🔧 Comandos Útiles

```bash
# Iniciar servidor en modo desarrollo
uvicorn main:app --reload

# Iniciar en puerto diferente
uvicorn main:app --reload --port 8080

# Ver logs detallados
uvicorn main:app --reload --log-level debug

# Reiniciar base de datos
rm futuroforbes.db
python init_data.py
```

---

## 📊 Datos de Ejemplo

Después de ejecutar `init_data.py`, tendrás:

### Cuentas
1. Cuenta Corriente Banco Nación (ARS $50,000)
2. Caja de Ahorro USD (USD $1,000)
3. Tarjeta Visa (ARS $0)
4. Efectivo (ARS $5,000)

### Categorías Principales
- 🍔 Comida (Supermercado, Restaurantes)
- 🚗 Transporte (Nafta, Transporte Público)
- 📄 Servicios (Electricidad, Internet)
- 🎬 Entretenimiento (Cine, Streaming)
- ❤️ Salud
- 💰 Ingresos (Salario)

---

## 🎯 Próximos Pasos

1. ✅ Backend API funcionando
2. 🔄 Crear frontend con AdminLTE4
3. 📊 Agregar dashboard con gráficos
4. 🔐 Implementar autenticación
5. 📈 Agregar reportes avanzados

---

## 🐛 Solución de Problemas

### Error: ModuleNotFoundError
```bash
# Asegúrate de estar en el directorio backend
cd backend
pip install -r requirements.txt
```

### Error: Database locked
```bash
# Cerrar todas las conexiones y reiniciar
rm futuroforbes.db
python init_data.py
```

### Puerto 8000 en uso
```bash
# Usar otro puerto
uvicorn main:app --reload --port 8080
```

---

## 📞 Soporte

Para más información, ver la documentación completa en `/docs`
