# Spec Delta: Core Financiero

## Data Models

**Nuevos Campos Requeridos**

Para poder alimentar el algoritmo de nombrado de la Bóveda, las identidades de cuentas y beneficiarios deben pre-cargar un campo `code` al ser instanciadas.

### Account (Actualización)
```diff
 class Account(SQLModel, table=True):
     id: int = Field(default=None, primary_key=True)
     user_id: int = Field(foreign_key="user.id")
+    code: str = Field(unique=True, index=True) # Código corto identificador. Ej: "SANT01", "CASH"
     account_type: str
     currency_code: str = Field(foreign_key="currency.code")
```

### Beneficiary (Actualización)
```diff
 class Beneficiary(SQLModel, table=True):
     id: int = Field(default=None, primary_key=True)
     user_id: int = Field(foreign_key="user.id")
+    code: str = Field(unique=True, index=True) # Código corto. Ej: "EDENO", "FIBER"
     name: str
```

## API Endpoints

Las interfaces `POST /accounts` y `POST /beneficiaries` deben hacer de `code` un campo REQUIRED en su esquema Pydantic para garantizar que la bóveda siempre cuente con este input al momento de un adjunto.
